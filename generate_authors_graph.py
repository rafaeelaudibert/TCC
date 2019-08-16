# Core imports
import json
import math
from pprint import pprint as pp

# Library imports
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from tqdm import tqdm, trange
import fire

# Constants
DATASET_SIZE = 4_107_340
CONFERENCE_IDS = ['1184914352', '1127325140', '1203999783']
CONFERENCE_NAME = 'AAAI-NIPS-IJCAI'
AUTHOR_IDS = [('563069026', 'Hinton'), ('161269817', 'Bengio'),
              ('2053214915', 'LeCun')]
AUTHOR_COLOR = "#eb3dce"
PAPER_COLOR = "#57def2"
COLOR_PALETTE = [
    ('#FECEE9', '#EFA0CD', '#FF66BC', '#4F032E', "#0F0008"),
    ('#D4E4BC', '#AAB796', '#6B8E36', '#576D36', '#384722'),
    ('#BAD3E0', '#5FA7CE', '#2DB5FF', '#0091E0', '#275B77'),
    ('#F9EDEE', '#DBA6AB', '#E63946', '#9E454C', '#561C21'),
]
TURING_AWARD_YEAR = 2018
DATASET_BASE_PATH = './dblp_arnet/'


def get_data(dictionary):
    '''
        Given a dictionary, parse the necessary data contained in it
    '''
    return {
        'id': dictionary.get('id', 0),
        'title': dictionary.get('title', ''),
        'year': int(dictionary.get('year', 0)),
        'authors': dictionary.get('authors', []),
        'references': dictionary.get('references', []),
    }

def main(save_adj: bool = False, save_conf: bool = False, figure_save_path: str = "graph.svg", save_gml: bool = False, plot_to_files: bool = False):
    G = nx.DiGraph()
    conference_papers = {}

    # Read file adding to array
            for line in tqdm(f, total=DATASET_SIZE):
            parsed_json = json.loads(line)
            try:
                    if parsed_json['venue']['id'] in CONFERENCE_IDS:
                    # If doesn't have year in the dictionary
                    if parsed_json['year'] not in conference_papers:
                        conference_papers[int(parsed_json['year'])] = []

                    conference_papers[int(parsed_json['year'])].append(get_data(parsed_json))
            except KeyError as e:
                pass

    older_papers = {}
    for year in sorted(conference_papers.keys()):

        # Add papers and authors to be referenced
        for paper in conference_papers[year]:
            older_papers[paper['id']] = [author for author in paper['authors']]

        print("I'm in year {}".format(str(year)))

        for paper in conference_papers[year]:
            
            # Adiciona/atualiza nodos dos autores
            for author in paper['authors']:          
                G.add_node(author['id'], name=author['name'] if 'name' in author else '')
            
            # Adiciona arestas
            for citation_id in paper['references']:
                if citation_id in older_papers:
                    for other_author in older_papers[citation_id]:  # Other paper authors
                        for author in paper['authors']:             # This paper authors
                            G.add_edge(author['id'], other_author['id'])
        print("Current Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))

        if plot_to_files:
            # Draw graph
            f = plt.figure()
            plt.title("Authors references graph until {}".format(str(year)))
            node_sizes = [degree + 1 for node, degree in list(G.in_degree())]
            nx.draw_spring(G, node_size=node_sizes, alpha=0.4, arrowsize=2, arrowstyle='- >')
            f.savefig(str(year) + "_authors_" + figure_save_path)
            # plt.show()
            plt.close()
            print("Saved figure for year {}".format(str(year)))

    print("Finished creating the graph")
    print("Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))        

    # Computing PageRank
    print('Generating PageRank')
    pr = nx.pagerank(G)
    nx.set_node_attributes(G, pr, 'pagerank')

    # Write graph data to file
    if save_adj:
        with open('./dblp_arnet/{}_graph.json'.format(CONFERENCE_NAME), 'w') as f:
            data = json_graph.adjacency_data(G)
            json.dump(data, f)
        print("Saved adjacency networkx matrix")

    if save_gml:    
        nx.write_gml(G, './dblp_arnet/{}_graph.gml'.format(CONFERENCE_NAME))
        print("Saved graph to .gml file")

    # Write json data to file
    if save_conf:
        with open('./dblp_arnet/{}.json'.format(CONFERENCE_NAME), 'w') as f:
            json.dump(conference_papers, f)
        print("Saved conference json")

if __name__ == "__main__":
    fire.Fire(main)
