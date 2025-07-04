import os, sys, re
import networkx as nx
import numpy as np
from scipy import stats


# returns appropriate labels for plots
def get_labels(snapshots_folder, communityDetection, usingWeights):
    folderName = snapshots_folder.split("/")

    if folderName[1][0] == '1':
        snapshot_size = "10"
    elif folderName[1][0] == '3':
        snapshot_size = "30"
    
    if communityDetection == "girvan_newman":
        detectionAlgorithm = "GN"
    elif communityDetection == "louvain":
        detectionAlgorithm = "LOUVAIN"
    
    if usingWeights:
        weights = "(S TEŽINOM)"
    else:
        weights = "(BEZ TEŽINE)"

    if folderName[2] == "Cs_5DIZ":
        type = "IZOLIRANE"
    elif folderName[2] == "Cs_10D":
        type = "STARE"
    else:
        type = "MLADE"

    return {
        "snapshotSize": snapshot_size,
        "detectionAlgorithm": detectionAlgorithm,
        "weights": weights,
        "type": type
    }


# returns array containing all flies
def get_all_flies(numOfFlies):
    return [f'fly{i+1}' for i in range(numOfFlies)]


# removes edge with the highest centrality based on weight
def most_central_edge(G):
    centrality = nx.edge_betweenness_centrality(G, weight="count")

    return max(centrality, key=centrality.get)


def natural_sort(l):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(l, key=alphanum_key)


def load_files_from_folder(path, file_format=".csv", n_sort=False):
    """
    Loads files of a specific format from a folder into a dictionary.

    Parameters:
    path (str): Directory path to load files from.
    file_format (str, optional): File format to filter by (default is ".csv").
    n_sort (bool, optional): Apply natural sorting if True (default is False).

    Returns:
    dict: Filenames as keys and their full paths as values.

    Raises:
    SystemExit: If the directory is empty.
    """

    if not os.listdir(path): sys.exit("Directory is empty")

    files_dict = {}
    for r, d, f in os.walk(path):
        if n_sort:
            f = natural_sort(f)
        for file in f:
            if file_format in file: files_dict.update({file: os.path.join(r, file)})

    return files_dict


def find_isolated_nodes(communities, allFlies):
    """
    Returns isolated nodes (flies) from given snapshot.

    Parameters:
    communities (list): List of communities represented as sets.
    allFlies (list): List of fly names.

    Returns:
    set: Set containing isolated nodes (flies).
    """
    allFlies = set(allFlies)

    currentCommunity = set()
    for community in communities:
        for node in community:
            currentCommunity.add(node)
    
    isolatedNodes = allFlies.difference(currentCommunity)
    return isolatedNodes


# computes Jaccard similarity between two sets.
def jaccard_similarity(set1, set2):
    return len(set1 & set2) / len(set1 | set2)


def track_consistent_communities(snapshots, similarity_threshold=0.5):
    """
    Assigns consistent community IDs across snapshots based on Jaccard similarity.
    
    Parameters:
    snapshots (array): List of snapshots (each snapshot is a list of communities).
    similarity_threshold (float): Jaccard similarity threshold for matching communities.
    
    Returns:
    list: List of snapshots with consistent community IDs.
    """
    community_mapping = {}  # Maps snapshot index -> old community ID -> new consistent ID
    last_assigned_id = 0    # Counter for community IDs
    
    for t, communities in enumerate(snapshots):
        current_mapping = {}  # Mapping for this snapshot
        community_sets = [set(comm) for comm in communities]  # Convert to sets for comparison
        
        if t==0:
            # Assign initial IDs in the first snapshot
            for i, comm in enumerate(community_sets):
                current_mapping[i] = last_assigned_id
                last_assigned_id += 1
        else:
            # Match communities with previous snapshot
            prev_mapping = community_mapping[t-1]
            prev_communities = [set(comm) for comm in snapshots[t-1]]
            
            used_ids = set()  # Track used IDs to prevent duplicate assignments
            
            for i, comm in enumerate(community_sets):
                best_match = None
                best_score = 0

                for j, prev_comm in enumerate(prev_communities):
                    score = jaccard_similarity(comm, prev_comm)
                    if score > best_score and score >= similarity_threshold:
                        best_match = j
                        best_score = score

                if best_match is not None and prev_mapping[best_match] not in used_ids:
                    current_mapping[i] = prev_mapping[best_match]  # Keep the same ID
                    used_ids.add(prev_mapping[best_match])
                else:
                    # Assign new ID if no good match
                    current_mapping[i] = last_assigned_id
                    last_assigned_id += 1
        
        community_mapping[t] = current_mapping  # Store mapping for this snapshot
    
    # Apply new IDs to snapshots
    new_snapshots = []
    for t, communities in enumerate(snapshots):
        sorted_communities = sorted(
            [(community_mapping[t][i], comm) for i, comm in enumerate(communities)],
            key=lambda x: x[0]
        )
        new_snapshots.append([comm for _, comm in sorted_communities])

    return new_snapshots


