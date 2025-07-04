import utils, plot
import networkx as nx
import numpy as np
import pandas as pd
import os


# configuration parameters
#communityDetectionAlgorithms = ["girvan_newman", "louvain"]
communityDetectionAlgorithms = ["louvain"]
usingWeights = True

snapshots_folder = 'initial_networks/10_sec_window/'
folders = os.listdir(snapshots_folder)
allFlies = utils.get_all_flies(numOfFlies = 12)

gn = []
louvain = []
groups = []
dict = {}

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
        communitySizes = []
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

            # counting number of found communities and isolated ones
            numberOfCommunities += len(communities)
            numOfIsolatedNodes = len(utils.find_isolated_nodes(communities, allFlies))
            isolatedFlies += numOfIsolatedNodes + isolatedCommunities
            
            # stores graph for each snapshot into an array
            snapshotsCommunities.append(communities)
            communitySizes.append(len(communities))

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

            snapshots += 1

        """
        valueToAdd = isolatedFlies
        # valueToAdd = numberOfCommunities

        # grouped bar chart
        if communityDetection == "girvan_newman":
            gn.append(valueToAdd)
        elif communityDetection == "louvain":
            louvain.append(valueToAdd)
        """

        """
        # preference coefficients
        consistentSnapshots = utils.track_consistent_communities(snapshotsCommunities)
        communitiesDicts = utils.generate_community_dict(consistentSnapshots, allFlies)

        matrix = utils.get_heatmap_data(communitiesDicts, allFlies, negative=False)
        #df = pd.DataFrame(matrix, allFlies, allFlies)

        # get elements above the matrix diagonal
        upper_elements = matrix[np.triu_indices_from(matrix, k=1)]
        values = upper_elements.tolist()
        """
    
    # grouped bar
    #groups.append(labels["type"])

    # HIST COMMUNITY SIZES
    #dict.update({labels["type"]: histData})

    # preference coefficients
    #dict.update({labels["type"]: values})


# grouped bar
"""
dict = {
    'Girvan-Newman': gn, 
    'Louvain': louvain
}
"""
#plot.plot_grouped_bar(dict, groups, labels, 2, snapshots)
#plot.plot_histogram(dict, 2, labels)

#plot.plot_heatmap(dict, labels, False)
#plot.plot_colormap(dict, labels, allFlies)

#plot.plot_boxplot(dict, labels, accumulated=True)
#utils.statistical_test(dict)