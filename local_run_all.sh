#!/bin/bash

# Define the Python script path
PYTHON_SCRIPT="libs/assembler_2/assembler_other.py"
DATA_FILE="data/covid_genome.txt"

# Loop over k-mer values from 3 to 50
for k in {3..50}; do
  # Loop over missing k-mers percentage from 1% to 10%
  for missing in {0..10}; do
    echo "Running assembler with k=$k and missing=${missing}%"
    python $PYTHON_SCRIPT $DATA_FILE $k $missing
    echo "Completed k=$k with missing=${missing}%"
    echo "--------------------------------------------"
  done
done

echo "All runs completed."

