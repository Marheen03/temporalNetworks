import os, sys, re, networkx as nx

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
    dict: flies as keys and community ID as values (-1 if node isn't part of community).
    """

    allFlies = []
    for i in range(numOfFlies):
        fly = 'fly' + str(i+1)
        allFlies.append(fly)

    communityOfNode = {}
    for fly in allFlies:
        for i, community in enumerate(communities):
            # check if fly is within certain community
            if fly in community:
                communityOfNode[fly] = i+1
                break
            communityOfNode[fly] = -1
    
    return communityOfNode