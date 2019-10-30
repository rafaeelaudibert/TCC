# Core imports
import json
import os

# Library imports
import networkx as nx
import fire

SAVE_FOLDER = './sorted_data/'


def sort_and_save(data, filename: str, key: str):
    write_filename = SAVE_FOLDER + \
        filename.split('/')[0] + ".{}.json".format(key)

    with open(write_filename, 'w') as f:
        print('Sorting by {}'.format(key))
        sorted_data = sorted(data, key=lambda id, data: data[key])
        print('Saving it')
        json.dump(sorted_data, f)
        print('Saved!')


def find_central(filename: str):
    G = nx.read_gml(filename)

    data = list(G.nodes(data=True))

    sort_and_save(data, filename, 'degree')
    sort_and_save(data, filename, 'indegree')
    sort_and_save(data, filename, 'outdegree')
    sort_and_save(data, filename, 'closeness')
    sort_and_save(data, filename, 'betweenness')
    sort_and_save(data, filename, 'pagerank')


if __name__ == "__main__":
    fire.Fire(find_central)
