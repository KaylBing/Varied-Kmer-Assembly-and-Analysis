!#bin/bash

kmer=$0
inputfile=$1


python3 libs/assembler2/assembler_other.py $inputfile $kmer
