#!/bin/bash
#SBATCH -n 8
#SBATCH -N 8
#SBATCH -t 0-10:00
#SBATCH -p serial
#SBATCH --mem=128G
#SBATCH -o myjob.o
#SBATCH -e myjob.e
#SBATCH --mail-type=ALL
#SBATCH --mail-user=akb523@nyu.edu

module purge
module load anaconda3/5.2.0
source ../../../Scripts/venv-urban/bin/activate
python3 tokenizing_dask.py
