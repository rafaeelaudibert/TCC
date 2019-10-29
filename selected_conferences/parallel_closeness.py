from multiprocessing import Pool
import time
import itertools
import functools

import matplotlib.pyplot as plt
import networkx as nx

from pprint import pprint as pp


def _chunks(nodes, n_chunks):
    """Divide a list of nodes `l` in `n` chunks"""
    l_iterator = iter(nodes)
    while True:
        nodes_tuple = tuple(itertools.islice(l_iterator, n_chunks))
        if not nodes_tuple:
            return
        yield nodes_tuple


def _betmap(G):
    """Pool for multiprocess only accepts functions with one argument.
    This function uses a tuple as its only argument. We use a named tuple for
    python 3 compatibility, and then unpack it when we send it to
    `betweenness_centrality_source`
    """
    centrality = closeness_centrality(*G[:-1])

    return centrality


def closeness_centrality_parallel(G, processes=None, **kwargs):
    """Parallel closeness centrality function"""
    pool = Pool(processes=processes)
    node_divisor = len(pool._pool) * 4
    node_chunks = list(_chunks(G.nodes(), int(G.order() / node_divisor)))
    num_chunks = len(node_chunks)
    print("Starting to compute closeness in {} chunks".format(num_chunks))
    graphs = [G] * num_chunks
    closeness_scores = pool.map(_betmap,
                                zip(graphs,
                                    node_chunks,
                                    [None] * num_chunks,
                                    [True] * num_chunks,
                                    [(x + 1, num_chunks) for x in range(num_chunks)])
                                )
    print("Finished computing closeness")
    pool.close()  # Remember to close the process pool

    print("Merging closeness values")
    # Reduce the partial solutions
    if len(closeness_scores) > 0:
        closeness_cumulator = closeness_scores[0]
        for closeness in closeness_scores[1:]:
            for n in closeness:
                if n not in closeness_cumulator:
                    closeness_cumulator[n] = closeness[n]
                else:
                    closeness_cumulator[n] += closeness[n]
        print("Finished merging")
        return closeness_cumulator
    else:
        print("No closeness to merge")
        return {}


def closeness_centrality(G, u=None, distance=None, wf_improved=True):
    if G.is_directed():
        G = G.reverse()  # create a reversed graph view

    if distance is not None:
        # use Dijkstra's algorithm with specified attribute as edge weight
        path_length = functools.partial(nx.single_source_dijkstra_path_length,
                                        weight=distance)
    else:
        path_length = nx.single_source_shortest_path_length

    if u is None:
        nodes = G.nodes
    else:
        nodes = u

    closeness_centrality = {}
    for n in nodes:
        sp = dict(path_length(G, n))
        totsp = sum(sp.values())

        if totsp > 0.0 and len(G) > 1:
            closeness_centrality[n] = (len(sp) - 1.0) / totsp

            # normalize to number of nodes-1 in connected part
            if wf_improved:
                s = (len(sp) - 1.0) / (len(G) - 1)
                closeness_centrality[n] *= s
        else:
            closeness_centrality[n] = 0.0

    return closeness_centrality


if __name__ == "__main__":
    G_ba = nx.barabasi_albert_graph(1000, 3)
    G_er = nx.gnp_random_graph(3000, 0.01)
    G_ws = nx.connected_watts_strogatz_graph(1000, 4, 0.1)
    for G in [G_er]:
        print("")
        print("Computing CLOSENESS centrality for:")
        print(nx.info(G))

        print("\tNon-Parallel version")
        start = time.time()
        bt = nx.closeness_centrality(G)
        print("\t\tTime: %.4F seconds" % (time.time() - start))
        print("\t\tCloseness centrality for node 0: %.5f" % (bt[0]))

        print("\tParallel version")
        start = time.time()
        bt = closeness_centrality_parallel(G)
        print("\t\tTime: %.4F" % (time.time() - start))
        print("\t\tCloseness centrality for node 0: %.5f" % (bt[0]))

    print("")

    nx.draw(G_ba)
    plt.show()
