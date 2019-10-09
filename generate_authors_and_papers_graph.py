# Core imports
import string
import re
import json
import math
import itertools
from pprint import pprint as pp
from unidecode import unidecode

# Library imports
import networkx as nx
from tqdm import tqdm, trange
import fire


# Constants
DATASET_SIZE = 4_107_340
CONFERENCE_IDS = ['1184914352', '1127325140', '1203999783']
CONFERENCE_NAME = 'AAAI-NIPS-IJCAI'
GML_BASE_PATH = './GML/'
MIN_YEAR = 1890
MAX_YEAR = 2020
GRAPH_TYPE = 'auth_paper'


# "Enums" for nodes/edges types
PAPER_NODE = 'paper'
AUTHOR_NODE = 'author'
AUTHORSHIP_EDGE = 'authorship'
CITATION_EDGE = 'citation'


def get_data(dictionary):
    '''Given a dictionary, parse the necessary data contained in it'''
    return {
        'id': dictionary.get('id', 0),
        'title': dictionary.get('title', ''),
        'year': int(dictionary.get('year', 0)),
        'authors': dictionary.get('authors', []),
        'references': dictionary.get('references', []),
    }


def read_from_dblp(dblp_filename: str,
                   papers_filename: str,
                   save_from_dblp: bool = False):
    """
        Fetch DBLP data and parse it properly
    """

    conference_papers = {}

    with open('./dblp_arnet/{}'.format(dblp_filename), 'r') as f:
        for line in tqdm(f, total=DATASET_SIZE):
            parsed_paper = json.loads(line)
            try:
                if parsed_paper['venue']['id'] in CONFERENCE_IDS:
                    # If doesn't have year in the dictionary
                    if parsed_paper['year'] not in conference_papers:
                        conference_papers[parsed_paper['year']] = []

                    conference_papers[parsed_paper['year']].append(
                        get_data(parsed_paper))

            except KeyError as e:
                pass
    if save_from_dblp:
        with open('./dblp_arnet/{}'.format(papers_filename), 'w') as f:
            json.dump(conference_papers, f)

    return conference_papers


def save_gml(G, graph_filename):
    """ Save a Graph G to a file in the `.gml` format """

    nx.write_gml(G, GML_BASE_PATH +
                 '{}_{}_{}'.format(CONFERENCE_NAME, GRAPH_TYPE, graph_filename))
    print("Saved graph to .gml file")


def save_yearly_gml(G, year, graph_filename):
    """
        Save a Graph G, related to a given `year`,
        to a file in the `.gml` format
    """

    gml_filename = GML_BASE_PATH + \
        '{}_{}_{}_{}'.format(
            CONFERENCE_NAME, year, GRAPH_TYPE, graph_filename)
    nx.write_gml(G, gml_filename)

    print("Saved graph to .gml file")


def generate_graph(should_save_gml: bool = False,
                   should_save_yearly_gml: bool = False,
                   should_read_from_dblp: bool = False,
                   should_save_from_dblp: bool = False,
                   should_generate_graph: bool = False,
                   plot_save_path: str = 'plot.png',
                   graph_filename: str = 'graph.gml',
                   dblp_filename: str = 'dblp_papers_v11.txt',
                   papers_filename: str = 'papers.json'):
    '''Function to generate the recommender systems graph

        Arguments:

            should_save_gml (bool): Save the final graph generated to a GML
                file, named by `graph_file`, prepended with the year

            should_save_yearly_gml (bool): Save the graph generated in each
                year timestep to a GML file

            should_read_from_dblp (bool): Read the graph from the dblp json
                file. If false, reads the GML from `graph_file`

            should_generate_graph (bool): If True, generates a graph from the
                conferences read if `read_from_dblp` was True

            plot_save_path (:obj:`str`): File to plot the chart generated
                interactively inside `save_yearly_gml`

            graph_filename (:obj:`str`): GML filename which is read and/or
                saved the graph to
    '''

    G = nx.DiGraph()

    # Read file adding to array
    if should_read_from_dblp:
        conference_papers = read_from_dblp(
            dblp_filename, papers_filename, should_save_from_dblp)
    else:
        with open('./dblp_arnet/{}'.format(papers_filename), 'r') as f:
            conference_papers = json.load(f)

    # Store older_papers in a dict
    older_papers = {}

    # Iterate through all the dataset years
    for year in range(MIN_YEAR, MAX_YEAR):

        if should_generate_graph and should_read_from_dblp:
            print("Parsing year {}".format(str(year)))

            # Add papers and authors to be referenced later
            for paper in conference_papers.get(year, []):
                older_papers[paper['id']] = [
                    author for author in paper['authors']]

            # Only after we can link them to one another
            # that's why we iterate twice
            for paper in conference_papers.get(year, []):
                # Adiciona nodos dos papers
                G.add_node(paper['id'], name=paper['title'], type=PAPER_NODE)

                # Adiciona/atualiza nodos dos autores,
                # adicionando arestas para o nodo do paper também
                for author in paper['authors']:
                    G.add_node(author['id'], name=author.get(
                        'name', ''), type=AUTHOR_NODE)

                    if paper['id'] in older_papers:
                        G.add_edge(author['id'], paper['id'],
                                   type=AUTHORSHIP_EDGE)

                # Adiciona arestas de citação
                for citation_id in paper['references']:
                    if citation_id in older_papers:
                        G.add_edge(paper['id'], citation_id,
                                   type=CITATION_EDGE)

            print("Current Graph size: {} nodes and {} edges".format(
                G.number_of_nodes(), G.number_of_edges()))
        else:
            gml_filename = GML_BASE_PATH + \
                '{}_{}_{}_{}'.format(
                    CONFERENCE_NAME, year, GRAPH_TYPE, graph_filename)
            print("Reading graph from GML file {}".format(gml_filename))
            try:
                G = nx.read_gml(gml_filename)
                print("Finished reading graph from GML file")
            except FileNotFoundError:
                G = nx.DiGraph()
                print("Generating empty graph, as there is no file")

        # Saving graph to .gml file
        if should_save_yearly_gml and G.number_of_nodes() > 0:
            save_yearly_gml(G, year, graph_filename)

    if should_generate_graph and should_read_from_dblp:
        print("Finished creating the graph")
        print("Graph size: {} nodes and {} edges".format(
            G.number_of_nodes(), G.number_of_edges()))

    # Save graph to .gml
    if should_save_gml:
        save_gml(G, graph_filename)


if __name__ == "__main__":
    fire.Fire(generate_graph)

# Centralidades
# Mais centrais a cada
# Community detection
# Self-citing (most/least self-citing community)
# Areas cooperação
# Paises
# Cooperação China/EUA -> Evolução
