#!/bin/bash
#SBATCH --mail-user=akb523
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=1-01:10:00
#SBATCH --mem=200G
#SBATCH --output=Job.%j.out
#SBATCH --error=Job.%j.err
#SBATCH --account=akb523
#SBATCH --partition=debug
module purge
module load python/intel/3.6.6
python tweepy_streamer.py ./Tweets
