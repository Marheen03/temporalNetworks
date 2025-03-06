import utils, networkx as nx

url = 'CsCh_10'
snapshot_graphs = utils.load_files_from_folder(url, n_sort=True, file_format=".gml")

# for each snapshot
numberOfCommunities = 0
isolatedNodes = 0
snapshots = 0
maxCommunitySize = 0

communityDetection = "x"

for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)
    if communityDetection == "girvan_newman":
        communitiesIterator = nx.community.girvan_newman(G, utils.most_central_edge)
        communities = list(sorted(c) for c in next(communitiesIterator))

        isolatedCommunities = 0
        for community in communities:
            if len(community) == 1:
                isolatedCommunities += 1
        isolatedNodes += isolatedCommunities
    else:
        communities = nx.community.louvain_communities(G, weight="count")
        isolatedCommunities = 0

    # finding the largest community
    largestCommunity = len(max(communities, key=len))
    maxCommunitySize = max(maxCommunitySize, largestCommunity)

    numberOfCommunities += len(communities)
    isolatedNodes += len(utils.find_isolated_nodes(communities))
    #print("{}. snapshot:".format(i+1), len(utils.find_isolated_nodes(communities)) + isolatedCommunities)
 
    communityOfNode = utils.get_community_of_node(communities)
    #print("{}. snapshot:".format(i+1), communityOfNode)
    snapshots += 1

if communityDetection == "girvan_newman":
    print("GIRVAN-NEWMANOV ALGORITAM")
else:
    print("LOUVAINOV ALGORITAM")

print("Duljina najveće zajednice:", maxCommunitySize)
print("Ukupan broj zajednica:", numberOfCommunities)
print("Prosječan broj zajednica:", numberOfCommunities / snapshots)

print("Ukupan broj izoliranih mušica:", isolatedNodes)
print("Prosječan broj izoliranih mušica:", isolatedNodes / snapshots)
