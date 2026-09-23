"""
P0 - Processo pai.

Cria o processo P1 e executando-o repetidas vezes sobre diferentes
listas de IDs e com diferentes
quantidades de threads. Para cada execucao.
"""

import os
import sys
import json
import time
import signal
import subprocess

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ = os.path.dirname(DIR_BASE)
P1_SCRIPT = os.path.join(DIR_BASE, "p1.py")

DIR_LISTAS = os.path.join(DIR_RAIZ, "listas")
DIR_LOGS = os.path.join(DIR_RAIZ, "logs")
DIR_STATS = os.path.join(DIR_RAIZ, "stats")

os.makedirs(DIR_LOGS, exist_ok=True)
os.makedirs(DIR_STATS, exist_ok=True)

CONF = [
    ("pequena", os.path.join(DIR_LISTAS, "lista_ids_pequena.txt"), 1),
    ("pequena", os.path.join(DIR_LISTAS, "lista_ids_pequena.txt"), 4),
    ("media",   os.path.join(DIR_LISTAS, "lista_ids_media.txt"),   1),
    ("media",   os.path.join(DIR_LISTAS, "lista_ids_media.txt"),   4),
    ("grande",  os.path.join(DIR_LISTAS, "lista_ids_grande.txt"),  1),
    ("grande",  os.path.join(DIR_LISTAS, "lista_ids_grande.txt"),  4),
]


def contar_ids(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return len([l for l in f if l.strip()])


def contar_linhas_log(caminho):
    if not os.path.exists(caminho):
        return 0
    with open(caminho, "r", encoding="utf-8") as f:
        return len([l for l in f if l.strip()])


def classificar_termino(returncode):
    if returncode == 0:
        return "termino normal (sucesso)", returncode

    if returncode < 0 and os.name != "nt":
        sinal = -returncode
        try:
            nome_sinal = signal.Signals(sinal).name
        except ValueError:
            nome_sinal = str(sinal)
        return f"terminado por sinal ({nome_sinal})", None

    return f"termino normal com erro (exit={returncode})", returncode


def executar_p1(lista_path, n_threads, log_path, stats_path):
    inicio_wall = time.time()
    proc = subprocess.Popen(
        [sys.executable, P1_SCRIPT, lista_path, str(n_threads), log_path, stats_path]
    )
    returncode = proc.wait()
    tempo_wall = time.time() - inicio_wall
    return returncode, tempo_wall


def main():
    resultados = []

    for nome_lista, lista_path, n_threads in CONF:
        if not os.path.isfile(lista_path):
            print(f"[P0] AVISO: lista '{lista_path}' nao encontrada, pulando.")
            continue

        log_path = os.path.join(DIR_LOGS, f"log_{nome_lista}_{n_threads}threads.txt")
        stats_path = os.path.join(DIR_STATS, f"stats_{nome_lista}_{n_threads}threads.json")

        total_ids = contar_ids(lista_path)
        print(f"\n[P0] Executando P1 | lista={nome_lista} ({total_ids} IDs) | N={n_threads} thread(s)...")

        status, tempo_wall = executar_p1(lista_path, n_threads, log_path, stats_path)
        descricao_status, exit_code = classificar_termino(status)

        linhas_log = contar_linhas_log(log_path)
        enriquecimento_completo = (linhas_log == total_ids)

        tempo_p1 = None
        if os.path.exists(stats_path):
            with open(stats_path, "r", encoding="utf-8") as f:
                tempo_p1 = json.load(f).get("tempo_total_segundos")

        situacao = descricao_status
        if exit_code == 0 and not enriquecimento_completo:
            situacao += " -- ENRIQUECIMENTO INCOMPLETO"

        resultados.append({
            "lista": nome_lista,
            "total_ids": total_ids,
            "n_threads": n_threads,
            "tempo_wall_p0_s": round(tempo_wall, 4),
            "tempo_interno_p1_s": tempo_p1,
            "linhas_log": linhas_log,
            "status": situacao,
        })

        print(
            f"[P0] pid filho finalizado -> {descricao_status} | "
            f"tempo(P0)={tempo_wall:.4f}s | tempo(P1)={tempo_p1}s | "
            f"log={linhas_log}/{total_ids} linhas"
        )

    # ---- relatorio consolidado ----
    print("\n" + "=" * 90)
    print("RELATORIO CONSOLIDADO")
    print("=" * 90)
    print(f"{'Lista':<10}{'IDs':<8}{'N threads':<12}{'Tempo P1 (s)'}")
    print("-" * 60)
    for r in resultados:
        print(
            f"{r['lista']:<10}{r['total_ids']:<8}{r['n_threads']:<12}"
            f"{str(r['tempo_interno_p1_s'])}"
        )

    caminho_relatorio = os.path.join(DIR_STATS, "relatorio_consolidado.json")
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"\n[P0] Relatorio salvo em {caminho_relatorio}")


if __name__ == "__main__":
    main()
