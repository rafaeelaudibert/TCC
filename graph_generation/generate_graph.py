# Imports
import json
from typing import TypeVar, List

import fire
import networkx as nx
import json_stream
from json_stream.dump import JSONStreamEncoder
from tqdm import tqdm, trange

from parallel_betweenness import betweenness_centrality_parallel
from parallel_closeness import closeness_centrality_parallel

# Helper function
T = TypeVar("T")


def map_lower(*input_list: List[T]) -> List[T]:
    return [entry.lower() for entry in input_list]


# Generic constants
CONFERENCE_IDS = {
    "all": None,
    "AAAI-NIPS-IJCAI": map_lower("AAAI", "NIPS", "NeurIPS", "IJCAI"),
    # AAAI, NIPS, IJCAI, CVPR, ECCV, ICCV, ICML, KDD, ACL, EMNLP, NAACL, SIGIR, WWW
    "CsRankings-IA": map_lower(
        "AAAI",
        "NIPS",
        "NeurIPS",
        "IJCAI",
        "CVPR",
        "ECCV",
        "ECCV (2)",
        "ECCV (3)",
        "ECCV (4)",
        "ECCV (5)",
        "ECCV (6)",
        "ECCV (7)",
        "ICCV",
        "ICCVG",
        "international conference on computer vision",  # Weird, I know, but what am I gonna do
        "ICML",  # International Conference on Machine Learning
        "ICMLC",  # International Conference on Machine Learning and Cybernetics
        "ICMLA",  # International Conference on Machine Learning and Applications
        "ICMLA (1)",  # International Conference on Machine Learning and Applications
        "ICMLA (2)",  # International Conference on Machine Learning and Applications
        "KDD",
        "knowledge discovery and data mining",
        "ACL",
        "EMNLP",
        "EMNLP-CoNLL",
        "Empirical Methods in Natural Language Processing",
        "NAACL",
        "HLT-NAACL",
        "SIGIR",
        "WWW",
    ),
}

VERSION = "v13"


class GenerateGraph:
    DATASET_SIZE = 5_354_309
    GML_BASE_PATH = "../GML/"
    DBLP_FILENAME = f"../dblp_arnet.{VERSION}.json"

    def __init__(
        self,
        graph_name: str = "",
        conference_name: str = "",
        conference_ids: List[int] = None,
        min_year: int = 1890,
        max_year: int = 2021,
    ):

        self.graph_name = graph_name
        self.conference_name = conference_name
        self.conference_ids = conference_ids
        self.min_year = min_year
        self.max_year = max_year

        self.G = nx.Graph()  # placeholder
        self.yearly_G = nx.Graph()  # placeholder

    def generate(self, **kwargs):
        raise NotImplementedError("You must implement this method")

    @staticmethod
    def get_data(dictionary: dict = {}) -> dict:
        """Given a dictionary, parse the necessary data contained in it"""
        # We need this because we are streaming the input
        dictified_dict = dict(dictionary)

        return {
            "id": dictified_dict.get("_id", dictified_dict.get("id", 0)),
            "title": dictified_dict.get("title", ""),
            "venue": dictified_dict.get("venue", None),
            "year": int(dictified_dict.get("year", 0)),
            "authors": list(map(dict, list(dictified_dict.get("authors", [])))),
            "references": list(dictified_dict.get("references", [])),
        }

    def print_graph_info(self) -> None:
        print(f"Graph size: {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges")

    def save_gpickle(self, G: nx.Graph = None, graph_name: str = None, conference_name: str = None) -> None:
        """Save a Graph G to a file in the `.gpickle` format"""

        # Default values
        G = G or self.G
        graph_name = graph_name or self.graph_name
        conference_name = conference_name or self.conference_name

        gpickle_filename = self.GML_BASE_PATH + "{}_{}_graph.gpickle".format(graph_name, conference_name)
        nx.write_gpickle(G, gpickle_filename)

        print(f"Saved graph to {gpickle_filename} file")

    def save_yearly_gpickle(
        self, year: int, G: nx.Graph = None, graph_name: str = None, conference_name: str = None
    ) -> None:
        """
        Save a Graph G, related to a given `year`,
        to a file in the `.gpickle` format
        """

        # Default values
        G = G or self.G
        graph_name = graph_name or self.graph_name
        conference_name = conference_name or self.conference_name

        gpickle_filename = self.GML_BASE_PATH + "{}_{}_{}_graph.gpickle".format(graph_name, conference_name, year)
        nx.write_gpickle(G, gpickle_filename)

        print(f"Saved graph to {gpickle_filename} file")

    def read_from_dblp(self, read_saved_from_dblp: bool = False, save_from_dblp: bool = False) -> dict:
        """
        Fetch DBLP data and parse it properly
        """

        conference_papers = {}

        if read_saved_from_dblp:
            json_filename = "../{}_{}.json".format(self.conference_name, self.graph_name)
            with open(json_filename, "r") as f:
                conference_papers = json.load(f)
        else:
            with open(self.DBLP_FILENAME, "r") as f:
                progress = tqdm(total=self.DATASET_SIZE, desc="Total")
                error_progress = tqdm(desc="Errors")
                success_progress = tqdm(desc="Success")
                for line in json_stream.load(f).persistent():
                    try:
                        if self.conference_ids is None or (
                            line["venue"]["raw"] is not None and line["venue"]["raw"].lower() in self.conference_ids
                        ):
                            # If doesn't have year in the dictionary
                            if line["year"] not in conference_papers:
                                conference_papers[line["year"]] = []

                            conference_papers[line["year"]].append(GenerateGraph.get_data(line))
                            success_progress.update(1)
                    except KeyError as e:
                        error_progress.update(1)
                        pass
                    finally:
                        progress.update(1)

        if save_from_dblp:
            json_filename = "../data/dblp_arnet_{}_{}.json".format(self.conference_name, self.graph_name)
            with JSONStreamEncoder():
                with open(json_filename, "w") as f:
                    json.dump(conference_papers, f, indent=4)

        return conference_papers

    def read_from_json(self) -> dict:
        json_filename = "../data/dblp_arnet_{}_{}.json".format(self.conference_name, self.graph_name)
        with open(json_filename, "r") as f:
            conference_papers = json.load(f)

        return conference_papers

    def read_from_gpickle(self, year: int) -> nx.DiGraph():
        gpickle_filename = self.GML_BASE_PATH + "{}_{}_{}_graph.gpickle".format(
            self.conference_name, year, self.graph_name
        )
        print(f"Reading graph from GML file {gpickle_filename}")

        try:
            self.G = nx.read_gpickle(gpickle_filename)
            print("Finished reading graph from GML file")
        except FileNotFoundError:
            self.G = nx.DiGraph()
            print("Generating empty graph, as there is no file")

    def compute_centralities(
        self, degree=False, betweenness=False, closeness=False, pagerank=False, G: nx.Graph = None
    ):
        # Check for default G
        if G is None:
            G = self.G

        if degree:
            self.compute_degree(G=G)

        if betweenness:
            self.compute_betweeness(G=G)

        if closeness:
            self.compute_closeness(G=G)

        if pagerank:
            self.compute_pagerank(G=G)

    def compute_degree(self, in_degree=True, out_degree=True, G: nx.Graph = None):

        # Check for default G
        if G is None:
            G = self.G

        print("Generating degree")
        degree_data = {node: degree for node, degree in list(G.degree)}
        nx.set_node_attributes(G, degree_data, "degree")

        if in_degree:
            print("Generating in_degree")
            in_degree_data = {node: degree for node, degree in list(G.in_degree)}
            nx.set_node_attributes(G, in_degree_data, "indegree")

        if out_degree:
            print("Generating out_degree")
            out_degree_data = {node: degree for node, degree in list(G.out_degree)}
            nx.set_node_attributes(G, out_degree_data, "outdegree")

    def compute_betweeness(self, G: nx.Graph = None):
        # Check for default G
        if G is None:
            G = self.G

        betweenness = betweenness_centrality_parallel(G)
        nx.set_node_attributes(G, betweenness, "betweenness")

    def compute_closeness(self, G: nx.Graph = None):
        # Check for default G
        if G is None:
            G = self.G

        closeness = closeness_centrality_parallel(G)
        nx.set_node_attributes(G, closeness, "closeness")

    def compute_pagerank(self, G: nx.Graph = None):
        # Check for default G
        if G is None:
            G = self.G

        print("Generating pagerank")
        try:
            pagerank = nx.pagerank(G)
        except nx.exception.NetworkXNotImplemented:
            print(
                "Not implemented pagerank for MultiGraph. \
                   Converting to normal graph"
            )
            pagerank = nx.pagerank(nx.DiGraph(G))

        nx.set_node_attributes(G, pagerank, "pagerank")


