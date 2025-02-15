# TODO: Understand what this file generates

# Core imports
import string
import re
import json
from pprint import pprint as pp

# Library imports
from unidecode import unidecode
import nltk
from nltk.corpus import stopwords
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from tqdm import tqdm
import click

# Constants
DATASET_SIZE = 4_107_340
CONFERENCE_IDS = ["1184914352", "1127325140", "1203999783"]
CONFERENCE_NAME = "AAAI-NIPS-IJCAI"
AUTHOR_COLOR = "#eb3dce"
PAPER_COLOR = "#57def2"
COLOR_PALETTE = [
    ("#FECEE9", "#EFA0CD", "#FF66BC", "#4F032E", "#0F0008"),
    ("#D4E4BC", "#AAB796", "#6B8E36", "#576D36", "#384722"),
    ("#BAD3E0", "#5FA7CE", "#2DB5FF", "#0091E0", "#275B77"),
    ("#F9EDEE", "#DBA6AB", "#E63946", "#9E454C", "#561C21"),
]
DATASET_BASE_PATH = "./dblp_arnet/"
GML_BASE_PATH = "./GML/"

FREQUENCY_OFFSET = 10

# Fetch stopwords, and download them if they haven't been yet
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
STOP_WORDS = set(stopwords.words("english"))

# "Enums" for nodes/edges types
PAPER_NODE = "paper"
AUTHOR_NODE = "author"
AUTHORSHIP_EDGE = "authorship"
CITATION_EDGE = "citation"


def get_data(dictionary):
    """Given a dictionary, parse the necessary data contained in it"""
    return {
        "id": dictionary.get("id", 0),
        "title": dictionary.get("title", ""),
        "year": int(dictionary.get("year", 0)),
        "authors": dictionary.get("authors", []),
        "references": dictionary.get("references", []),
    }


