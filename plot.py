import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb
import pandas as pd
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
def plot_histogram(groups, measuresDict, type, labels, snapshots):
    x = [groups[0]]*snapshots + [groups[1]]*snapshots + [groups[2]]*snapshots
    measures = list(measuresDict.values())
    df = pd.DataFrame({
        'Grupa':x, 'Girvan-Newman':measures[0], 'Louvain':measures[1]
    })

    # Plot histograms
    axes = df.hist(['Girvan-Newman','Louvain'], by='Grupa',
        layout=(2, 2), xrot=0,
        figsize=(8, 10), rwidth=1)

    for ax in axes.flatten():
        if type == 1:
            plt.title("Histogram veličina zajednica " + labels["weights"])
        elif type == 2:
            plt.title("Histogram izoliranih mušica " + labels["weights"])
        ax.set_xlabel("Veličina zajednica (" + labels["snapshotSize"] + " sekundi)")
        ax.set_ylabel("Broj snimki mreže")
        ax.set_ylim(bottom=0, top=80)

        # display count values on top of each bar
        for bar in ax.patches:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(-1, 1),
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=9)

    if type == 1:
        plt.suptitle("Histogram broja otkrivenih zajednica " + labels["weights"])
    elif type == 2:
        plt.suptitle("Histogram izoliranih mušica " + labels["weights"])
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
