

Este repositório contém a implementação prática, desenvolvido para a disciplina de **Sistemas Operacionais**.

O objetivo do projeto é demonstrar conceitos fundamentais do sistema operacional na prática, como **criação e orquestração de processos**, **concorrência através de threads**, **exclusão mútua** para prevenção de condições de corrida e **análise de ganho de desempenho ** em cargas limitadas por E/S .

---

##  Estrutura do Repositório

-  **`p0.py`**
  - Arquivo responsável pelo ponto de entrada e orquestração dos testes.
  - Cria o processo `p1.py` utilizando `subprocess.Popen()`.
  - Executa 6 simulações (combinações das listas Pequena, Média e Grande com 1 e 4 threads).
  - Mede o tempo total de execução, monitora os códigos de retorno do SO e faz a auditoria final comparando o número de linhas do log gerado com a quantidade de IDs de entrada.

-  **`p1.py`**
  - Script responsável por realizar o processamento dos IDs da lista de entrada.
  - Cria as threads para dividir o trabalho entre $N$ threads.
  - Utiliza dois locks independentes para garantir a integridade dos dados
  - Simula chamadas de API com tempo de espera/E/S.


-  **`listas/`**
  - Contém as listas de IDs em texto plano utilizadas nos testes:
    - `lista_ids_pequena.txt`: 20 IDs.
    - `lista_ids_media.txt`: 200 IDs.
    - `lista_ids_grande.txt`: 2000 IDs.

-  **Logs de Saída**
  - Arquivos contendo os registros do processamento gerados em cada uma das 6 execuções de teste.

### Pré-requisitos
- Python 3.10 ou superior instalado.


```bash
python p0.py
