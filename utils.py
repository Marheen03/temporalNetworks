import os, sys, re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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


def find_isolated_nodes(communities, numOfFlies=12):
    """
    Returns isolated nodes (flies) from given snapshot.

    Parameters:
    communities (list): List of communities represented as sets.
    numOfFlies (int): Total number of observed flies.

    Returns:
    set: Set containing isolated nodes (flies).
    """

    allFlies = set()
    for i in range(numOfFlies):
        fly = 'fly' + str(i+1)
        allFlies.add(fly)

    currentCommunity = set()
    for community in communities:
        for node in community:
            currentCommunity.add(node)
    
    isolatedNodes = allFlies.difference(currentCommunity)
    return isolatedNodes


def get_community_of_node(communities, numOfFlies=12):
    """
    Returns community ID in which given node is part of.

    Parameters:
    communities (list): List of communities represented as sets.
    numOfFlies (int): Total number of observed flies.

    Returns:
    dict: flies as keys and community ID as values (0 if node isn't part of community).
    """

    allFlies = []
    for i in range(numOfFlies):
        fly = 'fly' + str(i+1)
        allFlies.append(fly)

    communityOfNode = {}
    for fly in allFlies:
        communityOfNode[fly] = 0
        
        for i, community in enumerate(communities):
            # check if fly is within certain community
            if fly in community:
                communityOfNode[fly] = i+1
                break
    
    return communityOfNode


# creates histogram displaying community sizes for each snapshot
def plotHistogram(dataset, type, communityDetection, usingWeights, snapshots_folder):
    _, _, bars = plt.hist(dataset, bins=range(1, max(dataset)+2),
                               align="left", edgecolor='black', linewidth=1.2)
    plt.xticks(range(1, max(dataset)+2))
    
    # extract heights of the bars
    heights = [bar.get_height() for bar in bars]
    total = sum(heights)  # total count
    
    # add labels with both count and percentage
    for bar, height in zip(bars, heights):
        if height > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, height, 
                    f'{int(height)} ({(height / total * 100):.1f}%)', 
                    ha='center', va='bottom')

    if communityDetection == "girvan_newman":
        detectionAlgorithm = "GN"
    elif communityDetection == "louvain":
        detectionAlgorithm = "LOUVAIN"
    
    if usingWeights:
        weights = "(TEŽINA)"
    else:
        weights = "(BEZ TEŽINE)"

    if type == 'community_size':
        plt.title(detectionAlgorithm + " - histogram veličina zajednica " + weights)
        plt.xlabel("Veličina zajednica")
    elif type == 'isolated_flies':
        plt.title(detectionAlgorithm + " - histogram izoliranih mušica " + weights)
        plt.xlabel("Broj izoliranih mušica")
    
    if snapshots_folder == 'CsCh_10':
        snapshot_size = "10"
    elif snapshots_folder == 'CsCh_30':
        snapshot_size = "30"

    plt.ylabel("Broj snapshotova (" + snapshot_size + " sekundi)")
    plt.show()


# computes Jaccard similarity between two sets.
def jaccard_similarity(set1, set2):
    return len(set1 & set2) / len(set1 | set2)


def track_consistent_communities(snapshots, similarity_threshold=0.5):
    """
    Assigns consistent community IDs across snapshots based on Jaccard similarity.
    
    :param snapshots: List of snapshots (each snapshot is a list of communities).
    :param similarity_threshold: Jaccard similarity threshold for matching communities.
    :return: List of snapshots with consistent community IDs.
    """
    community_mapping = {}  # Maps snapshot index -> old community ID -> new consistent ID
    last_assigned_id = 0    # Counter for community IDs
    
    for t, communities in enumerate(snapshots):
        current_mapping = {}  # Mapping for this snapshot
        community_sets = [set(comm) for comm in communities]  # Convert to sets for comparison
        
        if t == 0:
            # Assign initial IDs in the first snapshot
            for i, comm in enumerate(community_sets):
                current_mapping[i] = last_assigned_id
                last_assigned_id += 1
        else:
            # Match communities with previous snapshot
            prev_mapping = community_mapping[t - 1]
            prev_communities = [set(comm) for comm in snapshots[t - 1]]
            
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


def plotColorMap(communitiesDict):
    # Get unique fly names (assuming they are the same across snapshots)
    flies = list(communitiesDict[0].keys())

    # Convert snapshots into a 2D NumPy array (shape: 12 flies x 120 snapshots)
    data_matrix = np.array([[snapshot[fly] for snapshot in communitiesDict] for fly in flies])

    # Create the heatmap
    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap("tab10", np.max(data_matrix) + 2)  # Adjust colors to match community IDs
    plt.imshow(data_matrix, aspect="auto", cmap=cmap)

    # Labels and formatting
    ticksX = np.arange(0, len(communitiesDict)+1, step=10)
    ticksX[0] += 1
    plt.xticks(ticks=ticksX, labels=ticksX)
    plt.yticks(ticks=np.arange(len(flies)), labels=flies)

    plt.xlabel("Snapshotovi")
    plt.ylabel("Vinske mušice")
    plt.title("Pripadnost mušica zajednicama kroz vrijeme")

    # Modify the label for Community 0
    community_ids = np.unique(data_matrix)  # Unique community IDs
    labels = [f"Izolirana mušica" if i == 0 else f"{i}. zajednica" for i in community_ids]
    patches = [mpatches.Patch(color=cmap(i), label=labels[idx]) for idx, i in enumerate(community_ids)]

    # Create a legend mapping community IDs to colors
    plt.legend(handles=patches, title="Zajednice", bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout(rect=[0.01, 0, 0.97, 1])  # Adjust the paddings
    plt.show()