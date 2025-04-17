import utils, plot, networkx as nx

# configuration parameters
numOfFlies = 12
communityDetection = "girvan_newman"
usingWeights = False
# snapshots_folder = 'isolated/30sec/CTRL10'
snapshots_folder = 'normal/30sec'

labels = utils.getLabels(snapshots_folder, communityDetection, usingWeights)

if communityDetection == "girvan_newman":
    print("GIRVAN-NEWMANOV ALGORITAM " + labels["weights"] + " - snapshotovi od " + labels["snapshotSize"] + " sekundi\n")
elif communityDetection == "louvain":
    print("LOUVAINOV ALGORITAM " + labels["weights"] + " - snapshotovi od " + labels["snapshotSize"] + " sekundi\n")


snapshot_graphs = utils.load_files_from_folder(snapshots_folder, n_sort=True, file_format=".gml")
allFlies = utils.getAllFlies(numOfFlies)

numberOfCommunities = 0
isolatedNodes = 0
snapshots = 0
maxCommunitySize = 0
communitySizes = []
numberOfIsolatedNodes = []
snapshotsCommunities = []

# for each snapshot
for i, graph_path in enumerate(snapshot_graphs.values()):
    G = nx.read_gml(graph_path)
    
    if communityDetection == "girvan_newman":
        if usingWeights:
            communitiesIterator = nx.community.girvan_newman(G, utils.most_central_edge)
        else:
            communitiesIterator = nx.community.girvan_newman(G)
        communitiesWithIsolatedNodes = list(sorted(c) for c in next(communitiesIterator))

        # communities without isolated nodes
        communities = [community for community in communitiesWithIsolatedNodes if len(community) != 1]
        isolatedCommunities = len(communitiesWithIsolatedNodes) - len(communities)
        isolatedNodes += isolatedCommunities

    elif communityDetection == "louvain":
        if usingWeights:
            communities = nx.community.louvain_communities(G, weight="count", seed=100)
        else:
            communities = nx.community.louvain_communities(G, seed=100)
        isolatedCommunities = 0

    # finding the largest community
    largestCommunity = len(max(communities, key=len))
    maxCommunitySize = max(maxCommunitySize, largestCommunity)

    numberOfCommunities += len(communities)
    numOfIsolatedNodes = len(utils.find_isolated_nodes(communities, allFlies))
    isolatedNodes += numOfIsolatedNodes
    #print("{}. snapshot:".format(i+1), len(utils.find_isolated_nodes(communities)) + isolatedCommunities)
    
    snapshotsCommunities.append(communities)

    communitySizes.append(len(communities) - isolatedCommunities)
    numberOfIsolatedNodes.append(numOfIsolatedNodes + isolatedCommunities)
    snapshots += 1

#plot.plotHistogram(communitySizes, 'community_size', labels)
#plot.plotHistogram(numberOfIsolatedNodes, 'isolated_flies', labels)


print("Ukupan broj zajednica:", numberOfCommunities)
print("Prosječan broj zajednica:", numberOfCommunities / snapshots)
print("Duljina najveće zajednice:", maxCommunitySize)

print("Ukupan broj izoliranih mušica:", isolatedNodes)
print("Prosječan broj izoliranih mušica:", isolatedNodes / snapshots)


"""
consistent_snapshots = utils.track_consistent_communities(snapshotsCommunities)
communitiesDict = []
for i, communities in enumerate(consistent_snapshots):
    communityOfNode = utils.get_community_of_node(communities, allFlies)
    communitiesDict.append(communityOfNode)
    
    #print("{}. snapshot:".format(i+1), communityOfNode)
    #print(f"Snapshot {i+1}: {communities}")

plot.plotColorMap(communitiesDict, labels)
df = utils.getHeatMapData(communitiesDict, allFlies, True)
plot.plotHeatMap(df, labels, True)
"""


"""
fliesInTop3 = {key : 0 for key in allFlies}
for fly in allFlies:
    sharedCommunities = utils.shared_communites(fly, communitiesDict, allFlies)
    # Sort based on Values
    sharedCommunitiesSorted = {k : v for k, v in sorted(sharedCommunities.items(), key=lambda item: item[1], reverse=True)}
    
    counter = 0
    for k in sharedCommunitiesSorted.keys():
        fliesInTop3[k] += 1

        counter += 1
        if counter == 3:
            break
plot.plotBarChart(fliesInTop3, labels) 
"""