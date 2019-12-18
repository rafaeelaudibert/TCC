# Core imports
import json
import os
from glob import glob
from collections import Counter

# Library imports
import networkx as nx
import fire
from tqdm import tqdm

SAVE_FOLDER = './loop_counts/'


def save_counts(filename, counts):
    write_filename = SAVE_FOLDER + \
        filename.split('/')[-1] + ".loops_count.json"

    with open(write_filename, 'w') as f:
        tqdm.write('Saving it')
        json.dump(counts, f)

        tqdm.write('Done!\n\n')


def find_loop_count(search_path: str):
    """
        path: str = Name of a gpickle file which we want to sort
            by their features or a path where we want to do it
            in all the files contained by it
    """

    for filename in tqdm(glob(search_path)):
        tqdm.write("Reading {}".format(filename))
        G = nx.read_gpickle(filename)

        tqdm.write("Counting (and sorting) self cites")
        loop_counts = Counter([edge[0]
                               for edge in G.edges() if edge[0] == edge[1]])
        ordered_loop_counts = sorted(
            dict(loop_counts).items(), key=lambda x: (-x[1], x[0]))

        save_counts(filename, ordered_loop_counts)


if __name__ == "__main__":
    fire.Fire(find_loop_count)
