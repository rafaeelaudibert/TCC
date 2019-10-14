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
GRAPH_TYPE = 'authors_citation'


class AuthorsCitationGraph(GenerateGraph):

    def __init__(self, *args, **kwargs):
        # Configure to current directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super().__init__(*args, **kwargs)

    def generate(self,
                 should_save_gml: bool = True,
                 should_save_yearly_gml: bool = False,
                 should_read_from_dblp: bool = True,
                 should_save_from_dblp: bool = False,
                 should_generate_graph: bool = True) -> None:
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
            conference_papers = self.read_from_json()

        # Store older_papers in an arrray
        older_papers = {}

        # Iterate through all the dataset years
        for year in range(self.min_year, self.max_year):

            if should_generate_graph and should_read_from_dblp:
                print(f"Parsing year {str(year)}")

                # Add papers and authors to be referenced later
                for paper in conference_papers.get(year, []):
                    older_papers[paper['id']] = [
                        author for author in paper['authors']]

                for paper in conference_papers.get(year, []):
                    # Adiciona/atualiza nodos dos autores
                    for author in paper['authors']:
                        self.G.add_node(
                            author['id'], name=author.get('name', ''))

                    # Adiciona arestas
                    for citation_id in paper['references']:
                        # Other paper authors
                        if citation_id in older_papers:
                            for other_author in older_papers[citation_id]:
                                for author in paper['authors']:
                                    # This paper authors
                                    self.G.add_edge(
                                        author['id'], other_author['id'])

                self.print_graph_info()
            else:
                self.G = self.read_from_gml(year)

            # Saving graph to .gml file
            if should_save_yearly_gml and self.G.number_of_nodes() > 0:
                super().save_yearly_gml(year)

        if should_generate_graph and should_read_from_dblp:
            print("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gml
        if should_generate_graph and should_save_gml:
            super().save_gml()


if __name__ == "__main__":
    graphGeneration = AuthorsCitationGraph(
        graph_name=GRAPH_TYPE,
        conference_name=CONFERENCE_NAME,
        conference_ids=CONFERENCE_IDS)

    fire.Fire(graphGeneration.generate)
