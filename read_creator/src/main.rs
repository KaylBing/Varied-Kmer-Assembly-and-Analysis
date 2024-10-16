use std::fs::File;
use std::io::{self, Read, Write, BufReader, BufWriter};

fn break_into_reads(genome: &str, read_length: usize) -> Vec<String> {
    let mut reads = Vec::new();
    // Use a while loop to control the step size of i
    let mut i = 0;
    while i + read_length <= genome.len() {
        let read = &genome[i..i + read_length];
        reads.push(read.to_string());
        i += read_length - 1; // Move by read_length - 1
    }

    reads
}

fn main() -> io::Result<()> {
    let input_file_path = "/home/mikhailu/Genetics_Code/Genomes/Cholerae/Vibrio_cholerae.txt";
    let output_file_path = "vibrio_cholerae_segments.txt";
    let read_length = 10;

    // Read the genome from the input file
    let input_file = File::open(input_file_path)?;
    let mut genome = String::new();
    let mut reader = BufReader::new(input_file);

    reader.read_to_string(&mut genome)?;

    // Generate the reads
    let reads = break_into_reads(&genome, read_length);

    // Write the reads to the output file
    let output_file = File::create(output_file_path)?;
    let mut writer = BufWriter::new(output_file);

    for read in reads {
        writeln!(writer, "{}", read)?;
    }

    println!("Reads written to {}", output_file_path);
    Ok(())
}
