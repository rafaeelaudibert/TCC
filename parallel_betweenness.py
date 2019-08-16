from multiprocessing import Pool
import time
import itertools

import matplotlib.pyplot as plt
import networkx as nx


def _chunks(nodes, n_chunks):
    """Divide a list of nodes `l` in `n` chunks"""
    l_iterator = iter(nodes)
    while True:
        nodes_tuple = tuple(itertools.islice(l_iterator, n_chunks))
        if not nodes_tuple:
            return
        yield nodes_tuple


def _betmap(G_normalized_weight_sources_tuple):
    """Pool for multiprocess only accepts functions with one argument.
    This function uses a tuple as its only argument. We use a named tuple for
    python 3 compatibility, and then unpack it when we send it to
    `betweenness_centrality_source`
    """
    return nx.betweenness_centrality_source(*G_normalized_weight_sources_tuple)  # nopep8


def betweenness_centrality_parallel(G, processes=None, **kwargs):
    """Parallel betweenness centrality  function"""
    pool = Pool(processes=processes)
    node_divisor = len(pool._pool) * 4
    node_chunks = list(_chunks(G.nodes(), int(G.order() / node_divisor)))
    num_chunks = len(node_chunks)
    betweenness_scores = pool.map(_betmap,
                                  zip([G] * num_chunks,
                                      [True] * num_chunks,
                                      [None] * num_chunks,
                                      node_chunks))

    # Reduce the partial solutions
    if len(betweenness_scores) > 0:
        betweenness_cumulator = betweenness_scores[0]
        for betweenness in betweenness_scores[1:]:
            for n in betweenness:
                betweenness_cumulator[n] += betweenness[n]
        return betweenness_cumulator
    else:
        return {}


if __name__ == "__main__":
    G_ba = nx.barabasi_albert_graph(1000, 3)
    G_er = nx.gnp_random_graph(1000, 0.01)
    G_ws = nx.connected_watts_strogatz_graph(1000, 4, 0.1)
    for G in [G_ba, G_er, G_ws]:
        print("")
        print("Computing betweenness centrality for:")
        print(nx.info(G))
        print("\tParallel version")
        start = time.time()
        bt = betweenness_centrality_parallel(G)
        print("\t\tTime: %.4F" % (time.time() - start))
        print("\t\tBetweenness centrality for node 0: %.5f" % (bt[0]))
        print("\tNon-Parallel version")
        start = time.time()
        bt = nx.betweenness_centrality(G)
        print("\t\tTime: %.4F seconds" % (time.time() - start))
        print("\t\tBetweenness centrality for node 0: %.5f" % (bt[0]))
    print("")

    nx.draw(G_ba)
    plt.show()
