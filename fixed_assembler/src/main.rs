use bio::io::fasta;
use bio::io::fasta::Writer;
use std::fs::File;
use std::io::{self, Write};

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

fn main() {
    let contigs = vec![
        "ATGCGTACG".to_string(),
        "CGTACGTAG".to_string(),
        "GTACGTACT".to_string(),
    ];
    let k = 4;
    let output_file = "assembled_genome.fasta";

    let assembled_genome = assemble_genome(contigs, k);
    if !assembled_genome.is_empty() {
        if let Err(e) = write_to_fasta(&assembled_genome, output_file) {
            eprintln!("Error writing to FASTA file: {}", e);
        } else {
            println!("Genome assembly written to {}", output_file);
        }
    } else {
        println!("Genome assembly failed.");
    }
}

