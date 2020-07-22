#!/bin/sh

#SBATCH --nodes=1
#SBATCH --output="slurm-%j.out"

# SBATCH -t 0-12:00

#SBATCH --job-name=sparktest

#SBATCH --partition=serial

#SBATCH --ntasks-per-node=16
#SBATCH --exclusive
#SBATCH --no-kill

module load anaconda3/5.2.0 java/1.8.0_131 spark/2.4.6-hd2.7

source ../../../Scripts/venv-urban/bin/activate

module load ant/1.9.6

export JAVA_HOME="/gpfsnyu/packages/java/jdk1.8.0_131"

export SPARK_VERSION="2.4.6-hd2.7"

export SPARK_HOME="/gpfsnyu/packages/spark/${SPARK_VERSION}"

export SPARK_LOCAL_SCRATCH_DIR="/scratch/${USER}/sparkscratch/"

export SPARK_LOCAL_DIR="/tmp/${USER}/spark"

ipnip=$(hostname -i)
echo -e "  ssh -N -L 4040:$ipnip:4040 $USER@hpc.shanghai.nyu.edu\n"

XDG_RUNTIME_DIR=""
ipnport=$(shuf -i8000-9999 -n1)
ipnip=$(hostname -i)

echo -e "\n"
echo    "  Paste ssh command in a terminal on local host (i.e., laptop)"
echo    "  ------------------------------------------------------------"
echo -e "  ssh -N -L $ipnport:$ipnip:$ipnport $USER@hpc.shanghai.nyu.edu\n"
echo    "  Open this address in a browser on local host; see token below"
echo    "  ------------------------------------------------------------"
echo -e "  localhost:$ipnport                                      \n\n"

jupyter-lab --no-browser --port=$ipnport --ip=$ipnip
