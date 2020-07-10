#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 32
#SBATCH -N 2
#SBATCH -t 2-00:00
#SBATCH --mem=64GB
#SBATCH --job-name jupyter
#SBATCH --output jupyter-log-%J.txt

module purge
spark-submit SparkJob.py
