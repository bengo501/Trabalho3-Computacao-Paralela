/* T3: as duas referências sequenciais, mais a árvore da versão balanceada.
 *
 *   ./sequencial n                  Bubble Sort do vetor inteiro (T1)
 *   ./sequencial n delta            a árvore original num processo só (T1 com delta)
 *   ./sequencial n balanceada p     a mesma árvore da versão balanceada com p processos
 *
 * A terceira forma existe porque, na versão balanceada, um delta único
 * não reproduz os pedaços das folhas. O processo percorre os mesmos
 * ajudantes (rank + 2^nivel) e ordena a folha com Bubble Sort.
 *
 * Compilação: gcc -O2 -std=c11 -o sequencial sequencial.c comum.c -lrt
 * -std=c11 esconde clock_gettime no gcc da Atlântica.
 */
#define _POSIX_C_SOURCE 199309L
#include "comum.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double agora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

static void uso(const char *nome)
{
    fprintf(stderr,
            "uso: %s n\n"
            "     %s n delta\n"
            "     %s n balanceada p\n",
            nome, nome, nome);
}

int main(int argc, char **argv)
{
    int balanceada = 0;
    int n, delta = 0, p = 1;

    if (argc == 2) {
        n = atoi(argv[1]);
        delta = n;
    } else if (argc == 3) {
        n = atoi(argv[1]);
        delta = atoi(argv[2]);
    } else if (argc == 4 && strcmp(argv[2], "balanceada") == 0) {
        n = atoi(argv[1]);
        p = atoi(argv[3]);
        balanceada = 1;
    } else {
        uso(argv[0]);
        return 1;
    }
    if (n < 1 || p < 1 || (!balanceada && delta < 1)) {
        fprintf(stderr, "n, delta e p devem ser positivos\n");
        return 1;
    }

    int *v = malloc((size_t)n * sizeof(int));
    int *aux = malloc((size_t)n * sizeof(int));
    if (!v || !aux) {
        fprintf(stderr, "sem memoria para n = %d\n", n);
        return 1;
    }

    inicializa(v, n);

    double t0 = agora();
    if (balanceada)
        ordena_balanceada(v, n, aux, 0, 0, p - 1);
    else
        ordena(v, n, delta, aux);
    double t1 = agora();

    long long erros = verifica(v, n);
    if (balanceada)
        printf("n=%d arvore=balanceada p=%d tempo=%.6f verificacao=%s\n",
               n, p, t1 - t0, erros == 0 ? "OK" : "ERRO");
    else
        printf("n=%d delta=%d tempo=%.6f verificacao=%s\n",
               n, delta, t1 - t0, erros == 0 ? "OK" : "ERRO");

    free(v);
    free(aux);
    return erros != 0;
}
