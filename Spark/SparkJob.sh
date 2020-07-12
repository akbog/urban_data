#!/bin/bash
# SBATCH -p parallel
# SBATCH --cpus-per-task 5
# SBATCH --nodes 3
# SBATCH -t 2-00:00
# SBATCH --mem=64GB
# SBATCH --job-name spark-test
# SBATCH --output spark-log-%J.txt

module purge
module load java/1.8.0_131
module load spark
source ../../../Scripts/venv-urban/bin/activate


ipnip=$(hostname -i)
echo -e "  ssh -N -L 4040:$ipnip:4040 $USER@hpc.shanghai.nyu.edu\n"
echo -e "  localhost:$ipnport                                      \n\n"

spark-submit SparkJob.py
