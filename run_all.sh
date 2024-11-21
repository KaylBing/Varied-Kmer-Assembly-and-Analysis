#!bin/bash

kmer=$2
inputfile=$1


python3 libs/assembler_2/assembler_other.py $inputfile $kmer
