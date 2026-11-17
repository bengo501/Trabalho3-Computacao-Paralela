#!/bin/bash
#SBATCH -J t3over
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 06:00:00
#SBATCH -o results/slurm-over-%j.out
# Série de 63 a 1023 processos, duas vezes, com a variável definida:
# OMPI_MCA_mpi_yield_when_idle=0 e =1.
# Continua o csv da campanha principal e usa o n já calibrado.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"

export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
export LD_LIBRARY_PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/lib:${LD_LIBRARY_PATH:-}
unset OMPI_MCA_mpi_yield_when_idle || true

OUT=${OUTDIR:-results}
mkdir -p "${OUT}/raw" bin
make

if [ ! -f "${OUT}/n.txt" ] || [ ! -f "${OUT}/runs.csv" ]; then
    echo "falta a campanha principal (${OUT}/n.txt e ${OUT}/runs.csv)" >&2
    exit 1
fi
N=$(cat "${OUT}/n.txt")
REPS=${REPS:-10}
echo "n da campanha: ${N}"

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

roda_seq() {
    local versao="$1" n="$2" delta="$3" p="$4" rep="$5"
    shift 5
    local log="${OUT}/raw/${versao}_d${delta}_p${p}_r${rep}.out"
    echo "${versao} n=${n} delta=${delta} p=${p} rep=${rep}"
    srun -N 1 -n 1 ./bin/sequencial "$@" > "${log}"
    local tempo
    tempo=$(ler_tempo "${log}") || exit 1
    grava "${versao}" "${n}" "${delta}" "${p}" 0 "${rep}" "${tempo}" OK
}

roda_mpi() {
    local bin="$1" versao="$2" n="$3" delta="$4" p="$5" yield="$6" rep="$7"
    shift 7
    local log="${OUT}/raw/${versao}_d${delta}_p${p}_y${yield}_r${rep}.out"
    echo "${versao} n=${n} delta=${delta} p=${p} yield=${yield} rep=${rep}"
    export OMPI_MCA_mpi_yield_when_idle="${yield}"
    srun -O -N 2 -n "${p}" --distribution=block --export=ALL,OMPI_MCA_mpi_yield_when_idle="${yield}" "${bin}" "$@" > "${log}"
    local tempo
    tempo=$(ler_tempo "${log}") || exit 1
    grava "${versao}" "${n}" "${delta}" "${p}" "${yield}" "${rep}" "${tempo}" OK
}

delta_de() {
    python3 -c "n=${1}; p=${2}; print((2*n+p)//(p+1))"
}

for p in 63 127 255 511 1023; do
    delta=$(delta_de "${N}" "${p}")
    for rep in $(seq 1 "${REPS}"); do
        roda_seq t1_delta "${N}" "${delta}" "${p}" "${rep}" "${N}" "${delta}"
    done
    for yield in 0 1; do
        for rep in $(seq 1 "${REPS}"); do
            roda_mpi ./bin/arvore arvore "${N}" "${delta}" "${p}" "${yield}" "${rep}" "${N}" "${delta}"
        done
    done
done

python3 scripts/resumir.py "${OUT}/runs.csv" | tee "${OUT}/resumo.txt"
echo "serie de 63 a 1023 terminou"
