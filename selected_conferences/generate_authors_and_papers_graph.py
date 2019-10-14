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
GRAPH_TYPE = 'author_paper'


class AuthorPaperGraph(GenerateGraph):
    # "Enums" for nodes/edges types
    PAPER_NODE = 'paper'
    AUTHOR_NODE = 'author'
    AUTHORSHIP_EDGE = 'authorship'
    CITATION_EDGE = 'citation'

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

        # Store older_papers in a dict
        older_papers = {}

        # Iterate through all the dataset years
        for year in range(self.min_year, self.max_year):

            if should_generate_graph and should_read_from_dblp:
                print(f"Parsing year {str(year)}")

                # Add papers and authors to be referenced later
                for paper in conference_papers.get(year, []):
                    older_papers[paper['id']] = [
                        author for author in paper['authors']]

                # Only after we can link them to one another
                # that's why we iterate twice
                for paper in conference_papers.get(year, []):
                    # Adiciona nodos dos papers
                    self.G.add_node(
                        paper['id'], name=paper['title'], type=self.PAPER_NODE)

                    # Adiciona/atualiza nodos dos autores,
                    # adicionando arestas para o nodo do paper também
                    for author in paper['authors']:
                        self.G.add_node(author['id'], name=author.get(
                            'name', ''), type=self.AUTHOR_NODE)

                        if paper['id'] in older_papers:
                            self.G.add_edge(author['id'], paper['id'],
                                            type=self.AUTHORSHIP_EDGE)

                    # Adiciona arestas de citação
                    for citation_id in paper['references']:
                        if citation_id in older_papers:
                            self.G.add_edge(paper['id'], citation_id,
                                            type=self.CITATION_EDGE)

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
    # Configure to current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    graphGeneration = AuthorPaperGraph(
        graph_name=GRAPH_TYPE,
        conference_name=CONFERENCE_NAME,
        conference_ids=CONFERENCE_IDS)

    fire.Fire(graphGeneration.generate)
