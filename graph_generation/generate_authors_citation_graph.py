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
                 save_gpickle: bool = True,
                 save_yearly_gpickle: bool = False,
                 save_non_cummulated_yearly_gpickle: bool = False,
                 read_from_dblp: bool = True,
                 save_from_dblp: bool = False,
                 read_saved_from_dblp: bool = False,
                 generate_graph: bool = True,
                 compute_degree: bool = True,
                 compute_closeness: bool = True,
                 compute_betweenness: bool = True,
                 compute_pagerank: bool = True) -> None:
        '''Function to generate the recommender systems graph

            Arguments:

                save_gpickle (bool): Save the final graph generated to a GML
                    file, named by `self.graph_file`

                save_yearly_gpickle (bool): Save the graph generated in each
                    year timestep to a GML file

                read_from_dblp (bool): Read the graph from the dblp json
                    file. If false, reads from the `self.conference_name` json

                save_from_dblp (bool): Saves the parsed papers to a json
                    file.

                generate_graph (bool): Generates the authors_and_papers
                    graph from the  articles read
        '''

        self.G = nx.MultiDiGraph()
        self.yearly_G = nx.MultiDiGraph()

        # Read file adding to array
        if read_from_dblp:
            conference_papers = self.read_from_dblp(
                read_saved_from_dblp, save_from_dblp)
        else:
            conference_papers = self.read_from_json()

        # Store older_papers in an arrray
        older_papers = {}

        # Iterate through all the dataset years
        for year in range(self.min_year, self.max_year):

            # Reset yearly graph
            if save_non_cummulated_yearly_gpickle:
                self.yearly_G = nx.DiGraph()

            if generate_graph and read_from_dblp:
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

                        if save_non_cummulated_yearly_gpickle:
                            self.yearly_G.add_node(
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

                                    if save_non_cummulated_yearly_gpickle:
                                        self.yearly_G.add_edge(
                                            author['id'], other_author['id'])

                self.print_graph_info()
            else:
                self.G = self.read_from_gpickle(year)

            # Saving graph to .gpickle file
            if save_yearly_gpickle and self.G.number_of_nodes() > 0:
                # Compute centralities for each year
                self.compute_centralities(degree=compute_degree,
                                          betweenness=compute_betweenness,
                                          closeness=compute_closeness,
                                          pagerank=compute_pagerank)

                super().save_yearly_gpickle(year)

                if save_non_cummulated_yearly_gpickle:
                    # Compute centralities for each year
                    self.compute_centralities(degree=compute_degree,
                                              betweenness=compute_betweenness,
                                              closeness=compute_closeness,
                                              pagerank=compute_pagerank,
                                              G=self.yearly_G)

                    super().save_yearly_gpickle(year,
                                                G=self.yearly_G,
                                                graph_name='yearly_' + self.graph_name)

        if generate_graph and read_from_dblp:
            print("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gpickle
        if generate_graph and save_gpickle:
            super().save_gpickle()


if __name__ == "__main__":
    graphGeneration = AuthorsCitationGraph(
        graph_name=GRAPH_TYPE,
        conference_name=CONFERENCE_NAME,
        conference_ids=CONFERENCE_IDS)

    fire.Fire(graphGeneration.generate)
