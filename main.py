import utils, networkx as nx

url = 'CsCh_10'
snapshot_graphs = utils.load_files_from_folder(url, n_sort=True, file_format=".gml")

# for each snapshot
sum = 0
snapshots = 0
for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)

    communities = nx.community.louvain_communities(G, weight="count")
    sum += len(communities)
    snapshots += 1

    """
    communityOfNode = utils.getCommunityOfNode('fly1', communities)
    print("{}. snapshot:".format(i+1), G.number_of_nodes())
    """

print("Prosječan broj snapshotova:", sum / snapshots)