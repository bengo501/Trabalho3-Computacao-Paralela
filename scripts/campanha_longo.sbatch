#!/bin/bash
#SBATCH -J t3longo
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 06:00:00
#SBATCH -o results/slurm-longo-%j.out
# Mesma campanha, com t1 previsto em cerca de 5 min.
# O csv vai para results/longo. Cabe nas 6 h que a conta aceita.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
export N=545552
export OUTDIR=results/longo
export RODA_OVER=1
bash scripts/campanha.sbatch
