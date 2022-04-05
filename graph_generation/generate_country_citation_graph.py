# Main class import
from collections import Counter, defaultdict
from typing import List
import numpy as np
import smoothfit

from tqdm import tqdm, trange
from generate_graph import GenerateGraph

# Core imports
import json
import os
from pprint import pprint as pp

# Library imports
import networkx as nx
import fire
import matplotlib.pyplot as plt
import seaborn as sns

## COMMAND USED TO RUN KINDA EVERYTHING
# python3 graph_generation/generate_graph.py --run-country-citation-graph --conference_name="AAAI-NIPS-IJCAI" --generate-graph --save-non-cummulated-yearly-gpickle --save-yearly-gpickle --save-non-cummulated-yearly-gpickle --save-gpickle


# Global graph configurations
sns.set_style("white")
plt.rc("axes", titlesize=18)  # fontsize of the axes title
plt.rc("axes", labelsize=14)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=13)  # fontsize of the tick labels
plt.rc("ytick", labelsize=13)  # fontsize of the tick labels
plt.rc("legend", fontsize=13)  # legend fontsize
plt.rc("font", size=13)  # controls default text sizes

colors = sns.color_palette("husl", 16)

# Constants
CONFERENCE_IDS = ["1184914352", "1127325140", "1203999783"]
CONFERENCE_NAME = "AAAI-NIPS-IJCAI"
GRAPH_TYPE = "countries_citation"

COUNTRY_REPLACEMENT = {}


