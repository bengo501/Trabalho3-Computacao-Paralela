/* Versão original da seção 3 e do anexo do enunciado.
 * Um executável só. Cada rank é um nó da árvore da figura 1.
 * A folha ordena com bubble_sort. O pai intercala as duas metades.
 * O tempo da raiz vai do início da distribuição até o vetor inteiro
 * estar ordenado. A inicialização fica de fora. */

#include "comum.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define TAG 1

static void falha(int rank, const char *msg)
{
    fprintf(stderr, "rank %d: %s\n", rank, msg);
    fflush(stderr);
    MPI_Abort(MPI_COMM_WORLD, 1);
}

static int *aloca(int n, int rank)
{
    int slots = n > 0 ? n : 1;
    int *p = malloc((size_t)slots * sizeof(int));
    if (!p)
        falha(rank, "sem memoria");
    return p;
}

static void uso(const char *nome)
{
    fprintf(stderr,
            "uso: %s n delta\n"
            "     %s n niveis K\n"
            "delta = ceil(2n/(P+1)) ocupa a arvore de P = 2^k-1 processos.\n"
            "K niveis de divisao pedem P = 2^(K+1)-1 processos.\n",
            nome, nome);
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);

    int my_rank, processos;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &processos);

    int n = 0, delta = 0;
    if (argc == 3) {
        n = atoi(argv[1]);
        delta = atoi(argv[2]);
    } else if (argc == 4 && strcmp(argv[2], "niveis") == 0) {
        n = atoi(argv[1]);
        int niveis = atoi(argv[3]);
        if (niveis < 0 || niveis >= 20) {
            if (my_rank == 0)
                uso(argv[0]);
            falha(my_rank, "numero de niveis invalido");
        }
        delta = (int)((n + (1LL << niveis) - 1) >> niveis);
        int esperado = (1 << (niveis + 1)) - 1;
        if (processos != esperado) {
            if (my_rank == 0)
                fprintf(stderr, "niveis %d pedem %d processos, nao %d\n",
                        niveis, esperado, processos);
            falha(my_rank, "quantidade de processos nao fecha a arvore");
        }
    } else {
        if (my_rank == 0)
            uso(argv[0]);
        falha(my_rank, "argumentos invalidos");
    }
    if (n < 1 || delta < 1) {
        if (my_rank == 0)
            uso(argv[0]);
        falha(my_rank, "n e delta devem ser positivos");
    }

    if (my_rank == 0 && !arvore_ocupa_todos(n, delta, 0, processos)) {
        int oficial = delta_da_arvore(n, processos);
        fprintf(stderr,
                "arvore: n=%d p=%d delta=%d nao ocupa todos os processos.\n",
                n, processos, delta);
        if (oficial != delta && arvore_ocupa_todos(n, oficial, 0, processos))
            fprintf(stderr, "o delta do enunciado para este p e %d.\n", oficial);
        else
            fprintf(stderr,
                    "mesmo o delta do enunciado (%d) corta a arvore antes "
                    "de um processo. use um n maior para este p.\n",
                    oficial);
        falha(my_rank, "arvore incompleta");
    }

    int tam_vetor;
    int *vetor;
    int *aux;

    if (my_rank != 0) {
        /* O filho não sabe o tamanho antes da mensagem. O Probe espera
         * o pai, e o Get_count diz quantos inteiros alocar. */
        int pai = pai_de(my_rank);
        MPI_Status status;
        MPI_Probe(pai, TAG, MPI_COMM_WORLD, &status);
        MPI_Get_count(&status, MPI_INT, &tam_vetor);
        vetor = aloca(tam_vetor, my_rank);
        aux = aloca(tam_vetor, my_rank);
        MPI_Recv(vetor, tam_vetor, MPI_INT, pai, TAG, MPI_COMM_WORLD, &status);
    } else {
        tam_vetor = n;
        vetor = aloca(tam_vetor, my_rank);
        aux = aloca(tam_vetor, my_rank);
        inicializa(vetor, tam_vetor);
    }

    double t0 = 0.0;
    if (my_rank == 0)
        t0 = MPI_Wtime();

    if (!divide(tam_vetor, delta, my_rank, processos)) {
        /* Folha, ou pedaço que já cabe em delta. ordena no mesmo
         * processo reproduz o que o sequencial faria neste pedaço. */
        ordena(vetor, tam_vetor, delta, aux);
    } else {
        /* As duas metades saem antes de qualquer espera pelo resultado,
         * para os dois filhos trabalharem ao mesmo tempo. A direita leva
         * o resto, e nenhum elemento se perde quando o tamanho é ímpar. */
        int meio = tam_vetor / 2;
        int esq = filho_esquerdo(my_rank);
        int dir = filho_direito(my_rank);
        MPI_Send(vetor, meio, MPI_INT, esq, TAG, MPI_COMM_WORLD);
        MPI_Send(vetor + meio, tam_vetor - meio, MPI_INT, dir, TAG, MPI_COMM_WORLD);
        MPI_Recv(vetor, meio, MPI_INT, esq, TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(vetor + meio, tam_vetor - meio, MPI_INT, dir, TAG, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
        intercala(vetor, tam_vetor, aux);
    }

    if (my_rank != 0) {
        MPI_Send(vetor, tam_vetor, MPI_INT, pai_de(my_rank), TAG, MPI_COMM_WORLD);
    } else {
        double t1 = MPI_Wtime();
        long long erros = verifica(vetor, tam_vetor);
        printf("resultado versao=arvore n=%d delta=%d p=%d tempo=%.6f verificacao=%s\n",
               n, delta, processos, t1 - t0, erros == 0 ? "OK" : "ERRO");
        fflush(stdout);
        free(vetor);
        free(aux);
        if (erros)
            falha(my_rank, "vetor final diferente de 1..n");
        MPI_Finalize();
        return 0;
    }

    free(vetor);
    free(aux);
    MPI_Finalize();
    return 0;
}
