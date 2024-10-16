use bio::io::fasta;
use bio::io::fasta::Writer;
use std::fs::File;
use std::io::{self, Write};
use std::fs;

// Function to look for overlaps in reads //
fn find_overlap(seq1: &str, seq2: &str, k: usize) -> usize {
    let max_overlap_len = k.min(seq1.len()).min(seq2.len());
    for i in (1..=max_overlap_len).rev() {
        if &seq1[seq1.len() - i..] == &seq2[..i] {
            return i;
        }
    }
    0
}

// Assembly function, k size will be changed to by a user input, with a default size //
fn assemble_genome(mut contigs: Vec<String>, k: usize) -> String {
    while contigs.len() > 1 {
        let mut max_overlap_len = 0;
        let mut best_pair = (0, 0);

        for i in 0..contigs.len() {
            for j in 0..contigs.len() {
                if i != j {
                    let overlap_len = find_overlap(&contigs[i], &contigs[j], k);
                    if overlap_len > max_overlap_len {
                        max_overlap_len = overlap_len;
                        best_pair = (i, j);
                    }
                }
            }
        }

        if max_overlap_len == 0 {
            println!("No overlaps found. Assembly is incomplete.");
            break;
        }

        let (i, j) = best_pair;
        let contig1 = contigs.swap_remove(i);
        let contig2 = if i < j { contigs.swap_remove(j - 1) } else { contigs.swap_remove(j) };
        let merged_contig = format!("{}{}", contig1, &contig2[max_overlap_len..]);
        contigs.push(merged_contig);
    }

    contigs.pop().unwrap_or_default()
}

// Writes assembled genome //
fn write_to_fasta(sequence: &str, output_file: &str) -> io::Result<()> {
    let file = File::create(output_file)?;
    let mut writer = Writer::new(file);
    writer.write("AssembledGenome", None, sequence.as_bytes())?;
    Ok(())
}

fn break_into_reads(genome: &str, read_length: usize) -> Vec<String> {
    let mut reads = Vec::new();
    
    // Iterate through the genome and generate reads of the specified length
    for i in 0..=genome.len() - read_length {
        let read = &genome[i..i + read_length];
        reads.push(read.to_string());
    }
    
    reads
}

fn main() {
    let genome = fs::read_to_string("/home/mikhailu/Genetics_Code/Varied-Kmer-Assembly-and-Analysis/read_creator/src/vibrio_cholerae_segments.txt");
    
    match genome {
        Ok(genome_data) => {
            let read_length = 5;
            let reads = break_into_reads(&genome_data, read_length);
            
            for read in reads {
                println!("{}", read);
            }
        }
        Err(e) => {
            eprintln!("Error reading genome file: {}", e);
        }
    }
}
