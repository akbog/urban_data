#!/bin/bash
SBATCH -p
SBATCH -n 16
SBATCH -N 1
SBATCH -t 2-00:00
SBATCH --mem=64GB
SBATCH --job-name spark-test
SBATCH --output spark-log-%J.txt

module purge
module load java/1.8.0_131
module load spark

spark-submit --total-executor-cores 64 --driver-memory G SparkJob.py
