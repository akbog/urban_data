#!/bin/bash
#SBATCH -p parallel
#SBATCH -n 16
#SBATCH -N 1
#SBATCH -t 05:00:00
#SBATCH --mem=64GB
#SBATCH -o myjob.o
#SBATCH -e myjob.e
#SBATCH --mail-type=ALL
#SBATCH --mail-user=akb523@nyu.edu

module purge
module load anaconda3/5.2.0
source Scripts/venv-urban/bin/activate
python3 tokenize_parallel.py Tweet_Directory/historical_data/full_text_tweets.csv Tweet_Directory/historical_data/full_text_tweets_pre.csv Tweet_Directory/DFS