def infer_country_from(organizations: List[str]):
    for organization in organizations:
        # Parse last name after all commas
        country = organization.split(", ")[-1].replace(".", "").lower()

        # Remove those pesky tabs
        country = country.replace("#TAB#", "")
        country = country.replace("#tab#", "")

        # Remove useless characters
        for old, new in [("(", ""), (")", ""), ("[", ""), ("]", ""), ("-", " "), ("_", " ")]:
            country = country.replace(old, new)

        # Make country replacement
        if country in COUNTRY_REPLACEMENT.keys():
            return (True, COUNTRY_REPLACEMENT[country])

        # Make org replacement
        if organization in COUNTRY_REPLACEMENT.keys():
            return (True, COUNTRY_REPLACEMENT[organization])

    return (False, organization)


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
        generate_missing_countries: bool = False,
        save_non_cummulated_yearly_gpickle: bool = False,
        read_from_dblp: bool = False,
        save_from_dblp: bool = False,
        read_saved_from_dblp: bool = False,
        generate_institutions_countries_count_chart: bool = False,
        generate_graph: bool = False,
        compute_degree: bool = False,
        compute_closeness: bool = False,
        compute_betweenness: bool = False,
        compute_pagerank: bool = False,
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

            generate_institutions_countries_count_chart(bool): Generates a chart showing
            the count of institutions per countyr
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

        # Used countries
        used_countries_set = set()

        # Store papers count per conference
        papers_count = defaultdict(lambda: 0)

        # Store papers count per year
        papers_year_count = defaultdict(lambda: 0)

        # Store how many papers we had per country per year
        papers_per_year_per_country = defaultdict(lambda: defaultdict(lambda: 0))

        # Iterate through all the dataset years
        for year in trange(self.min_year, self.max_year, desc="Years"):

            year_papers = conference_papers.get(str(year), [])

            # Reset yearly graph
            if save_non_cummulated_yearly_gpickle:
                self.yearly_G = nx.DiGraph()

            tqdm.write(f"Detecting countries for year {str(year)}")

            for paper in tqdm(year_papers, desc="Parsing Countries"):
                for author in paper["authors"]:
                    author_country = None
                    for org in [author.get("org", ""), *author.get("orgs", [])]:
                        found, country = infer_country_from([org])

                        if found and author_country is None:
                            author_country = country

                        if not found and country not in missing_set:
                            missing_set.add(country)
                        else:
                            used_countries_set.add(country)

                papers_per_year_per_country[year][author_country] += 1
                papers_count[paper["venue"]["raw"]] += 1
                papers_year_count[year] += 1

            if generate_graph:
                tqdm.write(f"Parsing year {str(year)}")

                # Add papers and authors to be referenced later
                for paper in year_papers:
                    older_papers[paper["id"]] = [author for author in paper["authors"]]

                for paper in tqdm(year_papers, desc="Conference Papers"):
                    # Adiciona/atualiza nodos dos países
                    for author in paper["authors"]:
                        country = infer_country_from([author.get("org", ""), *author.get("orgs", [])])
                        if country is not None:
                            self.G.add_node(country)

                            if save_non_cummulated_yearly_gpickle:
                                self.yearly_G.add_node(country)

                    # Adiciona arestas
                    for citation_id in paper["references"]:
                        # Other paper authors
                        if citation_id in older_papers:
                            for other_author in older_papers[citation_id]:
                                other_country = infer_country_from(
                                    [other_author.get("org", ""), *other_author.get("orgs", [])]
                                )
                                for author in paper["authors"]:
                                    # Fetch countries
                                    country = infer_country_from([author.get("org", ""), *author.get("orgs", [])])

                                    # Add edge
                                    if country is not None and other_country is not None:
                                        self.G.add_edge(country, other_country)

                                        if save_non_cummulated_yearly_gpickle:
                                            import pdb

                                            pdb.set_trace()

                                            self.yearly_G.add_edge(country, other_country)

                self.print_graph_info()
            # else:
            # self.G = self.read_from_gpickle(year)

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

        # Just use the COUNTRY_REPLACEMENT array to generate a quick chart
        if generate_institutions_countries_count_chart:
            values = [
                "-" if value is None else value
                for value in list(COUNTRY_REPLACEMENT.values())
                if value in used_countries_set
            ]
            counter = Counter(values)

            most_common = counter.most_common()
            labels, values = [key for key, val in most_common], [val for key, val in most_common]

            # First figure is a bar chart with how many institutions every used country has
            plt.xticks(rotation="vertical")
            fig = plt.figure(figsize=(13, 16), tight_layout=True)
            ax = fig.add_subplot(111)

            bars = ax.barh(labels[::-1], values[::-1], color=colors[:5])
            ax.bar_label(bars)

            ax.set_xlabel("Organizations Count")
            ax.set_ylabel("Countries")
            ax.set_title("Organizations Count x Country")
            fig.savefig("country_replacement_bar.png")

            # Second figure is a stacked country chart showing how many publications
            # per country we have every year
            years = np.array(list(papers_per_year_per_country.keys()))

            last_year = years[-1]
            last_year_papers = papers_per_year_per_country[last_year]
            top_countries_labels = [
                label for label, _value in sorted(last_year_papers.items(), key=lambda x: -x[1])  # if label is not None
            ][:15]
            values = np.array(
                [
                    [
                        year_values.get(country if country != "None" else "-", 0)
                        for year_values in papers_per_year_per_country.values()
                    ]
                    for country in top_countries_labels
                ]
            )
            percent = values / values.sum(axis=0).astype(float) * 100

            fig = plt.figure(figsize=(15, 15), tight_layout=True)
            ax = fig.add_subplot(111)

            ax.stackplot(years, percent, colors=colors, labels=top_countries_labels)
            ax.set_xticks(range(1970, 2015 + 1, 5))
            ax.set_title("Stacked percentage per country per year")
            ax.set_ylabel("Percent (%)")
            ax.margins(0, 0)  # Set margins to avoid "whitespace"

            # Shrink current axis's on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.001, box.width, box.height * 0.999])

            # Put a legend below current axis
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

            fig.savefig("countries_stacked.png")

            # Third figure is the count of different countries per year
            plt.xticks(rotation="vertical")
            fig = plt.figure(figsize=(10, 10), tight_layout=True)
            ax = fig.add_subplot(111)

            data = np.array([len(papers_per_year_per_country[year]) for year in years])
            ax.plot(years, data)

            basis, coeffs = smoothfit.fit1d(years, data, years.min(), years.max(), 5, degree=1, lmbda=1.0e-6)
            ax.plot(basis.mesh.p[0], coeffs[basis.nodal_dofs[0]], "-")

            ax.set_yticks(range(data.min(), data.max() + 1))
            ax.grid(axis="x", color="0.95")
            ax.grid(axis="y", color="0.9")

            ax.set_xlabel("Year")
            ax.set_ylabel("Countries Count")
            fig.savefig("country_per_year_line.png")

        if generate_missing_countries:
            with open("../data/missing_countries.json", "w") as f:
                json.dump({country: "" for country in missing_set}, f)

        if generate_graph:
            tqdm.write("Finished creating the graph")
            self.print_graph_info()

        # Save graph to .gpickle
        if generate_graph and save_gpickle:
            super().save_gpickle()


if __name__ == "__main__":
    graphGeneration = CountryCitationGraph(
        graph_name=GRAPH_TYPE, conference_name=CONFERENCE_NAME, conference_ids=CONFERENCE_IDS
    )

    fire.Fire(graphGeneration.generate)
