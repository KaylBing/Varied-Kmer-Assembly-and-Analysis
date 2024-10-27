import sys
from collections import defaultdict, deque

def read_kmers(file):
    kmers = []
    with open(file, "r") as handle:
        for line in handle:
            kmer = line.strip()
            if kmer:  # Ensure we don't pick up empty lines
                kmers.append(kmer)
    return kmers

def build_de_bruijn_graph(kmers):
    edges = defaultdict(list)
    nodes = set()
    for kmer in kmers:
        prefix = kmer[:-1]
        suffix = kmer[1:]
        edges[prefix].append(suffix)
        nodes.add(prefix)
        nodes.add(suffix)
    return edges, nodes

def find_eulerian_path(graph):
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    for node in graph:
        out_degree[node] = len(graph[node])
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    start_node = next((node for node in out_degree if out_degree[node] > in_degree[node]), None)
    if not start_node:
        start_node = next(iter(graph))

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

def reconstruct_genome_from_path(path):
    genome = path[0]
    for node in path[1:]:
        genome += node[-1]
    return genome

def reconstruct_genome(file):
    kmers = read_kmers(file)
    graph, _ = build_de_bruijn_graph(kmers)
    path = find_eulerian_path(graph)
    genome = reconstruct_genome_from_path(path)
    return genome

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reconstruct_genome.py <path_to_kmers_file>")
        sys.exit(1)

    file = sys.argv[1]
    genome = reconstruct_genome(file)
    print("Reconstructed Genome Length:", len(genome))
    print("Reconstructed Genome:", genome)
