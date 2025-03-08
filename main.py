import utils, networkx as nx

# configuration parameters
communityDetection = "girvan_newman"
usingWeights = False


url = 'CsCh_10'
snapshot_graphs = utils.load_files_from_folder(url, n_sort=True, file_format=".gml")

numberOfCommunities = 0
isolatedNodes = 0
snapshots = 0
maxCommunitySize = 0
communitySizes = []
numberOfIsolatedNodes = []

# for each snapshot
for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)
    if communityDetection == "girvan_newman":
        if usingWeights:
            communitiesIterator = nx.community.girvan_newman(G, utils.most_central_edge)
        else:
            communitiesIterator = nx.community.girvan_newman(G)
        communities = list(sorted(c) for c in next(communitiesIterator))

        isolatedCommunities = 0
        for community in communities:
            if len(community) == 1:
                isolatedCommunities += 1
        isolatedNodes += isolatedCommunities
    elif communityDetection == "louvain":
        if usingWeights:
            communities = nx.community.louvain_communities(G, weight="count")
        else:
            communities = nx.community.louvain_communities(G)
        isolatedCommunities = 0

    # finding the largest community
    largestCommunity = len(max(communities, key=len))
    maxCommunitySize = max(maxCommunitySize, largestCommunity)

    numberOfCommunities += len(communities)
    isolatedNodes += len(utils.find_isolated_nodes(communities))
    #print("{}. snapshot:".format(i+1), len(utils.find_isolated_nodes(communities)) + isolatedCommunities)
 
    communityOfNode = utils.get_community_of_node(communities)
    #print("{}. snapshot:".format(i+1), communityOfNode)

    communitySizes.append(len(communities) - isolatedCommunities)
    numberOfIsolatedNodes.append(len(utils.find_isolated_nodes(communities)) + isolatedCommunities)
    snapshots += 1

if usingWeights:
    weights = "(TEŽINA)"
else:
    weights = "(BEZ TEŽINE)"

if communityDetection == "girvan_newman":
    print("GIRVAN-NEWMANOV ALGORITAM " + weights)
elif communityDetection == "louvain":
    print("LOUVAINOV ALGORITAM " + weights)

print("\nDuljina najveće zajednice:", maxCommunitySize)
print("Ukupan broj zajednica:", numberOfCommunities)
print("Prosječan broj zajednica:", numberOfCommunities / snapshots)

print("Ukupan broj izoliranih mušica:", isolatedNodes)
print("Prosječan broj izoliranih mušica:", isolatedNodes / snapshots)

#utils.createHistogram(communitySizes, 'community_size', communityDetection, usingWeights)
#utils.createHistogram(numberOfIsolatedNodes, 'isolated_flies', communityDetection, usingWeights)