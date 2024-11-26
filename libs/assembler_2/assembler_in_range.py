import subprocess
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
import time

# Function to run the assembly process
def run_assembly(reconstruct_genome_script: str, genome_file: str, output_dir: str, k: int, remove_percentage: float):
    command = [
        "python", reconstruct_genome_script,  # Path to the reconstruct_genome.py script
        genome_file,  # Path to the genome (sequence) file
        str(k),  # K-mer size
        str(remove_percentage)  # Percentage of missing k-mers
    ]
    
    try:
        print(f"Running assembly with k={k} and missing k-mer percentage={remove_percentage}...")
        subprocess.run(command, check=True)
        print(f"Finished assembly with k={k} and missing k-mer percentage={remove_percentage}.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred for k={k} and missing k-mer percentage={remove_percentage}: {e}")

# Function to handle parallel assembly with different k-values and percentages
def run_assemblies_parallel(reconstruct_genome_script: str, genome_file: str, output_dir: str, k_range: range, remove_percentage_range: range, num_threads: int = 4):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        
        for k in k_range:
            for remove_percentage in remove_percentage_range:
                # Submit tasks to the executor
                futures.append(executor.submit(run_assembly, reconstruct_genome_script, genome_file, output_dir, k, remove_percentage))
        
        # Wait for all futures to complete
        for future in futures:
            future.result()  # This will re-raise any exception that occurred during execution

# Main function to parse arguments and start the assembly process
def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Run genome assembly with different k-mer values and removal percentages.")
    parser.add_argument("reconstruct_genome_script", help="Path to the reconstruct_genome.py script")
    parser.add_argument("genome_file", help="Path to the genome (sequence) file")
    parser.add_argument("output_dir", help="Directory to save output files")
    parser.add_argument("--k_start", type=int, default=3, help="Starting k-mer size (default: 3)")
    parser.add_argument("--k_end", type=int, default=10, help="Ending k-mer size (default: 10)")
    parser.add_argument("--k_step", type=int, default=1, help="Step for k-mer size (default: 1)")
    parser.add_argument("--remove_start", type=float, default=0.0, help="Starting k-mer removal percentage (default: 0.0)")
    parser.add_argument("--remove_end", type=float, default=30.0, help="Ending k-mer removal percentage (default: 30.0)")
    parser.add_argument("--remove_step", type=float, default=10.0, help="Step for k-mer removal percentage (default: 10.0)")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for parallel execution (default: 4)")

    args = parser.parse_args()

    # Validate output directory
    if not os.path.exists(args.output_dir):
        print(f"Error: Output directory '{args.output_dir}' does not exist.")
        return

    # Create a range for k-values and removal percentages
    k_range = range(args.k_start, args.k_end + 1, args.k_step)
    remove_percentage_range = [x for x in range(int(args.remove_start), int(args.remove_end) + 1, int(args.remove_step))]

    print(f"Starting assembly with k-values in range {args.k_start} to {args.k_end} and removal percentages from {args.remove_start}% to {args.remove_end}%.")

    # Run the assemblies in parallel
    start_time = time.time()
    run_assemblies_parallel(args.reconstruct_genome_script, args.genome_file, args.output_dir, k_range, remove_percentage_range, args.threads)
    print(f"All assemblies completed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()

