# This code uses networkx girvan_newman algorithm to compute the communities

# Core imports
import json
import os
from glob import glob

# Library imports
import networkx as nx
from networkx.algorithms import community
import click
from tqdm import tqdm

SAVE_FOLDER = "community_detection/"


def run_girvan_newman(G: nx.Graph):
    def highest_betweenness(G):
        edges = list(G.edges)
        betweenness = {
            (u, v): (G.nodes[u].get("betweenness", 0) + G.nodes[v].get("betweenness", 0)) / 2 for (u, v) in edges
        }
        return max(betweenness, key=lambda x: x[1])

    tqdm.write("Running girvan_newman method")
    centrality = community.centrality.girvan_newman(G, most_valuable_edge=highest_betweenness)

    tqdm.write("Finished it! Sorting data")
    return list(sorted(c) for c in next(centrality))


def run_greedy(G: nx.Graph):
    tqdm.write("Running greedy method")
    centrality = community.greedy_modularity_communities(G)

    tqdm.write("Finished it! Sorting data")
    return list(sorted(c) for c in list(centrality))


def save_communities(G, communities, filename: str, extra_filename: str = ""):
    write_filename = SAVE_FOLDER + filename.split("/")[-1] + ".{}_{}.json".format("communities", extra_filename)

    with open(write_filename, "w") as f:
        tqdm.write("Saving it")

        com_dict = {
            "communities_length": len(communities),
            "communities": communities,
            "each_community_length": [len(c) for c in communities],
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
        }
        json.dump(com_dict, f)

        tqdm.write("Done!\n\n")


@click.command()
@click.argument("path", type=click.Path(exists=True))
def find_community(path):
    """
    PATH is either a .gml file which we want to find the communities
    or a path where we want to do it in all the files contained by it
    """

    for filename in tqdm(glob(path)):
        tqdm.write("Reading {}".format(filename))
        G = nx.read_gml(filename)

        communities = run_girvan_newman(G)
        save_communities(G, communities, filename, "girvan_newman")

        communities = run_greedy(G)
        save_communities(G, communities, filename, "greedy")


if __name__ == "__main__":
    find_community()
