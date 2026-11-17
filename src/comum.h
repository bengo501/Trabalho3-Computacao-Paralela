#ifndef COMUM_H
#define COMUM_H

/* Rotinas do sequencial.c e a numeração da árvore da figura 1.
 * O rank 0 é a raiz. O filho da esquerda é 2*rank+1 e o da direita
 * é 2*rank+2. O pai de um rank é (rank-1)/2. Com 7 processos a figura
 * fica p0 -> p1, p2; p1 -> p3, p4; p2 -> p5, p6. */

void bubble_sort(int *v, int n);
void intercala(int *v, int n, int *aux);
void ordena(int *v, int n, int delta, int *aux);
void ordena_balanceada(int *v, int n, int *aux, int nivel, int rank, int max_rank);
void inicializa(int *v, int n);
long long verifica(const int *v, int n);

/* ceil(2n / (processos + 1)), o delta do enunciado para P = 2^k - 1. */
int delta_da_arvore(int n, int processos);

/* O processo divide quando o pedaço passa de delta e os dois filhos
 * existem nesta execução. */
int divide(int n, int delta, int rank, int processos);

/* 1 se a decisão de dividir entrega exatamente uma mensagem a cada
 * rank de 1 até processos-1. 0 deixa alguém preso no Probe. */
int arvore_ocupa_todos(int n, int delta, int rank, int processos);

/* 2^nivel, ou -1 se o deslocamento não cabe num int. */
int potencia_de_dois(int nivel);

/* Menor nível em que 2^nível > rank. A raiz fica no nível 0. */
int nivel_inicial(int rank);

/* rank + 2^nivel, ou max_rank+1 quando esse ajudante não existe. */
int ajudante_de(int rank, int nivel, int max_rank);

static inline int filho_esquerdo(int rank) { return 2 * rank + 1; }
static inline int filho_direito(int rank) { return 2 * rank + 2; }
static inline int pai_de(int rank) { return (rank - 1) / 2; }

#endif
