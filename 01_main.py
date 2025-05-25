import utils, plot
import networkx as nx
import numpy as np
import pandas as pd
import os


# configuration parameters
communityDetectionAlgorithms = ["louvain"]
usingWeights = True

snapshots_folder = 'initial_networks/10_sec_window/'
folders = os.listdir(snapshots_folder)
allFlies = utils.get_all_flies(numOfFlies = 12)

#gn = []
#louvain = []
#groups = []
histDict = {}

# for each group
for folder in folders:
    folder_path = snapshots_folder + folder
    # load all GML networks
    snapshot_graphs = utils.load_files_from_folder(folder_path, n_sort=True, file_format=".gml")
    histData = []

    # for each community detection algorithm
    for communityDetection in communityDetectionAlgorithms:
        print()
        labels = utils.get_labels(folder_path, communityDetection, usingWeights)
        if communityDetection == "girvan_newman":
            algorithm = "GIRVAN-NEWMANOV ALGORITAM"
        elif communityDetection == "louvain":
            algorithm = "LOUVAINOV ALGORITAM"
        print("("+ labels["type"] +") "+ algorithm +" - " + labels["weights"] + " - snapshotovi od " + labels["snapshotSize"] + " sekundi")

        numberOfCommunities = 0
        isolatedFlies = 0
        snapshots = 0
        maxCommunitySize = 0
        communitySizes = []
        numberOfIsolatedNodes = []
        snapshotsCommunities = []

        # for each snapshot
        for graph_path in snapshot_graphs.values():
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
            elif communityDetection == "louvain":
                if usingWeights:
                    communities = nx.community.louvain_communities(G, weight="count", seed=100)
                else:
                    communities = nx.community.louvain_communities(G, seed=100)
                isolatedCommunities = 0

            # finding the largest community
            largestCommunity = len(max(communities, key=len))
            maxCommunitySize = max(maxCommunitySize, largestCommunity)

            # counting number of found communities and isolated ones
            numberOfCommunities += len(communities)
            numOfIsolatedNodes = len(utils.find_isolated_nodes(communities, allFlies))
            isolatedFlies += numOfIsolatedNodes + isolatedCommunities
            
            # stores graph for each snapshot into an array
            snapshotsCommunities.append(communities)
            communitySizes.append(len(communities))
            numberOfIsolatedNodes.append(numOfIsolatedNodes + isolatedCommunities)

            # histogram
            """
            #ISOLATED NODES:
            histData.append(numOfIsolatedNodes + isolatedCommunities)
            #COMMUNITY LENGTH:
            histData.append(len(communities))
            #COMMUNITY SIZES:
            communitySizes = [len(comm) for comm in communities]
            histData.extend(communitySizes)
            """
            communitySizes = [len(comm) for comm in communities]
            histData.extend(communitySizes)

            snapshots += 1


        """
        # grouped bar chart
        if communityDetection == "girvan_newman":
            gn.append(numberOfCommunities)
        elif communityDetection == "louvain":
            louvain.append(numberOfCommunities)
        """

        """
        consistentSnapshots = utils.track_consistent_communities(snapshotsCommunities)
        communitiesDicts = utils.generate_community_dict(consistentSnapshots, allFlies)
        plot.plot_colormap(communitiesDicts, labels, allFlies)
        """


        """
        matrix = utils.get_heatmap_data(communitiesDicts, allFlies, negative=False)
        # get elements from matrix above diagonal
        upper_elements = matrix[np.triu_indices_from(matrix, k=1)]
        #print(upper_elements.tolist())

        #df = pd.DataFrame(matrix, allFlies, allFlies)
        #plot.plot_heatmap(df, labels, False)
        """


        """
        fliesInTop3 = {key : 0 for key in allFlies}
        for fly in allFlies:
            sharedCommunities = utils.shared_communites(fly, communitiesDicts, allFlies)
            # Sort based on Values
            sharedCommunitiesSorted = {k : v for k, v in sorted(sharedCommunities.items(), key=lambda item: item[1], reverse=True)}
            
            counter = 0
            for k in sharedCommunitiesSorted.keys():
                fliesInTop3[k] += 1

                counter += 1
                if counter == 3:
                    break
        plot.plot_bar_chart(fliesInTop3, labels) 
        """
    
    # grouped bar
    #groups.append(labels["type"])
    histDict.update({labels["type"]: histData})

"""
# grouped bar
measuresDict = {
    'Girvan-Newman': gn, 
    'Louvain': louvain
}
#plot.plot_grouped_bar(measuresDict, groups, labels, 1, snapshots)
"""
plot.plot_histogram(histDict, 3, labels)