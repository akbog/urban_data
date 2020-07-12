#!/bin/bash
# SBATCH -p parallel
# SBATCH -n 16
# SBATCH -N 1
# SBATCH -t 2-00:00
# SBATCH --mem=64GB
# SBATCH --job-name spark-test
# SBATCH --output spark-log.txt

module purge
module load spark

spark-submit SparkJob.py
