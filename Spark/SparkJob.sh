#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 32
#SBATCH -N 1
#SBATCH -t 2-00:00
#SBATCH --mem=64GB
#SBATCH --job-name spark-test
#SBATCH --output spark-log-%J.txt

module purge
module load java/1.8.0_131
module load anaconda3/5.2.0 spark

source ../../../Scripts/venv-urban/bin/activate
echo $JAVA_HOME

XDG_RUNTIME_DIR=""
ipnport=$(shuf -i8000-9999 -n1)
ipnip=$(hostname -i)
Master="local[*]"
echo -e "  ssh -N -L $ipnport:$ipnip:$ipnport $USER@hpc.shanghai.nyu.edu\n"
echo -e "  localhost:$ipnport                                      \n\n"
spark-submit --master $Master --total-executor-cores 64 --executor-memory 200G SparkJob.py
