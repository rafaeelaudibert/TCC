import networkx as nx
from glob import glob
from tqdm import tqdm
import click
import os


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--remove", "-r", is_flag=True, help="If we should or not remove the original .gml file")
def convert(path: str, remove: bool):
    """
    Looks for .gml files in PATH to convert them to .gpickle files
    """
    for filename in tqdm(glob(path)):
        if ".gml" in filename:
            tqdm.write("Parsing {}".format(filename))
            G = nx.read_gml(filename)
            nx.write_gpickle(G, filename.replace("gml", "gpickle"))

            # Remove the original .gml
            if remove:
                os.remove(filename)


if __name__ == "__main__":
    convert()
