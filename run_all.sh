#!bin/bash

kmer=$1
inputfile=$0


python3 libs/assembler_2/assembler_other.py $inputfile $kmer
