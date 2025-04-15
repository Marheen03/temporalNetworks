import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb


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
        weights = "(S TEŽINOM)"
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


# create colormap for flies' community distribution
def plotColorMap(communitiesDict, communityDetection, usingWeights, snapshots_folder):
    # get unique fly names
    flies = list(communitiesDict[0].keys())

    # convert snapshots into a 2D NumPy array (shape: 12 flies x 120 snapshots)
    data_matrix = np.array([[snapshot[fly] for snapshot in communitiesDict] for fly in flies])

    # create the colormap
    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap("tab10", np.max(data_matrix) + 2)  # adjust colors to match community IDs
    plt.imshow(data_matrix, aspect="auto", cmap=cmap)

    # Labels and formatting
    ticksX = np.arange(0, len(communitiesDict)+1, step=10)
    ticksX[0] += 1
    plt.xticks(ticks=ticksX, labels=ticksX)
    plt.yticks(ticks=np.arange(len(flies)), labels=flies)

    if snapshots_folder == 'CsCh_10':
        snapshot_size = "10"
    elif snapshots_folder == 'CsCh_30':
        snapshot_size = "30"
    
    if communityDetection == "girvan_newman":
        detectionAlgorithm = "GN"
    elif communityDetection == "louvain":
        detectionAlgorithm = "LOUVAIN"
    
    if usingWeights:
        weights = "(S TEŽINOM)"
    else:
        weights = "(BEZ TEŽINE)"

    plt.xlabel("Snapshotovi (" + snapshot_size + " sekundi)")
    plt.ylabel("Vinske mušice")
    plt.title(detectionAlgorithm + " - Pripadnost mušica zajednicama kroz vrijeme " + weights)

    # modify the label for Community 0
    community_ids = np.unique(data_matrix)  # Unique community IDs
    labels = [f"Izolirana mušica" if i == 0 else f"{i}. zajednica" for i in community_ids]
    patches = [mpatches.Patch(color=cmap(i), label=labels[idx]) for idx, i in enumerate(community_ids)]

    # create a legend mapping community IDs to colors
    plt.legend(handles=patches, title="Zajednice", bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout(rect=[0.01, 0, 0.97, 1])  # Adjust the paddings
    plt.show()


# create bar chart for flies in identical communities
def plotBarChart(fliesInTop3, communityDetection, usingWeights, snapshots_folder):
    plt.bar(fliesInTop3.keys(), fliesInTop3.values())
    if snapshots_folder == 'CsCh_10':
        snapshot_size = "10"
    elif snapshots_folder == 'CsCh_30':
        snapshot_size = "30"
    
    if communityDetection == "girvan_newman":
        detectionAlgorithm = "GN"
    elif communityDetection == "louvain":
        detectionAlgorithm = "LOUVAIN"
    
    if usingWeights:
        weights = "(S TEŽINOM)"
    else:
        weights = "(BEZ TEŽINE)"
    
    plt.title(detectionAlgorithm + " - Najčešće mušice u istoj zajednici " + weights)
    plt.xlabel('Mušice (snapshot od ' + snapshot_size +  ' sekundi)')
    plt.ylabel('Broj nalaska u top 3')
    plt.show()


# create heatmap for flies' preference
def plotHeatMap(df, communityDetection, usingWeights, snapshots_folder):
    if snapshots_folder == 'CsCh_10':
        snapshot_size = "10"
    elif snapshots_folder == 'CsCh_30':
        snapshot_size = "30"
    
    if communityDetection == "girvan_newman":
        detectionAlgorithm = "GN"
    elif communityDetection == "louvain":
        detectionAlgorithm = "LOUVAIN"
    
    if usingWeights:
        weights = "(S TEŽINOM)"
    else:
        weights = "(BEZ TEŽINE)"
    
    _, ax = plt.subplots(figsize=(10,5))
    sb.heatmap(df, annot=True, linewidths=.5, ax=ax)
    
    plt.title(detectionAlgorithm + " - Preferencije zajedničkih mušica " + weights)
    plt.xlabel('Mušice (snapshot od ' + snapshot_size +  ' sekundi)')
    plt.ylabel('Mušice (snapshot od ' + snapshot_size +  ' sekundi)')
    plt.show()