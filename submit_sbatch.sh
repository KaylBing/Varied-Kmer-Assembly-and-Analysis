#!/bin/bash
kmer=$2
inputfile=$1
#SBATCH --job-name=bad_job
#SBATCH --output=test_submit.txt
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --partition=cpu(all)

bash run_all.sh $inputfile $kmer
