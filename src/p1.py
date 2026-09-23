#!/usr/bin/env python3
"""
P1 - Processo filho / trabalhador.

Le uma lista de IDs de um arquivo texto, distribui os IDs entre N threads
de trabalho usando exclusao mutua, consulta uma API mockada para cada
ID e grava o resultado em um arquivo de log, protegendo a escrita
concorrente com outro mutex.

Codigos de saida:
    0 -> sucesso: todos os IDs foram processados e logados sem erro
    1 -> erro de argumentos ou arquivo de lista de entrada nao encontrado
    2 -> erro durante o processamento (uma ou mais threads levantaram excecao)
"""

import sys
import os
import json
import time
import random
import threading
from datetime import datetime


def mock_api(id_):
    time.sleep(random.uniform(0.002, 0.015))
    valor = round(random.uniform(1, 1000), 2)
    return {"id": id_, "status": "ok", "valor": valor}


class Enriquecedor:

    def __init__(self, ids, n_threads, log_path):
        self.ids = ids
        self.n_threads = n_threads
        self.log_path = log_path
        self.indice_lock = threading.Lock()   # mutex: distribuicao dos IDs
        self.log_lock = threading.Lock()      # mutex: escrita no log
        self.proximo_indice = 0
        self.erros = []

    def _proximo_id(self):
        """Secao critica: devolve um indice nunca repetido, ou None se acabou."""
        with self.indice_lock:
            idx = self.proximo_indice
            if idx >= len(self.ids):
                return None
            self.proximo_indice += 1
            return idx

    def _log(self, thread_nome, id_processado, resposta_json):
        linha = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, "
            f"{thread_nome}, {id_processado}, {json.dumps(resposta_json)}\n"
        )
        with self.log_lock:  # secao critica: escrita no arquivo compartilhado
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(linha)

    def _worker(self, thread_nome):
        try:
            while True:
                idx = self._proximo_id()
                if idx is None:
                    break
                id_atual = self.ids[idx]
                resposta = mock_api(id_atual)
                self._log(thread_nome, id_atual, resposta)
        except Exception as e:
            self.erros.append(f"{thread_nome}: {e}")

    def executar(self):
        threads = []
        for i in range(self.n_threads):
            nome = f"Thread-{i + 1}"
            t = threading.Thread(target=self._worker, name=nome, args=(nome,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return len(self.erros) == 0


def main():
    if len(sys.argv) != 5:
        print(
            "Uso: python3 p1.py <lista_ids.txt> <N_threads> <log.txt> <stats.json>",
            file=sys.stderr,
        )
        sys.exit(1)

    lista_path, n_threads_str, log_path, stats_path = sys.argv[1:5]

    try:
        n_threads = int(n_threads_str)
        if n_threads < 1:
            raise ValueError
    except ValueError:
        print("N_threads deve ser um inteiro >= 1", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(lista_path):
        print(f"Arquivo de lista nao encontrado: {lista_path}", file=sys.stderr)
        sys.exit(1)

    # remove log de execucao anterior para nao acumular linhas entre testes
    if os.path.exists(log_path):
        os.remove(log_path)

    inicio = time.time()

    with open(lista_path, "r", encoding="utf-8") as f:
        ids = [linha.strip() for linha in f if linha.strip()]

    enriquecedor = Enriquecedor(ids, n_threads, log_path)
    sucesso = enriquecedor.executar()

    fim = time.time()
    tempo_total = fim - inicio

    stats = {
        "n_threads": n_threads,
        "total_ids": len(ids),
        "tempo_total_segundos": round(tempo_total, 4),
        "erros": enriquecedor.erros,
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(
        f"[P1 pid={os.getpid()}] {len(ids)} IDs processados por "
        f"{n_threads} thread(s) em {tempo_total:.4f}s"
    )

    if not sucesso:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