@click.command()
@click.option(
    "--save-gml",
    is_flag=True,
    help="Save the final graph generated to a GML file, named by `--graph-file`, prepended with the year",
)
@click.option("--save-yearly-gml", is_flag=True, help="Save the graph generated in each year timestep to a GML file")
@click.option(
    "--plot-graph-figure",
    is_flag=True,
    help="Tries to apply a spring layout to the graph and print it. Use it carefully",
)
@click.option(
    "--read-from-dblp",
    is_flag=True,
    help="Read the graph from the dblp json file. If false, reads the GML from `--graph-file`",
)
@click.option(
    "--save-from-dblp", is_flag=True, help="Saves the graph generated when using --read-from-dblp to a JSON file"
)
@click.option(
    "--generate-graph",
    is_flag=True,
    help="If True, generates a graph from the conferences read if called with `--read-from-dblp`",
)
@click.option(
    "--parse-bag-of-words",
    is_flag=True,
    help="If True, generates a bag of words from the texts in the papers, and saves them to a file",
)
@click.option(
    "--figure-save-path",
    default="graph.svg",
    help="Path to save the figure generated by calling this with `--plot-graph-figure`",
)
@click.option("--graph-file", default="graph.gml", help="GML filename where the graph is read and/or saved to")
@click.option("--dblp-filename", default="dblp_papers_v11.txt", help="File containing the DBLP-downloaded data")
@click.option("--papers-filename", default="papers.json", help="JSON file where we save the parsed DBLP file")
def generate_graph(
    save_gml,
    save_yearly_gml,
    plot_graph_figure,
    read_from_dblp,
    save_from_dblp,
    generate_graph,
    parse_bag_of_words,
    figure_save_path,
    graph_file,
    dblp_filename,
    papers_filename,
):

    G = nx.DiGraph()
    conference_papers = {}
    indexed_words = {}  # Every word in the abstracts

    # Read file adding to array
    if read_from_dblp:
        with open("./dblp_arnet/{}".format(dblp_filename), "r") as f:
            for line in tqdm(f, total=DATASET_SIZE):
                parsed_paper = json.loads(line)
                try:
                    if parsed_paper["venue"]["id"] in CONFERENCE_IDS:
                        # If doesn't have year in the dictionary
                        if parsed_paper["year"] not in conference_papers:
                            conference_papers[parsed_paper["year"]] = []

                        # Only parse those with abstract
                        indexed_abstract = parsed_paper["indexed_abstract"]
                        if indexed_abstract["IndexLength"] > 0:
                            conference_papers[parsed_paper["year"]].append(get_data(parsed_paper))

                            if parse_bag_of_words:
                                # Build abstract string
                                abstract = ["" for x in range(indexed_abstract["IndexLength"])]
                                for word, arr in indexed_abstract["InvertedIndex"].items():
                                    for idx in arr:
                                        abstract[idx] = word
                                tokenized_abstract = nltk.word_tokenize(" ".join(abstract))

                                # Remove unwanted characters
                                regex_str = r"['0-9\-\.\,\\\/\]\+\*\^\_\=\:\~\|\!\"\(\)\[\]\<\>\#\?\u2017\u000f\u2014\u2212\u21d2\u2208\u2264\u2032]"
                                tkn_abstract = [
                                    re.sub(regex_str, r" ", unidecode(tkn))
                                    for tkn in tokenized_abstract
                                    if "github" in tkn or not re.fullmatch("[{}]+".format(string.punctuation), tkn)
                                ]
                                tkn_abstract = " ".join(tkn_abstract).split(" ")
                                for abstract_word in tkn_abstract:
                                    if len(abstract_word) > 0 and abstract_word.lower() not in STOP_WORDS:
                                        indexed_words[abstract_word.lower()] = (
                                            indexed_words.get(abstract_word.lower(), 0) + 1
                                        )
                except KeyError as e:
                    pass
        if save_from_dblp:
            with open("./dblp_arnet/{}".format(papers_filename), "w") as f:
                json.dump(conference_papers, f)
    else:
        with open("./dblp_arnet/{}".format(papers_filename), "r") as f:
            conference_papers = json.load(f)

    # Bag of words
    if parse_bag_of_words:
        indexed_words_set = set()
        for word, count in indexed_words.items():
            if not count < FREQUENCY_OFFSET:
                indexed_words_set.add(word)

        with open("indexed_words.json", "w") as f:
            json.dump(sorted(list(indexed_words_set)), f)
    else:
        indexed_words_set = None
        with open("indexed_words.json", "r") as f:
            indexed_words = json.load(f)
            indexed_words_set = set(indexed_words)

    # Store older_papers in a dict
    older_papers = {}

    # Iterate through all the dataset years
    for year in range(1890, 2020):

        if generate_graph and read_from_dblp:
            print("Parsing year {}".format(str(year)))

            # Add papers and authors to be referenced later
            for paper in conference_papers.get(year, []):
                older_papers[paper["id"]] = [author for author in paper["authors"]]

            # Only after we can link them to one another
            # that's why we iterate twice
            for paper in conference_papers.get(year, []):
                # Adiciona nodos dos papers
                G.add_node(paper["id"], name=paper["title"], type=PAPER_NODE)

                # Adiciona/atualiza nodos dos autores,
                # adicionando arestas para o nodo do paper também
                for author in paper["authors"]:
                    G.add_node(author["id"], name=author.get("name", ""), type=AUTHOR_NODE)

                    if paper["id"] in older_papers:
                        G.add_edge(author["id"], paper["id"], type=AUTHORSHIP_EDGE)

                # Adiciona arestas de citação
                for citation_id in paper["references"]:
                    if citation_id not in older_papers:
                        G.add_node(citation_id, name="undefined", type=PAPER_NODE)

                    G.add_edge(paper["id"], citation_id, type=CITATION_EDGE)

            print("Current Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))
        else:
            gml_filename = GML_BASE_PATH + "{}_{}_recommender_{}".format(CONFERENCE_NAME, year, graph_file)
            print("Reading graph from GML file {}".format(gml_filename))
            try:
                G = nx.read_gml(gml_filename)
                print("Finished reading graph from GML file")
            except FileNotFoundError:
                G = nx.DiGraph()
                print("Generating empty graph, as there is no file")

        if plot_graph_figure:
            # Draw graph
            f = plt.figure()
            plt.title("Authors references graph until {}".format(str(year)))
            node_sizes = [degree + 1 for node, degree in list(G.in_degree())]
            nx.draw_spring(G, node_size=node_sizes, alpha=0.4, arrowsize=2, arrowstyle="- >")

            # Save graph
            f.savefig(str(year) + "_authors_" + figure_save_path)
            # plt.show()
            plt.close()
            print("Saved figure for year {}".format(str(year)))

        if save_yearly_gml and G.number_of_nodes() > 0:
            # Saving graph to .gml file
            gml_filename = GML_BASE_PATH + "{}_{}_recommender_{}".format(CONFERENCE_NAME, year, graph_file)
            nx.write_gml(G, gml_filename)
            print("Saved graph to .gml file")

    if generate_graph and read_from_dblp:
        print("Finished creating the graph")
        print("Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))

    # Save graph to .gml
    if save_gml:
        path = GML_BASE_PATH + "{}_recommender_{}".format(CONFERENCE_NAME, graph_file)
        nx.write_gml(G, path)
        print(f"Saved graph to {path} file")


if __name__ == "__main__":
    generate_graph()
