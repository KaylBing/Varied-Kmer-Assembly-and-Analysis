#!/bin/bash

for i in {3..50}
do
	sbatch submit_sbatch.sh data/covid_genome.txt $i
done
