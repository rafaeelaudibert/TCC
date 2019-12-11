import networkx as nx
from glob import glob
from tqdm import tqdm
import fire
import os


def convert(path: str, remove: bool = False):
    for filename in tqdm(glob(path)):
        if '.gml' in filename:
            tqdm.write('Parsing {}'.format(filename))
            G = nx.read_gml(filename)
            nx.write_gpickle(G, filename.replace('gml', 'gpickle'))

            # Remove the original .gml
            if remove:
                os.remove(filename)


if __name__ == "__main__":
    fire.Fire(convert)
