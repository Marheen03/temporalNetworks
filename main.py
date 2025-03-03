import utils, networkx as nx

url = 'CsCh_10'
snapshot_graphs = utils.load_files_from_folder(url, n_sort=True, file_format=".gml")

# for each snapshot
for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)

    communities = nx.community.louvain_communities(G, weight="count")
    print (communities)

    """
    communityOfNode = utils.getCommunityOfNode('fly1', communities)
    print("{}. snapshot:".format(i+1), G.number_of_nodes())
    """

