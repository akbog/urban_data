#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 32
#SBATCH -N 2
#SBATCH -t 2-00:00
#SBATCH --mem=256GB
#SBATCH --job-name spark-test
#SBATCH --output spark-log-%J.txt

module purge
module load java/1.8.0_131
module load anaconda3/5.2.0 spark
source ../../../Scripts/venv-urban/bin/activate
echo $JAVA_HOME
spark-submit --total-executor-cores 64 --executor-memory 200G SparkJob.py
