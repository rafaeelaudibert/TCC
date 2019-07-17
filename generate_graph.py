import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from pprint import pprint as pp
from tqdm import tqdm, trange
import fire

DBLP_SIZE = 4_107_340
CONFERENCE_ID = '1203999783'
CONFERENCE_NAME = 'AAAI'
AUTHOR_COLOR = "#eb3dce"
PAPER_COLOR = "#57def2"
COLOR_PALETTE = ["#466365", "#B49A67", "#CEB3AB", "#C4C6E7", "#BAA5FF"]

def compute_colors(nodes):
    return [(AUTHOR_COLOR if node.starts_with('a') else PAPER_COLOR) for node in list(nodes)]

def get_data(dictionary):
    return {
        'title': dictionary['title'] if 'title' in dictionary else '',
        'year': dictionary['year'] if 'year' in dictionary else 0,
        'authors': dictionary['authors'] if 'authors' in dictionary else [],
        'citations': dictionary['citations'] if 'citations' in dictionary else []
    }

def main(save_adj: bool = False, save_conf: bool = False):
    G: nx.Graph = nx.Graph()
    conference_papers = {}

    # Read file adding to array
    with open('./dblp_arnet/dblp_papers_v11.txt', 'r') as f:
        for cnt, line in tqdm(enumerate(f), total=DBLP_SIZE):
            parsed_json = json.loads(line)
            try:
                if parsed_json['venue']['id'] == CONFERENCE_ID:
                    
                    # If doesn't have year
                    if parsed_json['year'] not in conference_papers:
                        conference_papers[parsed_json['year']] = []

                    conference_papers[parsed_json['year']].append(get_data(parsed_json))
                    
                    paper_node = "p_{}".format(parsed_json['id'])
                    G.add_node(paper_node)

                    for author in parsed_json['authors']:
                        author_node = "a_{}".format(author['id'])
                        G.add_node(author_node)
                        G.add_edge(paper_node, author_node)
                    break
            except KeyError as e:
                pass

    # Draw graph
    f = plt.figure(figsize=(24, 14), dpi=120)
    nx.draw_spring(G, threshold=0.001, node_size=1, alpha=0.05, node_color=compute_colors(G.nodes()))
    f.savefig("graph.svg")
    # plt.show()

    # Write graph data to file
    if save_adj:
        with open('./dblp_arnet/{}_graph.json'.format(CONFERENCE_NAME), 'w') as f:
            data = json_graph.adjacency_data(G)
            json.dump(data, f)

    # Write json data to file
    if save_conf:
        with open('./dblp_arnet/{}.json'.format(CONFERENCE_NAME), 'w') as f:
            json.dump(conference_papers, f)

if __name__ == "__main__":
    fire.Fire(main)
