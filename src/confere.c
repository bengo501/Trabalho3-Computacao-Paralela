/* Confere a árvore da figura, a fórmula do delta e a cobertura dos ranks
 * sem precisar do MPI. A ordenação em si roda nas rotinas do sequencial. */
#include "comum.h"

#include <stdio.h>
#include <stdlib.h>

static int falhas = 0;

static void espera(int cond, const char *msg)
{
    if (!cond) {
        fprintf(stderr, "falha: %s\n", msg);
        falhas++;
    }
}

static int ordenou(int n, int balanceada, int delta, int p)
{
    int *v = malloc((size_t)n * sizeof(int));
    int *aux = malloc((size_t)n * sizeof(int));
    if (!v || !aux)
        return 0;
    inicializa(v, n);
    if (balanceada)
        ordena_balanceada(v, n, aux, 0, 0, p - 1);
    else
        ordena(v, n, delta, aux);
    int ok = verifica(v, n) == 0;
    free(v);
    free(aux);
    return ok;
}

static void folhas_originais(int rank, int n, int delta, int p, int inicio,
                             int *ranks, int *inicios, int *tamanhos, int *qtd)
{
    if (!divide(n, delta, rank, p)) {
        ranks[*qtd] = rank;
        inicios[*qtd] = inicio;
        tamanhos[*qtd] = n;
        (*qtd)++;
        return;
    }
    int meio = n / 2;
    folhas_originais(filho_esquerdo(rank), meio, delta, p, inicio,
                     ranks, inicios, tamanhos, qtd);
    folhas_originais(filho_direito(rank), n - meio, delta, p, inicio + meio,
                     ranks, inicios, tamanhos, qtd);
}

static void folhas_bal(int rank, int nivel, int max_rank, int n, int *folhas, int *qtd)
{
    int ajudante = ajudante_de(rank, nivel, max_rank);
    if (ajudante > max_rank) {
        folhas[(*qtd)++] = n;
        return;
    }
    int meio = n / 2;
    folhas_bal(rank, nivel + 1, max_rank, meio, folhas, qtd);
    folhas_bal(ajudante, nivel + 1, max_rank, n - meio, folhas, qtd);
}

static int cobre_balanceada(int rank, int nivel, int max_rank, int n, char *visto)
{
    visto[rank] = 1;
    int ajudante = ajudante_de(rank, nivel, max_rank);
    if (ajudante > max_rank)
        return n;
    if (nivel_inicial(ajudante) != nivel + 1)
        return -1;
    int meio = n / 2;
    int esq = cobre_balanceada(rank, nivel + 1, max_rank, meio, visto);
    int dir = cobre_balanceada(ajudante, nivel + 1, max_rank, n - meio, visto);
    if (esq < 0 || dir < 0)
        return -1;
    return esq + dir;
}

int main(void)
{
    espera(delta_da_arvore(40, 7) == 10, "delta da figura");
    espera(delta_da_arvore(41, 7) == 11, "delta com teto");
    espera(delta_da_arvore(100000, 1) == 100000, "delta de um processo");
    espera(delta_da_arvore(100000, 31) == 6250, "delta de 31");
    espera(delta_da_arvore(100000, 1023) == 196, "delta de 1023");

    int ranks[8], inicios[8], tamanhos[8], qtd = 0;
    folhas_originais(0, 40, 10, 7, 0, ranks, inicios, tamanhos, &qtd);
    espera(qtd == 4, "a figura tem 4 folhas");
    int folha_ok = qtd == 4
        && ranks[0] == 3 && inicios[0] == 0 && tamanhos[0] == 10
        && ranks[1] == 4 && inicios[1] == 10 && tamanhos[1] == 10
        && ranks[2] == 5 && inicios[2] == 20 && tamanhos[2] == 10
        && ranks[3] == 6 && inicios[3] == 30 && tamanhos[3] == 10;
    espera(folha_ok, "folhas da figura 1");

    int ps[] = {1, 3, 7, 15, 31, 63, 127, 255, 511, 1023};
    for (int i = 0; i < 10; i++) {
        int p = ps[i];
        int delta = delta_da_arvore(100000, p);
        if (!arvore_ocupa_todos(100000, delta, 0, p)) {
            fprintf(stderr, "falha: n=100000 p=%d delta=%d nao ocupa a arvore\n", p, delta);
            falhas++;
        }
    }
    espera(!arvore_ocupa_todos(5, delta_da_arvore(5, 7), 0, 7),
           "n=5 com 7 processos tem de ser recusado");

    /* n medido na atlântica: o t1 ficou em torno de 45 s. */
    int campanha[] = {1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 127, 255, 511, 1023};
    for (int i = 0; i < 15; i++) {
        int p = campanha[i];
        int delta = delta_da_arvore(212064, p);
        int cabe = arvore_ocupa_todos(212064, delta, 0, p);
        int potencia = p == 2 || p == 4 || p == 8 || p == 16 || p == 32;
        if (!potencia && !cabe) {
            fprintf(stderr, "falha: n=212064 p=%d delta=%d nao ocupa a arvore\n", p, delta);
            falhas++;
        }
        char *visto = calloc((size_t)p, 1);
        int soma = visto ? cobre_balanceada(0, 0, p - 1, 212064, visto) : -1;
        int todos = soma == 212064;
        for (int r = 0; visto && r < p; r++)
            todos = todos && visto[r];
        if (!todos) {
            fprintf(stderr, "falha: balanceada nao cobre n=212064 p=%d\n", p);
            falhas++;
        }
        free(visto);
    }

    espera(ordenou(40, 0, 40, 1), "bubble de 40");
    espera(ordenou(40, 0, 10, 1), "arvore original de 40 com delta 10");
    espera(ordenou(41, 0, 11, 1), "arvore original de 41");
    espera(ordenou(1000, 0, 1000, 1), "bubble de 1000");

    int pbal[] = {1, 2, 3, 4, 5, 6, 8, 16, 31, 32, 63, 127};
    for (int i = 0; i < 12; i++) {
        int p = pbal[i];
        char *visto = calloc((size_t)p, 1);
        int soma = visto ? cobre_balanceada(0, 0, p - 1, 40, visto) : -1;
        int todos = soma == 40;
        for (int r = 0; visto && r < p; r++)
            todos = todos && visto[r];
        if (!todos) {
            fprintf(stderr, "falha: balanceada nao cobre p=%d (soma=%d)\n", p, soma);
            falhas++;
        }
        free(visto);
        if (!ordenou(40, 1, 0, p)) {
            fprintf(stderr, "falha: balanceada nao ordena n=40 p=%d\n", p);
            falhas++;
        }
    }
    espera(ordenou(1000, 1, 0, 31), "balanceada n=1000 p=31");
    espera(ordenou(1000, 1, 0, 32), "balanceada n=1000 p=32");

    int folhas[8], nfolhas = 0;
    folhas_bal(0, 0, 2, 40, folhas, &nfolhas);
    espera(nfolhas == 3 && folhas[0] == 10 && folhas[1] == 10 && folhas[2] == 20,
           "folhas da balanceada com 3 processos");
    nfolhas = 0;
    folhas_bal(0, 0, 3, 40, folhas, &nfolhas);
    espera(nfolhas == 4 && folhas[0] == 10 && folhas[1] == 10
           && folhas[2] == 10 && folhas[3] == 10,
           "folhas da balanceada com 4 processos");

    if (falhas) {
        fprintf(stderr, "%d falha(s)\n", falhas);
        return 1;
    }
    printf("ok\n");
    return 0;
}
