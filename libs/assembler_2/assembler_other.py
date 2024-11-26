from collections import defaultdict, deque
from typing import List, Dict, Tuple
import random
import sys
import time
import signal

# Timeout exception
class TimeoutException(Exception):
    pass

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutException("Genome reconstruction timed out after 10 minutes.")

# Generate k-mers from a sequence
def get_kmer_count_from_sequence(sequence: str, k: int = 3, cyclic: bool = True) -> Dict[str, int]:
    kmers = defaultdict(int)
    for i in range(len(sequence)):
        kmer = sequence[i:i + k]
        if len(kmer) != k:
            if cyclic:
                kmer += sequence[:(k - len(kmer))]
            else:
                continue
        kmers[kmer] += 1
    return dict(kmers)

# Randomly remove a percentage of k-mers
def remove_random_kmers(kmers: Dict[str, int], percentage: float) -> Dict[str, int]:
    if percentage <= 0:
        return kmers
    total_kmers = list(kmers.keys())
    remove_count = int(len(total_kmers) * (percentage / 100))
    to_remove = set(random.sample(total_kmers, remove_count))
    return {k: v for k, v in kmers.items() if k not in to_remove}

# Build a de Bruijn graph
def build_de_bruijn_graph(kmers: Dict[str, int]) -> Dict[str, List[str]]:
    edges = defaultdict(list)
    for kmer, count in kmers.items():
        prefix, suffix = kmer[:-1], kmer[1:]
        edges[prefix].extend([suffix] * count)
    return edges

# Find an Eulerian path
def find_eulerian_path(graph: Dict[str, List[str]]) -> List[str]:
    if not graph:
        return []
        
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    for node, neighbors in graph.items():
        out_degree[node] = len(neighbors)
        for neighbor in neighbors:
            in_degree[neighbor] += 1

    start_node = next((node for node in out_degree if out_degree[node] > in_degree[node]), 
                      next(iter(graph)))

    stack = [start_node]
    path = deque()
    
    while stack:
        node = stack[-1]
        if graph[node]:
            next_node = graph[node].pop()
            stack.append(next_node)
        else:
            path.appendleft(stack.pop())
            
    return list(path)

# Reconstruct sequence from Eulerian path
def reconstruct_sequence(path: List[str]) -> str:
    if not path:
        return ""
    return path[0] + ''.join(node[-1] for node in path[1:])

# Score the reconstructed sequence
def score_sequence(original: str, reconstructed: str, circular: bool = True,
                  match_score: float = 1.0, mismatch_score: float = -0.5,
                  length_penalty: float = -1.0) -> Tuple[float, Dict]:
    if not circular:
        min_length = min(len(original), len(reconstructed))
        length_diff = abs(len(original) - len(reconstructed))
        matches = sum(1 for i in range(min_length) if original[i] == reconstructed[i])
        mismatches = min_length - matches
        
        base_score = (matches * match_score) + (mismatches * mismatch_score)
        length_penalty_score = length_diff * length_penalty
        
        details = {
            'matches': matches,
            'mismatches': mismatches,
            'length_diff': length_diff,
            'base_score': base_score,
            'length_penalty': length_penalty_score,
            'percent_identity': (matches / min_length * 100) if min_length > 0 else 0,
            'mode': 'linear'
        }
        return base_score + length_penalty_score, details
    
    best_score = float('-inf')
    best_details = {}
    
    for i in range(len(reconstructed)):
        rotated = reconstructed[i:] + reconstructed[:i]
        score, details = score_sequence(original, rotated, False, 
                                         match_score, mismatch_score, length_penalty)
        if score > best_score:
            best_score = score
            best_details = details
            best_details.update({
                'rotation': i,
                'mode': 'circular',
                'aligned_sequence': rotated
            })
    
    return best_score, best_details

# Main reconstruction function
def reconstruct_from_kmers(sequence: str, k: int, cyclic: bool = True, 
                           remove_percentage: float = 0.0) -> Tuple[str, Dict, float]:
    start_time = time.time()
    kmers = get_kmer_count_from_sequence(sequence, k, cyclic)
    kmers = remove_random_kmers(kmers, remove_percentage)
    graph = build_de_bruijn_graph(kmers)
    path = find_eulerian_path(graph)
    reconstructed = reconstruct_sequence(path)
    
    score, details = score_sequence(sequence, reconstructed, circular=cyclic)
    details['reconstructed_sequence'] = reconstructed
    runtime = time.time() - start_time
    return reconstructed, details, runtime

# Entry point
if __name__ == "__main__":
    timeout_seconds = 600  # 10 minutes
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    try:
        seq_file = sys.argv[1]
        with open(seq_file, "r") as handle:
            sequence = handle.read().strip()

        sequence = sequence.replace("\n", "")
        kval = int(sys.argv[2])
        removal_percentage = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

        print(f"Original sequence: {sequence[0:100]}...")
        print(f"Length: {len(sequence)}")
        print(f"Randomly removing {removal_percentage:.2f}% of kmers.")

        reconstructed, details, runtime = reconstruct_from_kmers(sequence, k=kval, cyclic=True,
                                                                  remove_percentage=removal_percentage)
        print(f"K value: {kval}")
        print(f"\nReconstructed sequence: {reconstructed[:100]}...")
        print(f"Score: {details['base_score']:.1f}")
        print(f"Identity: {details['percent_identity']:.1f}%")
        print(f"Rotation needed: {details.get('rotation', 0)} positions")
        print(f"Runtime: {runtime:.2f} seconds")

        output_filename = f"output_k{kval}_missing{int(removal_percentage)}.txt"
        with open(output_filename, "w") as output_file:
            output_file.write(f"K value: {kval}\n")
            output_file.write(f"Percentage of missing kmers: {removal_percentage:.2f}%\n")
            output_file.write(f"Runtime: {runtime:.2f} seconds\n")
            output_file.write(f"Score: {details['base_score']:.1f}\n")
            output_file.write(f"Identity: {details['percent_identity']:.1f}%\n")
            output_file.write(f"Rotation needed: {details.get('rotation', 0)} positions\n")
            output_file.write(f"Original sequence snippet: {sequence[100:200]}\n")
            output_file.write(f"Reconstructed sequence snippet: {reconstructed[100:200]}\n")
            output_file.write(f"Full reconstructed sequence: {details['reconstructed_sequence']}\n")

        print(f"Results saved to {output_filename}")

    except TimeoutException as e:
        print(f"Error: {e}")
        sys.exit(1)
