import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from pprint import pprint as pp
from tqdm import tqdm, trange
from pprint import pprint as pp
import fire

DBLP_SIZE = 4_107_340
CONFERENCE_ID = '1203999783'
CONFERENCE_NAME = 'AAAI'
AUTHOR_COLOR = "#eb3dce"
PAPER_COLOR = "#57def2"
COLOR_PALETTE = ["#466365", "#B49A67", "#CEB3AB", "#C4C6E7", "#BAA5FF"]

def get_data(dictionary):
    return {
        'id': dictionary['id'] if 'id' in dictionary else 0,
        'title': dictionary['title'] if 'title' in dictionary else '',
        'year': dictionary['year'] if 'year' in dictionary else 0,
        'authors': dictionary['authors'] if 'authors' in dictionary else [],
        'references': dictionary['references'] if 'references' in dictionary else []
    }

def main(save_adj: bool = False, save_conf: bool = False, figure_save_path: str = "graph.svg"):
    G = nx.DiGraph()
    conference_papers = {}

    # Read file adding to array
    with open('./dblp_arnet/dblp_papers_v11.txt', 'r') as f:
        for cnt, line in tqdm(enumerate(f), total=DBLP_SIZE):
            parsed_json = json.loads(line)
            try:
                if parsed_json['venue']['id'] == CONFERENCE_ID:
                    
                    # If doesn't have year in the dictionary
                    if parsed_json['year'] not in conference_papers:
                        conference_papers[int(parsed_json['year'])] = []

                    conference_papers[int(parsed_json['year'])].append(get_data(parsed_json))
            except KeyError as e:
                pass

    older_papers = []
    year_colors = {}
    for year in sorted(conference_papers.keys()):
        year_conference_papers = conference_papers[year]
        year_color = "#{}".format(hex(abs(hash(str(year))))[2:8])
        year_colors[year] = year_color
        older_papers.extend([paper['id'] for paper in year_conference_papers]) # Add papers to be referenced

        print("I'm in year {} coloring {}".format(str(year), year_colors[year]))

        for paper in conference_papers[year]:
            G.add_node(paper['id'], color=year_colors[year])
            
            if 'references' in paper:
                for citation_id in paper['references']:
                    if citation_id in older_papers:
                        G.add_edge(paper['id'], citation_id)
        print("Current Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))

        # Draw graph
        f = plt.figure()
        plt.title(str(year))
        colors = [color for node, color in list(G.nodes.data('color'))]
        nx.draw_spring(G, node_size=10, alpha=0.4, node_color=colors)
        f.savefig(str(year) + figure_save_path)
        # plt.show()
        plt.close()
        print("Saved figure for year {}".format(str(year)))

    print("Year colors are: ")
    pp(year_colors)
    print("Finished creating the graph")
    print("Graph size: {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))

        

    # Write graph data to file
    if save_adj:
        with open('./dblp_arnet/{}_graph.json'.format(CONFERENCE_NAME), 'w') as f:
            data = json_graph.adjacency_data(G)
            json.dump(data, f)
        print("Saved adjacency networkx matrix")

    # Write json data to file
    if save_conf:
        with open('./dblp_arnet/{}.json'.format(CONFERENCE_NAME), 'w') as f:
            json.dump(conference_papers, f)
        print("Saved conference json")

if __name__ == "__main__":
    fire.Fire(main)
