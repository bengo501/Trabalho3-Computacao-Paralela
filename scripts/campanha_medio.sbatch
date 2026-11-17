#!/bin/bash
#SBATCH -J t3medio
#SBATCH -N 2
#SBATCH --nodelist=atlantica[03-04]
#SBATCH --exclusive
#SBATCH -t 06:00:00
#SBATCH -o results/slurm-medio-%j.out
# Mesma campanha, com t1 previsto em cerca de 2 min.
# O csv vai para results/medio e não mexe no de 45 s.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
export N=345037
export OUTDIR=results/medio
export RODA_OVER=1
bash scripts/campanha.sbatch
