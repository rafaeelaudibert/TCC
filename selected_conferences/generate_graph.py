# Imports
import json
from typing import List

import fire
import networkx as nx
from tqdm import tqdm, trange

# Generic constants
CONFERENCE_IDS = ['1184914352', '1127325140', '1203999783']
CONFERENCE_NAME = 'AAAI-NIPS-IJCAI'


class GenerateGraph:
    DATASET_SIZE = 4_107_340
    GML_BASE_PATH = '../GML/'
    DBLP_FILENAME = 'dblp_papers_v11.txt'

    def __init__(self,
                 graph_name: str = '',
                 conference_name: str = '',
                 conference_ids: List[int] = None,
                 min_year: int = 1890,
                 max_year: int = 2020):

        self.graph_name = graph_name
        self.conference_name = conference_name
        self.conference_ids = conference_ids
        self.min_year = min_year
        self.max_year = max_year

        self.G = nx.Graph()  # placeholder

    def generate(self, **kwargs):
        raise NotImplementedError("You must implement this method")

    @staticmethod
    def get_data(dictionary: dict = {}) -> dict:
        '''Given a dictionary, parse the necessary data contained in it'''
        return {
            'id': dictionary.get('id', 0),
            'title': dictionary.get('title', ''),
            'year': int(dictionary.get('year', 0)),
            'authors': dictionary.get('authors', []),
            'references': dictionary.get('references', []),
        }

    def print_graph_info(self) -> None:
        print(f"Graph size: {self.G.number_of_nodes()} nodes \
                and {self.G.number_of_edges()} edges")

    def save_gml(self) -> None:
        """ Save a Graph G to a file in the `.gml` format """

        gml_filename = self.GML_BASE_PATH + \
            '{}_{}_graph.gml'.format(self.graph_name,
                                     self.conference_name)
        nx.write_gml(self.G, gml_filename)

        print(f"Saved graph to {gml_filename} file")

    def save_yearly_gml(self, year: int) -> None:
        """
            Save a Graph G, related to a given `year`,
            to a file in the `.gml` format
        """

        gml_filename = self.GML_BASE_PATH + \
            '{}_{}_{}_graph.gml'.format(
                self.graph_name, self.conference_name, year)
        nx.write_gml(self.G, gml_filename)

        print(f"Saved graph to {gml_filename} file")

    def read_from_dblp(self, save_from_dblp: bool = False) -> dict:
        """
            Fetch DBLP data and parse it properly
        """

        conference_papers = {}

        with open('../dblp_arnet/{}'.format(self.DBLP_FILENAME), 'r') as f:
            for line in tqdm(f, total=self.DATASET_SIZE):
                parsed_paper = json.loads(line)
                try:
                    if self.conference_ids is None or \
                            parsed_paper['venue']['id'] in self.conference_ids:
                        # If doesn't have year in the dictionary
                        if parsed_paper['year'] not in conference_papers:
                            conference_papers[parsed_paper['year']] = []

                        conference_papers[parsed_paper['year']].append(
                            GenerateGraph.get_data(parsed_paper))

                except KeyError as e:
                    pass

        if save_from_dblp:
            json_filename = '../dblp_arnet/{}_{}.json'.format(
                self.conference_name, self.graph_name)
            with open(json_filename, 'w') as f:
                json.dump(conference_papers, f)

        return conference_papers

    def read_from_json(self) -> dict:
        json_filename = '../dblp_arnet/{}_{}.json'.format(
            self.conference_name, self.graph_name)
        with open(json_filename, 'r') as f:
            conference_papers = json.load(f)

        return conference_papers

    def read_from_gml(self, year: int) -> nx.DiGraph():
        gml_filename = self.GML_BASE_PATH + '{}_{}_{}_graph.gml'.format(
            self.conference_name, year, self.graph_name)
        print(f"Reading graph from GML file {gml_filename}")

        try:
            self.G = nx.read_gml(gml_filename)
            print("Finished reading graph from GML file")
        except FileNotFoundError:
            self.G = nx.DiGraph()
            print("Generating empty graph, as there is no file")


def generate_graph(run_authors_and_papers_graph: bool = False,
                   run_collaboration_graph: bool = False,
                   run_citation_graph: bool = False,
                   run_authors_citation_graph: bool = False,
                   **kwargs: dict) -> None:
    """
        Run the required authors generation
    """
    if run_authors_and_papers_graph:
        from generate_authors_and_papers_graph import AuthorPaperGraph  # nopep8
        graphGeneration = AuthorPaperGraph(
            graph_name='author_paper',
            conference_name=CONFERENCE_NAME,
            conference_ids=CONFERENCE_IDS)

        print("Starting AuthorPaperGraph generation")
        graphGeneration.generate(**kwargs)

    if run_collaboration_graph:
        from generate_collaboration_graph import CollaborationGraph
        graphGeneration = CollaborationGraph(
            graph_name='collaboration',
            conference_name=CONFERENCE_NAME,
            conference_ids=CONFERENCE_IDS)

        print("Starting CollaborationGraph generation")
        graphGeneration.generate(**kwargs)

    if run_citation_graph:
        from generate_citation_graph import CitationGraph
        graphGeneration = CitationGraph(
            graph_name='citation',
            conference_name=CONFERENCE_NAME,
            conference_ids=CONFERENCE_IDS)

        print("Starting CitationGraph generation")
        graphGeneration.generate(**kwargs)

    if run_authors_citation_graph:
        from generate_authors_citation_graph import AuthorsCitationGraph
        graphGeneration = AuthorsCitationGraph(
            graph_name='authors_citation',
            conference_name=CONFERENCE_NAME,
            conference_ids=CONFERENCE_IDS)

        print("Starting AuthorsCitationGraph generation")
        graphGeneration.generate(**kwargs)


if __name__ == "__main__":
    fire.Fire(generate_graph)
