#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 4
#SBATCH -N 8
#SBATCH -t 01:00:00
#SBATCH --mem=64GB
#SBATCH --job-name jupyter
#SBATCH --output jupyter-log-%J.txt

module purge
module load python/gnu/3.7.3
source ../../../Scripts/venv-urban/bin/activate

XDG_RUNTIME_DIR=""
ipnport=8193
ipnip=$(hostname -i)

echo -e "\n"
echo    "  Paste ssh command in a terminal on local host (i.e., laptop)"
echo    "  ------------------------------------------------------------"
echo -e "  ssh -N -L $ipnport:$ipnip:$ipnport $USER@hpc.shanghai.nyu.edu\n"
echo    "  Open this address in a browser on local host; see token below"
echo    "  ------------------------------------------------------------"
echo -e "  localhost:$ipnport                                      \n\n"

jupyter-notebook --no-browser --port=$ipnport --ip=$ipnip
