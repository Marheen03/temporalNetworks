import os, sys, re
import networkx as nx


# returns array containing all flies
def getAllFlies(numOfFlies):
    allFlies = []
    for i in range(numOfFlies):
        flyString = 'fly' + str(i+1)
        allFlies.append(flyString)
    
    return allFlies


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
    allFlies (array): Array of fly names.

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


def get_community_of_node(communities, allFlies):
    """
    Returns community ID in which given node is part of.

    Parameters:
    communities (list): List of communities represented as sets.
    allFlies (array): Array of fly names.

    Returns:
    dict: flies as keys and community ID as values (0 if node isn't part of community).
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
    array: List of snapshots with consistent community IDs.
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


def shared_communites(fly, communitiesDict, allFlies):
    """
    Counts occurences when chosen fly was in identical community with all flies
    through all snapshots.
    
    Parameters:
    fly (string): List of snapshots (each snapshot is a list of communities).
    communitiesDict (array): Array of community distributions for each snapshot.
    allFlies (array): Array containing names of all flies.
    
    Returns:
    dict: Flies as keys and number of occurences in the same community as values.
    """
    allFliesCopy = [flyCopy for flyCopy in allFlies if flyCopy != fly]
    mutual_flies = {key : 0 for key in allFliesCopy}

    for i in range(len(communitiesDict)):
        communityID = communitiesDict[i][fly]

        for flyCopy in allFliesCopy:
            if communitiesDict[i][flyCopy] == communityID:
                mutual_flies[flyCopy] += 1
    
    return mutual_flies
