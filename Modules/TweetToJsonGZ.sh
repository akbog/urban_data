#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 16
#SBATCH -N 1
#SBATCH -t 05:00:00
#SBATCH --mem=64GB
#SBATCH --job-name jupyter
#SBATCH --output jupyter-log-%J.txt

module purge
module load python/gnu/3.7.3
source ../../../Scripts/venv-urban/bin/activate

python3 TweetToJsonGzRev.py 
