import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb


# create histogram displaying community sizes for each snapshot
def plot_histogram(dataset, type, labels):
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

    if type == 'community_size':
        plt.title(labels["detectionAlgorithm"] + " - histogram veličina zajednica " + labels["weights"])
        plt.xlabel("Veličina zajednica (" + labels["type"] + ")")
    elif type == 'isolated_flies':
        plt.title(labels["detectionAlgorithm"] + " - histogram izoliranih mušica " + labels["weights"])
        plt.xlabel("Broj izoliranih mušica (" + labels["type"] + ")")

    plt.ylabel("Broj snapshotova (" + labels["snapshotSize"] + " sekundi)")
    plt.show()


# create grouped bar plot based on given data
def plot_grouped_bar_plot(measuresDict, groups, labels, type):
    x = np.arange(len(groups))  # the label locations
    width = 0.4  # the width of the bars
    
    for i, array in enumerate(list(measuresDict.values())):
        if i==0:
            position_shift = x-0.2
        else:
            position_shift = x+0.2

        plt.bar(position_shift, array, width)

        # add labels on top of bars
        for xpos, height in zip(position_shift, array):
            plt.text(xpos, height + 0.1, str(height),
                     ha='center', va='bottom', fontsize=10)

    plt.xticks(x, groups)
    plt.legend(
        list(measuresDict.keys()),
        bbox_to_anchor=(1.05, 1), 
        loc='upper left',
        title='Algoritmi',
        borderaxespad=0.
    )
    
    plt.xlabel('Grupe ('+ labels["snapshotSize"] +' sekundi)')
    if type==1:
        plt.ylabel('Broj otkrivenih zajednica')
        plt.title("Broj otkrivenih zajednica po algoritmima "+ labels["weights"])
    elif type==2:
        plt.ylabel('Broj izoliranih mušica')
        plt.title("Broj izoliranih mušica po algoritmima "+ labels["weights"])
    else:
        plt.ylabel('Veličina najveće zajednice')
        plt.title("Veličina najveće zajednice po algoritmima "+ labels["weights"])

    plt.tight_layout()
    plt.show()


# create colormap for flies' community distribution
def plot_colormap(communitiesDict, labels, id):
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

    plt.xlabel("Snapshotovi (" + labels["snapshotSize"] + " sekundi)")
    plt.ylabel("Vinske mušice (" + labels["type"] + ")")
    plt.title(labels["detectionAlgorithm"] + " - Pripadnost mušica zajednicama kroz vrijeme " + labels["weights"])

    # modify the label for Community 0
    community_ids = np.unique(data_matrix)  # Unique community IDs
    labels = [f"Izolirana mušica" if i == 0 else f"{i}. zajednica" for i in community_ids]
    patches = [mpatches.Patch(color=cmap(i), label=labels[idx]) for idx, i in enumerate(community_ids)]

    # create a legend mapping community IDs to colors
    plt.legend(handles=patches, title="Zajednice", bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout(rect=[0.01, 0, 0.97, 1])  # Adjust the paddings
    plt.show()


# create bar chart for flies in identical communities
def plot_bar_chart(fliesInTop3, labels):
    plt.bar(fliesInTop3.keys(), fliesInTop3.values())
    plt.title(labels["detectionAlgorithm"] + " - Najčešće mušice u istoj zajednici " + labels["weights"])
    
    plt.xlabel('Mušice (' + labels["type"] + ')')
    plt.ylabel('Broj nalaska u top 3 (snapshotovi od ' + labels["snapshotSize"] +  ' sekundi)')
    plt.show()


# create heatmap for flies' preference
def plot_heatmap(df, labels, negative):
    if negative:
        num = -1
    else:
        num = 0
    
    _, ax = plt.subplots(figsize=(10,5))
    sb.heatmap(df, vmin=num, vmax=1, annot=True, linewidths=.5, ax=ax)
    
    plt.title(labels["detectionAlgorithm"] + " - Preferencije zajedničkih mušica " + labels["weights"] + ", " + labels["snapshotSize"] + " sekundi")
    plt.xlabel('Mušice (' + labels["type"] + ')')
    plt.ylabel('Mušice (' + labels["type"] + ')')
    plt.show()


# create boxplot for distribution visualization
def plot_boxplot(data, type, directed, accumulated, type1=''):
    """
    if multiple:
        fig, _ = plt.subplots(4, 5, figsize=(11, 8))
        fig.tight_layout(pad=4)

        for i, dataDict in enumerate(data):
            plt.subplot(4, 5, i+1)
            plt.boxplot(dataDict.values(), labels=dataDict.keys())
            plt.ylim(0, 1)

            plt.title("{}. opservacija".format(i+1))

        plt.suptitle("Distribucija koeficijenta preferencije (" + type + "), " + directed)    
    """
    plt.figure(figsize=(8, 6))
    plt.boxplot(data.values(), labels=data.keys())

    plt.ylim(0, 1)
    if accumulated == False:
        plt.xlabel('Redni broj tretmana (' + type1 + ')')
    plt.ylabel('Vrijednosti ' + directed)
    plt.title("Distribucija koeficijenta preferencije (" + type + ")")
    
    plt.show()
