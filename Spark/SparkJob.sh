#!/bin/bash
# SBATCH -p parallel
# SBATCH --ntasks-per-node 5
# SBATCH --nodes 6
# SBATCH -t 2-00:00
# SBATCH --mem=128GB
# SBATCH --job-name spark-test
# SBATCH --output spark-log-%J.txt

module purge
module load java/1.8.0_131
module load spark
source ../../../Scripts/venv-urban/bin/activate


ipnip=$(hostname -i)
echo -e "  ssh -N -L 4040:$ipnip:4040 $USER@hpc.shanghai.nyu.edu\n"

spark-submit --num-executors 6 --executor-cores 24 --executor-memory 124G SparkJob.py
