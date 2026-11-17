#!/bin/bash
#SBATCH -J t3verifica
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 00:30:00
#SBATCH -o results/verificar-%j.out
# Conferência curta antes da campanha. A figura usa 7 processos.
# -O é o --overcommit: o T2 precisou dele acima de 32 processos.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"

export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
export LD_LIBRARY_PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/lib:${LD_LIBRARY_PATH:-}
unset OMPI_MCA_mpi_yield_when_idle || true

mkdir -p results bin
make clean && make

echo "$SLURM_JOB_NODELIST" | tee results/nodes.txt

confere() {
    echo "== $* =="
    "$@"
    echo
}

confere srun -N 1 -n 1 ./bin/sequencial 40
confere srun -N 1 -n 1 ./bin/sequencial 40 10
confere srun -N 1 -n 1 ./bin/sequencial 41 11
confere srun -N 1 -n 1 ./bin/sequencial 40 balanceada 4
confere srun -N 1 -n 1 ./bin/sequencial 40 balanceada 3

confere srun -N 2 -n 7 --distribution=block ./bin/arvore 40 10
confere srun -N 2 -n 7 --distribution=block ./bin/arvore 41 11
confere srun -N 2 -n 7 --distribution=block ./bin/arvore 40 niveis 2
confere srun -N 1 -n 1 ./bin/arvore 1000 1000
confere srun -N 2 -n 4 --distribution=block ./bin/balanceada 40
confere srun -N 2 -n 3 --distribution=block ./bin/balanceada 40
confere srun -N 2 -n 31 --distribution=block ./bin/balanceada 40
confere srun -N 2 -n 32 --distribution=block ./bin/balanceada 40

export OMPI_MCA_mpi_yield_when_idle=1
confere srun -N 2 -n 7 --distribution=block ./bin/arvore 40 10
unset OMPI_MCA_mpi_yield_when_idle

delta63=$(python3 -c 'n=100000; p=63; print((2*n+p)//(p+1))')
confere srun -O -N 2 -n 63 --distribution=block ./bin/arvore 100000 "$delta63"

echo "verificacao do cluster terminou"
