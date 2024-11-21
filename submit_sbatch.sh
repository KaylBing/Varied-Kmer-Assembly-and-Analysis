#!/bin/bash
kmer=$0
#SBATCH --job-name=cursedPyorbitSandbox
#SBATCH --output=pyorbitoutput2.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=128G
#SBATCH --partition=cpu(all)

bash run_all.sh $kmer
