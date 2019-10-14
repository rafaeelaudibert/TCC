# Main class import
from generate_graph import GenerateGraph

# Core imports
import json
import os

# Library imports
import networkx as nx
import fire

# Constants
CONFERENCE_IDS = ['1184914352', '1127325140', '1203999783']
CONFERENCE_NAME = 'AAAI-NIPS-IJCAI'
GRAPH_TYPE = 'collaboration'


class CollaborationGraph(GenerateGraph):

    def generate(self,
                 should_save_gml: bool = True,
                 should_save_yearly_gml: bool = False,
                 should_read_from_dblp: bool = True,
                 should_save_from_dblp: bool = False,
                 should_generate_graph: bool = True):
        '''Function to generate the recommender systems graph

            Arguments:

                should_save_gml (bool): Save the final graph generated to a GML
                    file, named by `self.graph_file`

                should_save_yearly_gml (bool): Save the graph generated in each
                    year timestep to a GML file

                should_read_from_dblp (bool): Read the graph from the dblp json
                    file. If false, reads from the `self.conference_name` json

                should_save_from_dblp (bool): Saves the parsed papers to a json
                    file.

                should_generate_graph (bool): Generates the authors_and_papers
                    graph from the  articles read
        '''

        self.G = nx.DiGraph()

        # Read file adding to array
        if should_read_from_dblp:
            conference_papers = self.read_from_dblp(should_save_from_dblp)
        else:
            with open(f'../dblp_arnet/{self.conference_name}.json', 'r') as f:
                conference_papers = json.load(f)

        # Store older_papers in a dict
        older_papers = {}

        # Iterate through all the dataset years
        for year in range(self.min_year, self.max_year):

            if should_generate_graph and should_read_from_dblp:
                print(f"Parsing year {str(year)}")

                for paper in conference_papers.get(year, []):
                    # First create the nodes
                    for author in paper['authors']:
                        self.G.add_node(
                            author['id'], name=author.get('name', ''))

                    # Add the edges
                    for author_main in paper['authors']:
                        for author_collaborator in paper['authors']:
                            if author_main != author_collaborator:
                                self.G.add_edge(author_main['id'],
                                                author_collaborator['id'],
                                                name=paper.get('title', ''))

                self.print_graph_info()
            else:
                gml_filename = self.GML_BASE_PATH + \
                    '{}_{}_{}_graph.gml'.format(
                        self.conference_name, year, self.graph_name)
                print(f"Reading graph from GML file {gml_filename}")

                try:
                    self.G = nx.read_gml(gml_filename)
                    print("Finished reading graph from GML file")
                except FileNotFoundError:
                    self.G = nx.DiGraph()
                    print("Generating empty graph, as there is no file")

            # Saving graph to .gml file
            if should_save_yearly_gml and G.number_of_nodes() > 0:
                super().save_yearly_gml(year)

        if should_generate_graph and should_read_from_dblp:
            print("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gml
        if should_generate_graph and should_save_gml:
            super().save_gml()


if __name__ == "__main__":
    # Configure to current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    graphGeneration = CollaborationGraph(
        graph_name=GRAPH_TYPE,
        conference_name=CONFERENCE_NAME,
        conference_ids=CONFERENCE_IDS)

    fire.Fire(graphGeneration.generate)
