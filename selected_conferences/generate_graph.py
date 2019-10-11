# Imports
import json
import networkx as nx
from tqdm import tqdm, trange


class GenerateGraph:
    DATASET_SIZE = 4_107_340
    GML_BASE_PATH = '../GML/'
    DBLP_FILENAME = 'dblp_papers_v11.txt'

    def __init__(self,
                 graph_name='',
                 conference_name='',
                 conference_ids=None,
                 min_year=1890,
                 max_year=2020):

        self.graph_name = graph_name
        self.conference_name = conference_name
        self.conference_ids = conference_ids
        self.min_year = min_year
        self.max_year = max_year

        self.G = nx.Graph()  # placeholder

    def generate(self, **kwargs):
        raise NotImplementedError("You must implement this method")

    @staticmethod
    def get_data(dictionary):
        '''Given a dictionary, parse the necessary data contained in it'''
        return {
            'id': dictionary.get('id', 0),
            'title': dictionary.get('title', ''),
            'year': int(dictionary.get('year', 0)),
            'authors': dictionary.get('authors', []),
            'references': dictionary.get('references', []),
        }

    def print_graph_info(self):
        print(f"Graph size: {self.G.number_of_nodes()} nodes \
                and {self.G.number_of_edges()} edges")

    def save_gml(self):
        """ Save a Graph G to a file in the `.gml` format """

        nx.write_gml(self.G, self.GML_BASE_PATH +
                     '{}_{}_graph.gml'.format(self.graph_name,
                                              self.conference_name))
        print("Saved graph to .gml file")

    def save_yearly_gml(self, year):
        """
            Save a Graph G, related to a given `year`,
            to a file in the `.gml` format
        """

        gml_filename = self.GML_BASE_PATH + \
            '{}_{}_{}_graph.gml'.format(
                self.graph_name, self.conference_name, year)
        nx.write_gml(self.G, gml_filename)

        print("Saved graph to .gml file")

    def read_from_dblp(self, save_from_dblp: bool = False):
        """
            Fetch DBLP data and parse it properly
        """

        conference_papers = {}

        with open('../dblp_arnet/{}'.format(self.DBLP_FILENAME), 'r') as f:
            for line in tqdm(f, total=self.DATASET_SIZE):
                parsed_paper = json.loads(line)
                try:
                    if parsed_paper['venue']['id'] in self.conference_ids:
                        # If doesn't have year in the dictionary
                        if parsed_paper['year'] not in conference_papers:
                            conference_papers[parsed_paper['year']] = []

                        conference_papers[parsed_paper['year']].append(
                            super().get_data(parsed_paper))

                except KeyError as e:
                    pass

        if save_from_dblp:
            with open(f'../dblp_arnet/{self.conference_name}.json', 'w') as f:
                json.dump(conference_papers, f)

        return conference_papers


if __name__ == "__main__":
    raise NotImplementedError(
        "This is an abstract class. You must call its inherited classes")
