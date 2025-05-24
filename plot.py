import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb
from matplotlib import patches as mpatches


# create grouped bar plot based on given data
def plot_grouped_bar(measuresDict, groups, labels, type, snapshots):
    x = np.arange(len(groups))  # the label locations
    width = 0.4  # the width of the bars
    
    for i, array in enumerate(list(measuresDict.values())):
        if i==0:
            position_shift = x-0.2
        else:
            position_shift = x+0.2

        plt.bar(position_shift, array, width)

        # add labels on top of bars: count (percentage %)
        for xpos, height in zip(position_shift, array):
            average = height / snapshots
            plt.text(xpos, height + 0.1, f"{int(height)} ({average:.2f})",
                     ha='center', va='bottom', fontsize=9)

    plt.xticks(x, groups)
    plt.legend(
        list(measuresDict.keys()),
        loc='lower right',
        title='Algoritmi',
    )
    
    plt.xlabel('Grupe ('+ labels["snapshotSize"] +' sekundi)')
    if type==1:
        plt.ylabel('Broj otkrivenih zajednica')
        plt.title("Broj otkrivenih zajednica po algoritmima "+ labels["weights"])
    elif type==2:
        plt.ylabel('Broj izoliranih mušica')
        plt.title("Broj izoliranih mušica po algoritmima "+ labels["weights"])

    plt.tight_layout()
    plt.show()


# create histograms
def plot_histogram(measuresDict, type, labels, snapshots):
    fig, _ = plt.subplots(1, 3, figsize=(15, 5))
    fig.tight_layout(pad=4)

    for i, (group, data) in enumerate(measuresDict.items()):
        plt.subplot(1, 3, i+1)
        _, _, bars = plt.hist(data, bins=range(1, max(data)+2),
                               align="left", edgecolor='black', linewidth=1.2)
        plt.xticks(range(1, max(data)+2))
        
        # extract heights of the bars
        heights = [bar.get_height() for bar in bars]
        # add labels with both count and percentage
        for bar, height in zip(bars, heights):
            if height > 0:
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.8, 
                    f'{int(height)} ({(height / snapshots * 100):.1f}%)', 
                    ha='center', va='bottom', fontsize=7
                )
        plt.title(group)

    if type == 1:
        plt.suptitle(labels["detectionAlgorithm"] + " - histogram broja otkrivenih zajednica " + labels["weights"])
        xlabel = "Broj otkrivenih zajednica ("+ labels["snapshotSize"] +" sekundi)"
    elif type == 2:
        plt.suptitle(labels["detectionAlgorithm"] + " - histogram broja izoliranih mušica " + labels["weights"])
        xlabel = "Broj izoliranih mušica (" + labels["snapshotSize"] + " sekundi)"
    
    fig.supxlabel(xlabel)
    fig.supylabel("Broj snimaka mreža")

    plt.show()


# create colormap for flies' community distribution
def plot_colormap(communitiesDicts, labels, allFlies):
    # convert snapshots into a 2D NumPy array (shape: number of flies x number of snapshots)
    data_matrix = np.array([[snapshot[fly] for snapshot in communitiesDicts] for fly in allFlies])

    # create the colormap
    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap("tab10", np.max(data_matrix) + 1)  # adjust colors to match community IDs
    plt.imshow(data_matrix, aspect="auto", cmap=cmap)

    # labels and formatting
    ticksX = np.arange(0, len(communitiesDicts)+1, step=10)
    ticksX[0] += 1
    plt.xticks(ticks=ticksX, labels=ticksX)
    plt.yticks(ticks=np.arange(len(allFlies)), labels=allFlies)

    plt.xlabel("Redni broj snimka mreže (" + labels["snapshotSize"] + " sekundi)")
    plt.ylabel("Nazivi mušica")
    plt.title(
        labels["detectionAlgorithm"] +
        " - Pripadnost mušica zajednicama kroz vrijeme " +
        labels["weights"] + " (" + labels["type"] + ")"
    )

    # modify the label for community 0 (isolated node)
    community_ids = np.unique(data_matrix)
    labels = [f"Izolirana mušica" if i == 0 else f"{i}. zajednica" for i in community_ids]
    patches = [mpatches.Patch(color=cmap(i), label=labels[idx]) for idx, i in enumerate(community_ids)]

    # create a legend mapping community IDs to colors
    plt.legend(handles=patches, title="Zajednice", bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout(rect=[0.01, 0, 0.97, 1])  # adjust the paddings
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
def plot_boxplot(dataDict, type, directed, accumulated, type1=''):
    plt.figure(figsize=(8, 6))
    plt.boxplot(dataDict.values(), labels=dataDict.keys())

    plt.ylim(0, 1)
    if accumulated == False:
        plt.xlabel('Redni broj tretmana (' + type1 + ')')
    plt.ylabel('Vrijednosti ' + directed)
    plt.title("Distribucija koeficijenta preferencije (" + type + ")")
    
    plt.show()
