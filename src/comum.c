#include "comum.h"

#include <stdlib.h>
#include <string.h>

void bubble_sort(int *v, int n)
{
    int trocou = 1;
    for (int fim = n - 1; fim > 0 && trocou; fim--) {
        trocou = 0;
        for (int i = 0; i < fim; i++) {
            if (v[i] > v[i + 1]) {
                int t = v[i];
                v[i] = v[i + 1];
                v[i + 1] = t;
                trocou = 1;
            }
        }
    }
}

void intercala(int *v, int n, int *aux)
{
    int meio = n / 2;
    int i = 0, j = meio, k = 0;

    while (i < meio && j < n)
        aux[k++] = (v[i] <= v[j]) ? v[i++] : v[j++];
    while (i < meio)
        aux[k++] = v[i++];
    while (j < n)
        aux[k++] = v[j++];

    memcpy(v, aux, (size_t)n * sizeof(int));
}

void ordena(int *v, int n, int delta, int *aux)
{
    if (n <= delta) {
        bubble_sort(v, n);
        return;
    }
    int meio = n / 2;
    ordena(v, meio, delta, aux);
    ordena(v + meio, n - meio, delta, aux + meio);
    intercala(v, n, aux);
}

void ordena_balanceada(int *v, int n, int *aux, int nivel, int rank, int max_rank)
{
    int ajudante = ajudante_de(rank, nivel, max_rank);
    if (ajudante > max_rank) {
        bubble_sort(v, n);
        return;
    }
    int meio = n / 2;
    ordena_balanceada(v, meio, aux, nivel + 1, rank, max_rank);
    ordena_balanceada(v + meio, n - meio, aux, nivel + 1, ajudante, max_rank);
    intercala(v, n, aux);
}

void inicializa(int *v, int n)
{
    for (int i = 0; i < n; i++)
        v[i] = n - i;
}

long long verifica(const int *v, int n)
{
    long long erros = 0;
    for (int i = 0; i < n; i++)
        if (v[i] != i + 1)
            erros++;
    return erros;
}

int delta_da_arvore(int n, int processos)
{
    return (int)((2LL * n + processos) / (processos + 1));
}

int divide(int n, int delta, int rank, int processos)
{
    return n > delta && filho_direito(rank) < processos;
}

int arvore_ocupa_todos(int n, int delta, int rank, int processos)
{
    if (!divide(n, delta, rank, processos))
        return filho_direito(rank) >= processos;
    int meio = n / 2;
    return arvore_ocupa_todos(meio, delta, filho_esquerdo(rank), processos)
        && arvore_ocupa_todos(n - meio, delta, filho_direito(rank), processos);
}

int potencia_de_dois(int nivel)
{
    if (nivel < 0 || nivel >= 30)
        return -1;
    return 1 << nivel;
}

int nivel_inicial(int rank)
{
    int nivel = 0;
    while (nivel < 30 && potencia_de_dois(nivel) <= rank)
        nivel++;
    return nivel;
}

int ajudante_de(int rank, int nivel, int max_rank)
{
    int salto = potencia_de_dois(nivel);
    if (salto < 0 || salto > max_rank - rank)
        return max_rank + 1;
    return rank + salto;
}
