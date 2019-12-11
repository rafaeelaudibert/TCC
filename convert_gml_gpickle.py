import networkx as nx
from glob import glob
from tqdm import tqdm

for filename in tqdm(glob('./GML/*.gml')):
    tqdm.write('Parsing {}'.format(filename))
    G = nx.read_gml(filename)
    nx.write_gpickle(G, filename.replace('gml', 'gpickle'))
