/* Versão balanceada, derivada de mpi_mergesort.c de Atanas Radenski
 * (PDPTA 2011, licença GPL-2.0). O repositório de origem é o que o
 * professor publicou em parallel-merge-sort-master.
 *
 * Três trocas pedidas pelo enunciado, em relação a esse código:
 * a folha usa bubble_sort, o vetor começa em ordem decrescente, e o
 * tempo é MPI_Wtime na mesma região da versão original.
 *
 * Ao dividir, o processo manda a metade direita para um ajudante e
 * fica com a esquerda. Os processos internos também conquistam. */

#include "comum.h"

#include <stdio.h>
#include <stdlib.h>
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

/* Ordena v[0, n). A metade direita vai para o ajudante rank + 2^nivel.
 * A esquerda continua neste processo, no nível seguinte. */
static void ordena_mpi(int *v, int n, int *aux, int nivel, int rank, int max_rank)
{
    int ajudante = ajudante_de(rank, nivel, max_rank);
    if (ajudante > max_rank) {
        bubble_sort(v, n);
        return;
    }

    int meio = n / 2;
    MPI_Request pedido;
    MPI_Status status;

    /* Isend devolve a direita e segue. Este processo ordena a esquerda
     * enquanto a mensagem caminha, e não escreve na direita nesse meio
     * tempo. Request_free solta o handle; o envio termina sozinho.
     * O Recv abaixo escreve na mesma direita. Isso é seguro porque a
     * resposta só é enviada depois que o ajudante recebeu o pedaço:
     * quando este Recv termina, o Isend já terminou. */
    MPI_Isend(v + meio, n - meio, MPI_INT, ajudante, TAG, MPI_COMM_WORLD, &pedido);
    ordena_mpi(v, meio, aux, nivel + 1, rank, max_rank);
    MPI_Request_free(&pedido);
    MPI_Recv(v + meio, n - meio, MPI_INT, ajudante, TAG, MPI_COMM_WORLD, &status);
    if (status.MPI_SOURCE != ajudante)
        falha(rank, "resposta veio de outro processo");
    intercala(v, n, aux);
}

static void executa_ajudante(int rank, int max_rank)
{
    /* Quem manda para este rank é o processo que o escolheu como
     * ajudante. O Probe com ANY_SOURCE descobre esse pai e o tamanho. */
    MPI_Status status;
    int tam_vetor;
    MPI_Probe(MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &status);
    MPI_Get_count(&status, MPI_INT, &tam_vetor);
    int pai = status.MPI_SOURCE;

    int *vetor = aloca(tam_vetor, rank);
    int *aux = aloca(tam_vetor, rank);
    MPI_Recv(vetor, tam_vetor, MPI_INT, pai, TAG, MPI_COMM_WORLD, &status);

    /* O nível não vem na mensagem. rank + 2^nivel cai em
     * [2^nivel, 2^(nivel+1)), então o nível inicial do ajudante é
     * nivel+1 do processo que o chamou. */
    int nivel = nivel_inicial(rank);
    ordena_mpi(vetor, tam_vetor, aux, nivel, rank, max_rank);
    MPI_Send(vetor, tam_vetor, MPI_INT, pai, TAG, MPI_COMM_WORLD);
    free(vetor);
    free(aux);
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);

    int my_rank, processos;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &processos);
    int max_rank = processos - 1;

    if (argc != 2) {
        if (my_rank == 0)
            fprintf(stderr, "uso: %s n\n", argv[0]);
        falha(my_rank, "argumentos invalidos");
    }
    int n = atoi(argv[1]);
    if (n < 1) {
        if (my_rank == 0)
            fprintf(stderr, "uso: %s n\n", argv[0]);
        falha(my_rank, "n deve ser positivo");
    }

    if (my_rank == 0) {
        int *vetor = aloca(n, my_rank);
        int *aux = aloca(n, my_rank);
        inicializa(vetor, n);

        double t0 = MPI_Wtime();
        ordena_mpi(vetor, n, aux, 0, my_rank, max_rank);
        double t1 = MPI_Wtime();

        long long erros = verifica(vetor, n);
        printf("resultado versao=balanceada n=%d p=%d tempo=%.6f verificacao=%s\n",
               n, processos, t1 - t0, erros == 0 ? "OK" : "ERRO");
        fflush(stdout);
        free(vetor);
        free(aux);
        if (erros)
            falha(my_rank, "vetor final diferente de 1..n");
    } else {
        executa_ajudante(my_rank, max_rank);
    }

    MPI_Finalize();
    return 0;
}