def get_community_of_node(communities, allFlies):
    """
    Returns community ID in which given node is part of.

    Parameters:
    communities (list): List of communities represented as sets.
    allFlies (list): List of fly names.

    Returns:
    dict: Flies as keys and community ID as values (0 if node isn't part of community).
    """
    communityOfNode = {}
    for fly in allFlies:
        communityOfNode[fly] = 0
        
        for i, community in enumerate(communities):
            # check if fly is within certain community
            if fly in community:
                communityOfNode[fly] = i+1
                break
    
    return communityOfNode


def generate_community_dict(consistentSnapshots, allFlies):
    """
    Returns community dictionary containing community IDs for each fly.

    Parameters:
    consistentSnapshots (list): List of snapshots with consistent community IDs.
    allFlies (list): List of fly names.

    Returns:
    list: List of community distributions for each snapshot.
    """
    communitiesDicts = []

    for communities in consistentSnapshots:
        communityOfNode = get_community_of_node(communities, allFlies)
        communitiesDicts.append(communityOfNode)
    
    return communitiesDicts


def get_heatmap_data(communitiesDict, allFlies, negative):
    """
    Creates NumPy array which can be used to create heatmap
    for visualizing preferences of flies' common communities.

    Parameters:
    communitiesDict (list): List of community distributions for each snapshot.
    allFlies (list): List containing names of all flies.
    negative (bool): Determines whether or not to set the least element of interval to -1 or 0.
    
    Returns:
    numpy array: 2D array containing coefficients of common community preference.
    """
    numOfFlies = len(allFlies)
    npArray = np.zeros((numOfFlies, numOfFlies))

    if negative:
        num = -1
    else:
        num = 0
    numOfSnapshots = len(communitiesDict)

    for snapshot in range(numOfSnapshots):
        for i, fly1 in enumerate(allFlies):
            communityID1 = communitiesDict[snapshot][fly1]
            if communityID1 == 0:
                continue

            for j, fly2 in enumerate(allFlies):
                if fly1 == fly2:
                    continue

                communityID2 = communitiesDict[snapshot][fly2]
                if communityID2 == 0:
                    continue

                if communityID1 == communityID2:
                    npArray[i, j] += 1
                else:
                    npArray[i, j] += num
    
    # normalize matrix elements (divide elements with total number of snapshots)
    return npArray / numOfSnapshots


def statistical_test(dict, automatic):
    """
    Performs statistical test.

    Parameters:
    dict (dict): Dictionary containing coefficients of common community preference for each group.

    Returns:
    int: p-values from tests.
    """
    print()
    p1, p2, p3 = 0, 0, 0
    
    if automatic:
        # check normal distribution
        isSignificant = []
        for group, array in dict.items():
            res = stats.normaltest(array)
            print("{}: p-vrijednost = {}".format(group, res.pvalue))
            isSignificant.append(res.pvalue > 0.05)
        values = list(dict.values())

        # if all p-values are greater than 0.05
        if all(isSignificant):
            print("\nPostoji normalna distribucija - jednosmjerni ANOVA test")
            _, p_value = stats.f_oneway(values[0], values[1], values[2])
        else:
            print("\nNe postoji normalna distribucija - Kruskal-Wallis test")
            _, p_value = stats.kruskal(values[0], values[1], values[2])

        print("P-vrijednost:", p_value)
        if p_value <= 0.05:
            print("Postoji statistički značajna razlika")
        else:
            print("Ne postoji statistički značajna razlika")
    else:
        p1 = stats.ttest_ind(dict["MLADE"], dict["STARE"]).pvalue
        p2 = stats.ttest_ind(dict["STARE"], dict["IZOLIRANE"]).pvalue
        p3 = stats.ttest_ind(dict["MLADE"], dict["IZOLIRANE"]).pvalue

        print("P-vrijednosti:")
        print("MLADE i STARE:", p1)
        print("STARE i IZOLIRANE:", p2)
        print("MLADE i IZOLIRANE:", p3)

    return p1, p2, p3