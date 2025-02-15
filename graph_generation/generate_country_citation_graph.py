# Main class import
from collections import defaultdict
from itertools import count
from generate_graph import GenerateGraph

# Core imports
import json
import os
from pprint import pprint as pp
from tqdm import tqdm

# Library imports
import networkx as nx
import fire

# Constants
CONFERENCE_IDS = ["1184914352", "1127325140", "1203999783"]
CONFERENCE_NAME = "AAAI-NIPS-IJCAI"
GRAPH_TYPE = "countries_citation"

COUNTRY_REPLACEMENT = {}


def infer_country_from(organization: str):
    # Parse last name
    country = organization.split(",")[-1].replace(".", "").lower().strip()

    # Make country replacement
    if country in COUNTRY_REPLACEMENT.keys() and COUNTRY_REPLACEMENT[country] is not None:
        return (True, COUNTRY_REPLACEMENT[country])

    return (False, country)


class CountryCitationGraph(GenerateGraph):
    def __init__(self, *args, **kwargs):
        global COUNTRY_REPLACEMENT

        # Configure to current directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        with open("./country_replacement.json", "r") as f:
            COUNTRY_REPLACEMENT = json.load(f)

        super().__init__(*args, **kwargs)

    def generate(
        self,
        save_gpickle: bool = False,
        save_yearly_gpickle: bool = False,
        save_non_cummulated_yearly_gpickle: bool = False,
        read_from_dblp: bool = False,
        save_from_dblp: bool = False,
        read_saved_from_dblp: bool = False,
        generate_graph: bool = False,
        compute_degree: bool = False,
        compute_closeness: bool = False,
        compute_betweenness: bool = False,
        compute_pagerank: bool = False,
        generate_missing_countries: bool = False,
    ) -> None:
        """Function to generate the recommender systems graph

        Arguments:

            save_gpickle (bool): Save the final graph generated to a GML
                file, named by `self.graph_file`

            save_yearly_gpickle (bool): Save the graph generated in each
                year timestep to a GML file

            read_from_dblp (bool): Read the graph from the dblp json
                file. If false, reads from the `self.conference_name` json

            save_from_dblp (bool): Saves the parsed papers to a json
                file.

            read_saved_from_dblp (bool): Read the conference_papers dict
                from a json file, saved previously with `save_from_dblp`.

            generate_graph (bool): Generates the authors_and_papers
                graph from the  articles read
        """

        self.G = nx.MultiDiGraph()
        self.yearly_G = nx.MultiDiGraph()

        # Read file adding to array
        if read_from_dblp:
            conference_papers = self.read_from_dblp(read_saved_from_dblp, save_from_dblp)
        else:
            conference_papers = self.read_from_json()

        # Store older_papers in an arrray
        older_papers = {}

        # Store missing countries
        missing_set = set()

        # Store papers count per conference
        papers_count = defaultdict(lambda: 0)

        # Store papers count per year
        papers_year_count = defaultdict(lambda: 0)

        # Iterate through all the dataset years
        for year in tqdm(range(self.min_year, self.max_year)):

            # Reset yearly graph
            if save_non_cummulated_yearly_gpickle:
                self.yearly_G = nx.DiGraph()

            if generate_missing_countries:
                print(f"Generating missing countries for year {str(year)}")

                for paper in conference_papers.get(str(year), []):
                    for author in paper["authors"]:
                        for org in [author.get("org", ""), *author.get("orgs", [])]:
                            found, country = infer_country_from(org)
                            if not found and country not in missing_set:
                                missing_set.add(country)

                    papers_count[paper["venue"]["raw"]] += 1
                    papers_year_count[year] += 1

            elif generate_graph and read_from_dblp:
                print(f"Parsing year {str(year)}")

                # Add papers and authors to be referenced later
                for paper in conference_papers.get(year, []):
                    older_papers[paper["id"]] = [author for author in paper["authors"]]

                for paper in conference_papers.get(year, []):
                    # Adiciona/atualiza nodos dos países
                    for author in paper["authors"]:
                        country = infer_country_from(author.get("org", ""))
                        if country is not None:
                            self.G.add_node(country)

                            if save_non_cummulated_yearly_gpickle:
                                self.yearly_G.add_node(country)

                    # Adiciona arestas
                    for citation_id in paper["references"]:
                        # Other paper authors
                        if citation_id in older_papers:
                            for other_author in older_papers[citation_id]:
                                for author in paper["authors"]:
                                    # Fetch countries
                                    country = infer_country_from(author.get("org", ""))
                                    other_country = infer_country_from(other_author.get("org", ""))

                                    # Add edge
                                    if country is not None and other_country is not None:
                                        self.G.add_edge(country, other_country)

                                        if save_non_cummulated_yearly_gpickle:
                                            self.yearly_G.add_edge(country, other_country)

                self.print_graph_info()
            else:
                self.G = self.read_from_gpickle(year)

            # Saving graph to .gpickle file
            if save_yearly_gpickle and self.G.number_of_nodes() > 0:
                # Compute centralities for each year
                self.compute_centralities(
                    degree=compute_degree,
                    betweenness=compute_betweenness,
                    closeness=compute_closeness,
                    pagerank=compute_pagerank,
                )

                super().save_yearly_gpickle(year)

                if save_non_cummulated_yearly_gpickle:
                    # Compute centralities for each year
                    self.compute_centralities(
                        degree=compute_degree,
                        betweenness=compute_betweenness,
                        closeness=compute_closeness,
                        pagerank=compute_pagerank,
                        G=self.yearly_G,
                    )

                    super().save_yearly_gpickle(year, G=self.yearly_G, graph_name="yearly_" + self.graph_name)

        with open("../data/missing_countries.json", "w") as f:
            json.dump({country: "" for country in missing_set}, f)

        count = sum(len(value) for value in conference_papers.values())
        print("Papers count per conference", papers_count)
        print("Papers count per year", papers_year_count)
        print("Total papers count: ", count)

        if generate_graph and read_from_dblp:
            print("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gpickle
        if generate_graph and save_gpickle:
            super().save_gpickle()


if __name__ == "__main__":
    graphGeneration = CountryCitationGraph(
        graph_name=GRAPH_TYPE, conference_name=CONFERENCE_NAME, conference_ids=CONFERENCE_IDS
    )

    fire.Fire(graphGeneration.generate)
