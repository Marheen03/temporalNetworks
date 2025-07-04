import utils, plot, os
import networkx as nx
import numpy as np

numOfFlies = 12
accumulated = True
isDirected = True
usingWeights = True


if isDirected:
    directed = "(USMJEREN)"
else:
    directed = "(NEUSMJEREN)"

snapshots_folder = 'treatments/30_sec_window/'
folders = os.listdir(snapshots_folder)
cumulativeDict = {}

# for each group
for folder in folders:
    if accumulated:
        coefficients = []
    else:
        dict = {}
        
    folder_path = snapshots_folder + folder
    treatments = os.listdir(folder_path)
    
    labels = utils.get_labels(folder_path, "louvain", usingWeights)
    
    # for each treatment
    for i, treatment in enumerate(treatments):
        path = folder_path + "/" + treatment
        snapshot_graphs = utils.load_files_from_folder(path, n_sort=True, file_format=".gml")
        allFlies = utils.get_all_flies(numOfFlies)

        snapshotsCommunities = []
        # for each snapshot
        for j, graph_path in enumerate(snapshot_graphs.values()):
            G = nx.read_gml(graph_path)
            if not isDirected:
                G = G.to_undirected()

            if usingWeights:
                communities = nx.community.louvain_communities(G, weight="count", seed=100)
            else:
                communities = nx.community.louvain_communities(G, seed=100)
            print(i+1, j+1)

            # stores graph for each snapshot into an array
            snapshotsCommunities.append(communities)
        
        # makes snapshot IDs consistent
        consistent_snapshots = utils.track_consistent_communities(snapshotsCommunities)
        communitiesDict = []
        for communities in consistent_snapshots:
            communityOfNode = utils.get_community_of_node(communities, allFlies)
            communitiesDict.append(communityOfNode)

        matrix = utils.get_heatmap_data(communitiesDict, allFlies, negative=False)    
        # get elements above the matrix diagonal
        upper_elements = matrix[np.triu_indices_from(matrix, k=1)]
        values = upper_elements.tolist()

        if accumulated:
            # coefficients.extend(values)
            coefficients.append(sum(values) / len(values))
        else:
            key = "{}.".format(i+1)
            dict.update({key : values})
    
    if accumulated:
        cumulativeDict.update({labels["type"] : coefficients})
    else:
        cumulativeDict.update({labels["type"] : dict})


p1, p2, p3 = utils.statistical_test(cumulativeDict, automatic=True)

# plot.plot_boxplot(cumulativeDict, labels, accumulated, [p1, p2, p3])
