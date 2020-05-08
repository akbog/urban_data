#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 32
#SBATCH -N 1
#SBATCH -t 2-00:00
#SBATCH --mem=64GB
#SBATCH --job-name lda_script
#SBATCH --output lda-script-%J.txt

module purge
module load python/gnu/3.7.3
source ../../../Scripts/venv-urban/bin/activate
python3 LDAModelScript.py
