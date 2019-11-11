# Main class import
from generate_graph import GenerateGraph

# Core imports
import json
import os
from pprint import pprint as pp

# Library imports
import networkx as nx
import fire

# Constants
CONFERENCE_IDS = ['1184914352', '1127325140', '1203999783']
CONFERENCE_NAME = 'AAAI-NIPS-IJCAI'
GRAPH_TYPE = 'countries_citation'


USA_ENUM = ['ak', 'alaska', 'al', 'alabama', 'ar', 'arkansas', 'az', 'arizona',
            'ca', 'california', 'co', 'colorado', 'ct', 'connecticut', 'de',
            'delaware', 'fl', 'florida', 'ga', 'georgia', 'hi', 'hawaii', 'ia',
            'iowa', 'id', 'idaho', 'il', 'illinois', 'in', 'indiana', 'ks',
            'kansas', 'ky', 'kentucky', 'la', 'louisiana', 'ma',
            'massachusetts', 'md', 'maryland', 'me', 'maine', 'mi', 'michigan',
            'mn', 'minnesota', 'mo', 'missouri', 'ms', 'mississippi', 'mt',
            'montana', 'nv', 'nevada', 'nc', 'north carolina', 'nd',
            'north dakota', 'ne', 'nebraska', 'nh', 'new hampshire', 'nj',
            'new jersey', 'nm', 'new mexico', 'nv', 'nevada', 'ny', 'new york',
            'oh', 'ohio', 'ok', 'oklahoma', 'or', 'oregon', 'pa',
            'pennsylvania', 'ri', 'rhode island', 'sc', 'south carolina', 'sd',
            'south dakota', 'tn', 'tennessee', 'tx', 'texas', 'ut', 'utah', 'vt',
            'vermont', 'va', 'virginia', 'wa', 'washington', 'wi', 'wisconsin',
            'wv', 'west virginia', 'wy', 'wyoming', 'dc', 'columbia']


def infer_country_from(organization: str):
    country = organization.split(', ')[-1][:-5].replace('.', '').lower()
    country = country if '#TAB#' in organization else None

    return country if country not in USA_ENUM else 'USA'


class CountryCitationGraph(GenerateGraph):

    def __init__(self, *args, **kwargs):
        # Configure to current directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super().__init__(*args, **kwargs)

    def generate(self,
                 save_gml: bool = True,
                 save_yearly_gml: bool = False,
                 save_non_cummulated_yearly_gml: bool = False,
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

                save_gml (bool): Save the final graph generated to a GML
                    file, named by `self.graph_file`

                save_yearly_gml (bool): Save the graph generated in each
                    year timestep to a GML file

                read_from_dblp (bool): Read the graph from the dblp json
                    file. If false, reads from the `self.conference_name` json

                save_from_dblp (bool): Saves the parsed papers to a json
                    file.

                read_saved_from_dblp (bool): Read the conference_papers dict
                    from a json file, saved previously with `save_from_dblp`.

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
            if save_non_cummulated_yearly_gml:
                self.yearly_G = nx.DiGraph()

            if generate_graph and read_from_dblp:
                print(f"Parsing year {str(year)}")

                # Add papers and authors to be referenced later
                for paper in conference_papers.get(year, []):
                    older_papers[paper['id']] = [
                        author for author in paper['authors']]

                for paper in conference_papers.get(year, []):
                    # Adiciona/atualiza nodos dos países
                    for author in paper['authors']:
                        country = infer_country_from(author.get('org', ''))
                        if country is not None:
                            self.G.add_node(country)

                            if save_non_cummulated_yearly_gml:
                                self.yearly_G.add_node(country)

                    # Adiciona arestas
                    for citation_id in paper['references']:
                        # Other paper authors
                        if citation_id in older_papers:
                            for other_author in older_papers[citation_id]:
                                for author in paper['authors']:
                                    # Fetch countries
                                    country = infer_country_from(
                                        author.get('org', ''))
                                    other_country = infer_country_from(
                                        other_author.get('org', ''))

                                    # Add edge
                                    if country is not None and \
                                            other_country is not None:
                                        self.G.add_edge(country, other_country)

                                        if save_non_cummulated_yearly_gml:
                                            self.yearly_G.add_edge(
                                                country, other_country)

                self.print_graph_info()
            else:
                self.G = self.read_from_gml(year)

            # Saving graph to .gml file
            if save_yearly_gml and self.G.number_of_nodes() > 0:
                # Compute centralities for each year
                self.compute_centralities(degree=compute_degree,
                                          betweenness=compute_betweenness,
                                          closeness=compute_closeness,
                                          pagerank=compute_pagerank)

                super().save_yearly_gml(year)

                if save_non_cummulated_yearly_gml:
                    # Compute centralities for each year
                    self.compute_centralities(degree=compute_degree,
                                              betweenness=compute_betweenness,
                                              closeness=compute_closeness,
                                              pagerank=compute_pagerank,
                                              G=self.yearly_G)

                    super().save_yearly_gml(year,
                                            G=self.yearly_G,
                                            graph_name='yearly_' + self.graph_name)

        if generate_graph and read_from_dblp:
            print("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gml
        if generate_graph and save_gml:
            super().save_gml()


if __name__ == "__main__":
    graphGeneration = CountryCitationGraph(
        graph_name=GRAPH_TYPE,
        conference_name=CONFERENCE_NAME,
        conference_ids=CONFERENCE_IDS)

    fire.Fire(graphGeneration.generate)
