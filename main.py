import utils, networkx as nx

url = 'CsCh_10'
snapshot_graphs = utils.load_files_from_folder(url, n_sort=True, file_format=".gml")

# for each snapshot
numberOfCommunities = 0
isolatedNodes = 0
snapshots = 0
maxCommunitySize = 0

for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)
    communities = nx.community.louvain_communities(G, weight="count")

    # finding the largest community
    largestCommunity = len(max(communities, key=len))
    maxCommunitySize = max(maxCommunitySize, largestCommunity)

    numberOfCommunities += len(communities)
    isolatedNodes += len(utils.find_isolated_nodes(communities))
    
    snapshots += 1
    #print("{}. snapshot:".format(i+1), isolatedNodes)

    communityOfNode = utils.get_community_of_node(communities)
    #print("{}. snapshot:".format(i+1), communityOfNode)


print("Duljina najveće zajednice:", maxCommunitySize)
print("Ukupan broj zajednica:", numberOfCommunities)
print("Prosječan broj zajednica:", numberOfCommunities / snapshots)
print("Prosječan broj izoliranih mušica:", isolatedNodes / snapshots)