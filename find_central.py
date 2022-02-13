# Core imports
import json
from glob import glob

# Library imports
import networkx as nx
import click
from tqdm import tqdm

SAVE_FOLDER = "./sorted_data/"


def sort_and_save(data, filename: str, key: str):
    write_filename = SAVE_FOLDER + filename.split("/")[-1] + ".{}.json".format(key)

    with open(write_filename, "w") as f:
        tqdm.write("Sorting by {}".format(key))
        sorted_data = sorted(data, key=lambda data: data[1].get(key, ""), reverse=True)
        tqdm.write("Saving it")
        json.dump(sorted_data, f)
        tqdm.write("Done!")


@click.command()
@click.argument("path", type=click.Path(exists=True))
def find_central(path):
    """
    PATH is a .gpickle file that we want to sort
    by their features or a path where we want to do it
    in all the files contained by it
    """

    for filename in tqdm(glob(path)):

        tqdm.write("Reading {}".format(filename))
        data = list(nx.read_gpickle(filename).nodes(data=True))

        sort_and_save(data, filename, "degree")
        sort_and_save(data, filename, "indegree")
        sort_and_save(data, filename, "outdegree")
        sort_and_save(data, filename, "closeness")
        sort_and_save(data, filename, "betweenness")
        sort_and_save(data, filename, "pagerank")


if __name__ == "__main__":
    find_central()