# endclass GenerateGraph


def generate_graph(
    run_authors_and_papers_graph: bool = False,
    run_collaboration_graph: bool = False,
    run_citation_graph: bool = False,
    run_authors_citation_graph: bool = False,
    run_country_citation_graph: bool = False,
    conference_name: str = "CsRankings-IA",
    **kwargs: dict,
) -> None:
    """
    Run the required authors generation
    """

    if run_authors_and_papers_graph:
        from generate_authors_and_papers_graph import AuthorPaperGraph

        graphGeneration = AuthorPaperGraph(
            graph_name="author_paper",
            conference_name=conference_name,
            conference_ids=CONFERENCE_IDS.get(conference_name, None),
        )

        print("Starting AuthorPaperGraph generation")
        graphGeneration.generate(**kwargs)
        del graphGeneration

    if run_collaboration_graph:
        from generate_collaboration_graph import CollaborationGraph

        graphGeneration = CollaborationGraph(
            graph_name="collaboration",
            conference_name=conference_name,
            conference_ids=CONFERENCE_IDS.get(conference_name, None),
        )

        print("Starting CollaborationGraph generation")
        graphGeneration.generate(**kwargs)
        del graphGeneration

    if run_citation_graph:
        from generate_citation_graph import CitationGraph

        graphGeneration = CitationGraph(
            graph_name="citation",
            conference_name=conference_name,
            conference_ids=CONFERENCE_IDS.get(conference_name, None),
        )

        print("Starting CitationGraph generation")
        graphGeneration.generate(**kwargs)
        del graphGeneration

    if run_authors_citation_graph:
        from generate_authors_citation_graph import AuthorsCitationGraph

        graphGeneration = AuthorsCitationGraph(
            graph_name="authors_citation",
            conference_name=conference_name,
            conference_ids=CONFERENCE_IDS.get(conference_name, None),
        )

        print("Starting AuthorsCitationGraph generation")
        graphGeneration.generate(**kwargs)
        del graphGeneration

    if run_country_citation_graph:
        from generate_country_citation_graph import CountryCitationGraph

        graphGeneration = CountryCitationGraph(
            graph_name="countries_citation",
            conference_name=conference_name,
            conference_ids=CONFERENCE_IDS.get(conference_name, None),
        )

        print("Starting CountryCitationGraph generation")
        graphGeneration.generate(**kwargs)
        del graphGeneration


if __name__ == "__main__":
    fire.Fire(generate_graph)
