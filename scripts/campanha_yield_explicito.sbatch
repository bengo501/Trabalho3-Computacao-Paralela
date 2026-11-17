#!/bin/bash
#SBATCH -J t3yield
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 03:00:00
#SBATCH -o results/slurm-yield-%j.out
# Errata da versão 2: a série de 63 a 1023 com a variável definida
# nos dois valores. Não mexe nos csv já medidos.
# Três tamanhos, só esta série, para comparar com a rodada em que
# a espera ativa apagava a variável em vez de gravar 0.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"

export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
export LD_LIBRARY_PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/lib:${LD_LIBRARY_PATH:-}

make

confere_yield() {
    local y="$1"
    local saida
    saida=$(srun -O -N 2 -n 63 --distribution=block \
        --export=ALL,OMPI_MCA_mpi_yield_when_idle="${y}" \
        printenv OMPI_MCA_mpi_yield_when_idle | sort -u)
    echo "conferencia yield=${y}: [${saida}]"
    if [ "${saida}" != "${y}" ]; then
        echo "a variavel nao chegou aos processos com o valor ${y}" >&2
        exit 1
    fi
}

confere_yield 0
confere_yield 1

ler_tempo() {
    local log="$1"
    local tempo ver
    tempo=$(sed -n 's/.*tempo=\([0-9.][0-9.]*\).*/\1/p' "$log" | tail -1)
    ver=$(sed -n 's/.*verificacao=\(OK\|ERRO\).*/\1/p' "$log" | tail -1)
    if [ -z "${tempo}" ] || [ "${ver}" != "OK" ]; then
        echo "falha em ${log}" >&2
        cat "${log}" >&2 || true
        exit 1
    fi
    echo "${tempo}"
}

grava() {
    echo "$1,$2,$3,$4,$5,$6,$7,$8" >> "${OUT}/runs.csv"
}

roda_mpi() {
    local n="$1" delta="$2" p="$3" yield="$4" rep="$5"
    local log="${OUT}/raw/arvore_d${delta}_p${p}_y${yield}_r${rep}.out"
    echo "arvore n=${n} delta=${delta} p=${p} yield=${yield} rep=${rep}"
    export OMPI_MCA_mpi_yield_when_idle="${yield}"
    srun -O -N 2 -n "${p}" --distribution=block \
        --export=ALL,OMPI_MCA_mpi_yield_when_idle="${yield}" \
        ./bin/arvore "${n}" "${delta}" > "${log}"
    local tempo
    tempo=$(ler_tempo "${log}") || exit 1
    grava arvore "${n}" "${delta}" "${p}" "${yield}" "${rep}" "${tempo}" OK
}

delta_de() {
    python3 -c "n=${1}; p=${2}; print((2*n+p)//(p+1))"
}

REPS=${REPS:-10}
BASE=results/yield-explicito

for par in "212064 ${BASE}/ref" "345037 ${BASE}/medio" "545552 ${BASE}/longo"; do
    N=${par%% *}
    OUT=${par#* }
    mkdir -p "${OUT}/raw"
    echo "versao,n,delta,p,yield,rep,tempo,verificacao" > "${OUT}/runs.csv"
    echo "${N}" > "${OUT}/n.txt"
    echo "tamanho ${N} em ${OUT}"
    for p in 63 127 255 511 1023; do
        delta=$(delta_de "${N}" "${p}")
        for yield in 0 1; do
            for rep in $(seq 1 "${REPS}"); do
                roda_mpi "${N}" "${delta}" "${p}" "${yield}" "${rep}"
            done
        done
    done
done

echo "serie explicita de yield terminou"
