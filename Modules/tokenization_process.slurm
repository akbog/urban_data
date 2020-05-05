#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 16
#SBATCH -N 1
#SBATCH -t 1-00:00
#SBATCH --mem=64GB
#SBATCH -o tokenjob.o
#SBATCH -e tokenjob.e
# SBATCH --mail-type=ALL
# SBATCH --mail-user=akb523@nyu.edu

module purge
module load anaconda3/5.2.0
source ../../../Scripts/venv-urban/bin/activate
python3 tokenizing_dask.py
