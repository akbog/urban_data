#!/bin/bash
#SBATCH -n 16
#SBATCH -N 1
#SBATCH -t 0-10:00
#SBATCH -p parallel
#SBATCH --mem=64G
#SBATCH -o myjob.o
#SBATCH -e myjob.e
#SBATCH --mail-type=ALL
#SBATCH --mail-user=akb523@nyu.edu

module purge
module load anaconda3/5.2.0
source ../../../Scripts/venv-urban/bin/activate
python3 tokenizing_dask.py
