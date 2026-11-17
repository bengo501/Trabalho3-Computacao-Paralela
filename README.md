# Trabalho 3: divisão e conquista com MPI

Ordenação de um vetor em ordem decrescente, com Bubble Sort nas folhas e intercalação na subida da árvore. Duas versões paralelas (árvore original e árvore balanceada) e as referências sequenciais pedidas pelo enunciado.

- Disciplina: Computação Paralela e Distribuída (PUCRS)
- Autor: Bernardo Klein Heitz
- Repositório: https://github.com/bengo501/Trabalho3-Computacao-Paralela
- Cluster: Atlântica (LAD), nós `atlantica03` e `atlantica04`, `--exclusive`

## Problema e algoritmo

O processo raiz gera o vetor `n, n-1, ..., 1`. Se o pedaço passa de `delta`, o rank `r` envia a metade esquerda ao filho `2r+1` e a direita ao filho `2r+2`. A folha ordena com Bubble Sort. O pai intercala na volta. Com `P = 2^k - 1`, `delta = ceil(2n/(P+1))` enche a árvore.

A versão balanceada, derivada de `mpi_mergesort.c` de Atanas Radenski (PDPTA 2011, GPL-2.0), manda só a metade direita ao ajudante `rank + 2^nível` e fica com a esquerda. A folha continua sendo Bubble Sort no vetor decrescente.

## Estrutura

```
src/           arvore.c, balanceada.c, sequencial.c, comum.c, comum.h, confere.c
scripts/       campanha.sbatch, campanha_over.sbatch, campanha_*.sbatch, resumir.py
results/       runs.csv (campanha oficial), medio/, longo/, yield-explicito/, lscpu.txt
relatorio/     relatorio.pdf e geradores
apresentacao/  apresentacao.pptx e gerador
```

## Compilação

No cluster (Open MPI 4.1.1):

```bash
export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
export LD_LIBRARY_PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/lib:$LD_LIBRARY_PATH
make clean && make
```

Flags: `-O2 -std=c11 -Wall -Wextra` nos três binários. O sequencial liga `-lrt` por causa de `clock_gettime`.

## Programas

### `bin/sequencial` (sem MPI)

- `./sequencial n` — Bubble Sort do vetor inteiro (T1)
- `./sequencial n delta` — mesma árvore original em um processo (T1delta)
- `./sequencial n balanceada p` — mesma árvore de ajudantes em um processo (T1bal)

### `bin/arvore`

- `./arvore n delta` ou `./arvore n niveis K`
- SPMD; o papel sai do rank
- Imprime `verificacao=OK` ou `ERRO` e o tempo da raiz com `MPI_Wtime` (inicialização fora)

### `bin/balanceada`

- `./balanceada n`
- Mesma região de tempo e mesma verificação

### `bin/confere`

Checagens locais da figura, da fórmula do delta e da cobertura da árvore balanceada: `make teste`.

## Campanha no cluster

Sempre nos mesmos dois nós, `--exclusive`, distribuição `block`. Acima de 32 processos: `srun -O`. A série de 63 a 1023 roda com `OMPI_MCA_mpi_yield_when_idle=0` e `=1`, os dois escritos na variável.

```bash
# campanha oficial (T1 entre 30 e 60 s): N=212064
id=$(sbatch --parsable --export=ALL,N=212064,RODA_OVER=1 scripts/campanha.sbatch)
```

Ou as campanhas longas:

```bash
sbatch scripts/campanha_medio.sbatch   # N=345037
sbatch scripts/campanha_longo.sbatch   # N=545552
```

Os tempos brutos ficam em `results/runs.csv` (e `results/medio`, `results/longo`). Resumo:

```bash
python3 scripts/resumir.py results/runs.csv
```

## Métricas

- `S = T1 / Tp` (pode passar de P; inclui ganho de algoritmo)
- `Sdelta = T1delta / Tp` (só paralelismo)
- `E = Sdelta / P`; de 63 a 1023, `E = Sdelta / 32`
- Razão `T1 / T1delta`: ganho de algoritmo

## Resultados oficiais (n = 212064, T1 = 45,330 s)

Árvore original (mediana de 10 repetições, `verificacao=OK` em todas):

| P | Tp (s) | S | Sdelta | E |
|---|--------|---|--------|---|
| 1 | 45,296 | 1,00 | 1,00 | 1,00 |
| 3 | 11,288 | 4,02 | 2,00 | 0,67 |
| 7 | 2,850 | 15,91 | 3,92 | 0,56 |
| 15 | 0,770 | 58,86 | 7,17 | 0,48 |
| 31 | 0,354 | 128,16 | 7,61 | 0,25 |

Na série de 63 a 1023, ceder o núcleo (`yield=1`) encurtou todas as linhas frente a `yield=0`. Em P = 1023, a espera ativa ficou em 3,067 s e o yield em 0,221 s.

## Limitações

- Open MPI 4.1.1 sem thread de progresso: em P = 2 na versão balanceada, o `MPI_Isend` não anda durante o Bubble Sort da folha esquerda; Sdelta fica em 1,00.
- Acima de 32 processos, a eficiência usa as 32 threads de hardware, não P.
- A distribuição `block` concentra folhas nos ranks altos; em P = 31 a análise da “segunda leva” é inferida dessa distribuição e dos tempos.

## Relatório e slides

```bash
python relatorio/montar_pdf.py
python apresentacao/montar.py
```

Os números saem de `relatorio/dados.py`, lendo `results/runs.csv`.
