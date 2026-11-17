#!/bin/bash
#SBATCH -J t3ordenacao
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 06:00:00
#SBATCH -o results/slurm-%j.out
# Campanha do T3, sempre nestes 2 nós.
# distribuição block: ranks consecutivos no mesmo nó.
# A série de 63 a 1023 fica em campanha_over.sbatch,
# porque a conta não aceita um job de 12 horas em 2 nós.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"

export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
export LD_LIBRARY_PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/lib:${LD_LIBRARY_PATH:-}
unset OMPI_MCA_mpi_yield_when_idle || true

OUT=${OUTDIR:-results}
mkdir -p "${OUT}/raw" bin
make clean && make

echo "$SLURM_JOB_NODELIST" | tee "${OUT}/nodes.txt"
srun -N 2 -n 2 --distribution=block bash -c 'echo == $(hostname) ==; lscpu' > "${OUT}/lscpu.txt"

REPS=${REPS:-10}

if [ -f "${OUT}/runs.csv" ]; then
    mv "${OUT}/runs.csv" "${OUT}/runs-$(date +%Y%m%d-%H%M%S).csv"
fi
echo "versao,n,delta,p,yield,rep,tempo,verificacao" > "${OUT}/runs.csv"

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

medir_t1() {
    local n="$1"
    local log="${OUT}/raw/calib_n${n}.out"
    echo "calibracao n=${n}"
    srun -N 1 -n 1 ./bin/sequencial "${n}" > "${log}"
    local tempo
    tempo=$(ler_tempo "${log}") || exit 1
    echo "${n} ${tempo}" | tee -a "${OUT}/calib.txt"
}

if [ -n "${N:-}" ]; then
    echo "n informado: ${N}"
else
    : > "${OUT}/calib.txt"
    medir_t1 100000
    N=100000
    for _ in 1 2 3; do
        if escolha=$(python3 scripts/escolhe_n.py "${OUT}/calib.txt"); then
            N=${escolha}
            break
        fi
        medir_t1 "${escolha}"
        N=${escolha}
    done
fi
echo "${N}" | tee "${OUT}/n.txt"

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
    # 0 e 1 saem explícitos. Apagar a variável não vale como espera ativa:
    # o lançamento pode ceder o núcleo sozinho.
    export OMPI_MCA_mpi_yield_when_idle="${yield}"
    local nos=2
    if [ "${p}" -eq 1 ]; then
        nos=1
    fi
    if [ "${p}" -gt 32 ]; then
        srun -O -N "${nos}" -n "${p}" --distribution=block --export=ALL,OMPI_MCA_mpi_yield_when_idle="${yield}" "${bin}" "$@" > "${log}"
    else
        srun -N "${nos}" -n "${p}" --distribution=block --export=ALL,OMPI_MCA_mpi_yield_when_idle="${yield}" "${bin}" "$@" > "${log}"
    fi
    local tempo
    tempo=$(ler_tempo "${log}") || exit 1
    grava "${versao}" "${n}" "${delta}" "${p}" "${yield}" "${rep}" "${tempo}" OK
}

delta_de() {
    python3 -c "n=${1}; p=${2}; print((2*n+p)//(p+1))"
}

for rep in $(seq 1 "${REPS}"); do
    roda_seq t1 "${N}" "${N}" 1 "${rep}" "${N}"
done

for p in 1 3 7 15 31; do
    delta=$(delta_de "${N}" "${p}")
    if [ "${delta}" -ne "${N}" ]; then
        for rep in $(seq 1 "${REPS}"); do
            roda_seq t1_delta "${N}" "${delta}" "${p}" "${rep}" "${N}" "${delta}"
        done
    fi
    for rep in $(seq 1 "${REPS}"); do
        roda_mpi ./bin/arvore arvore "${N}" "${delta}" "${p}" 0 "${rep}" "${N}" "${delta}"
    done
done

for p in 2 4 8 16 32 31; do
    for rep in $(seq 1 "${REPS}"); do
        roda_seq t1_balanceada "${N}" 0 "${p}" "${rep}" "${N}" balanceada "${p}"
    done
    for rep in $(seq 1 "${REPS}"); do
        roda_mpi ./bin/balanceada balanceada "${N}" 0 "${p}" 0 "${rep}" "${N}"
    done
done

python3 scripts/resumir.py "${OUT}/runs.csv" | tee "${OUT}/resumo.txt"
echo "campanha principal terminou"

if [ "${RODA_OVER:-0}" = "1" ]; then
    echo "seguindo para 63 a 1023 no mesmo job"
    bash scripts/campanha_over.sbatch
fi
