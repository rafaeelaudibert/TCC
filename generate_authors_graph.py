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


def generate_graph(save_records: bool = False,
                   save_gml: bool = False,
                   plot_graph_figure: bool = False,
                   read_from_dblp: bool = False,
                   generate_graph: bool = False,
                   figure_save_path: str = "graph.svg",
                   graph_file: str = 'graph.gml',
                   dblp_filename: str = 'dblp_papers_v11.txt'):
    G = nx.DiGraph()
    conference_papers = {}

    # Read file adding to array
    if read_from_dblp:
        with open('./dblp_arnet/{}'.format(dblp_filename), 'r') as f:
            for line in tqdm(f, total=DATASET_SIZE):
            parsed_json = json.loads(line)
            try:
                    if parsed_json['venue']['id'] in CONFERENCE_IDS:
                    # If doesn't have year in the dictionary
                    if parsed_json['year'] not in conference_papers:
                            conference_papers[parsed_json['year']] = []

                        conference_papers[parsed_json['year']].append(
                            get_data(parsed_json))
            except KeyError as e:
                pass

    older_papers = {}

    for year in range(1890, 2020):

        if generate_graph and read_from_dblp:
            print("Parsing year {}".format(str(year)))

            # Add papers and authors to be referenced later
            for paper in conference_papers.get(year, []):
                older_papers[paper['id']] = [
                    author for author in paper['authors']]
            
            for paper in conference_papers.get(year, []):
            # Adiciona/atualiza nodos dos autores
            for author in paper['authors']:          
                    G.add_node(author['id'],
                               name=author.get('name', ''),
                               count=G.node[author['id']].get('count', 0) + 1 if author['id'] in G.nodes() else 1)  # nopep8
            
            # Adiciona arestas
            for citation_id in paper['references']:
                if citation_id in older_papers:
                        # Other paper authors
                        for other_author in older_papers[citation_id]:
                            # This paper authors
                            for author in paper['authors']:
                            G.add_edge(author['id'], other_author['id'])

            print("Current Graph size: {} nodes and {} edges".format(
                G.number_of_nodes(), G.number_of_edges()))
        else:
            gml_filename = DATASET_BASE_PATH + \
                '{}_{}_{}'.format(CONFERENCE_NAME, year, graph_file)
            print("Reading graph from GML file {}".format(gml_filename))
            try:
                G = nx.read_gml(gml_filename)
                print("Finished reading graph from GML file")
            except FileNotFoundError:
                G = nx.DiGraph()
                print("Generating empty graph, as there is no file")

        if plot_graph_figure:
            # Draw graph
            f = plt.figure()
            plt.title("Authors references graph until {}".format(str(year)))
            node_sizes = [degree + 1 for node, degree in list(G.in_degree())]
            nx.draw_spring(G, node_size=node_sizes, alpha=0.4,
                           arrowsize=2, arrowstyle='- >')

            # Save graph
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

    # Save graph to .gml
    if save_gml:    
        nx.write_gml(G, DATASET_BASE_PATH +
                     '{}_{}'.format(CONFERENCE_NAME, graph_file))
        print("Saved graph to .gml file")

    # Write json data to file
    if save_records:
        with open('./dblp_arnet/{}.json'.format(CONFERENCE_NAME), 'w') as f:
            json.dump(conference_papers, f)
        print("Saved conference json")


if __name__ == "__main__":
    fire.Fire(generate_graph)
