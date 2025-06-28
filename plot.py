import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb


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
def plot_histogram(measuresDict, type, labels):
    fig, _ = plt.subplots(1, 3, figsize=(15, 5))
    fig.tight_layout(pad=4)

    for i, (group, data) in enumerate(measuresDict.items()):
        plt.subplot(1, 3, i+1)

        if type in [1, 3]:
            minValue = 1
        elif type == 2:
            minValue = 0

        _, _, bars = plt.hist(data, bins=range(minValue, max(data)+2),
                               align="left", edgecolor='black', linewidth=1.2)
        plt.xticks(range(minValue, max(data)+2))
        
        # extract heights of the bars
        heights = [bar.get_height() for bar in bars]
        totalHeight = sum(heights)
        # add labels with both count and percentage
        for bar, height in zip(bars, heights):
            if height > 0:
                plt.text(
                    bar.get_x() + bar.get_width() / 2 + 0.15,
                    height + 0.2,
                    f'{int(height)} ({(height / totalHeight * 100):.1f}%)', 
                    ha='center', va='bottom', fontsize=6
                )
        plt.title(group)

    if type == 1:
        plt.suptitle(labels["detectionAlgorithm"] + " - histogram broja otkrivenih zajednica " + labels["weights"])
        xlabel = "Broj otkrivenih zajednica ("+ labels["snapshotSize"] +" sekundi)"
    elif type == 2:
        plt.suptitle(labels["detectionAlgorithm"] + " - histogram broja izoliranih mušica " + labels["weights"])
        xlabel = "Broj izoliranih mušica (" + labels["snapshotSize"] + " sekundi)"
    elif type == 3:
        plt.suptitle(labels["detectionAlgorithm"] + " - histogram veličina otkrivenih zajednica " + labels["weights"])
        xlabel = "Veličina zajednica (" + labels["snapshotSize"] + " sekundi)"
    
    fig.supxlabel(xlabel)
    fig.supylabel("Broj snimaka mreža")
    plt.show()


# create colormap
def plot_colormap(dict, labels, allFlies):
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), constrained_layout=False)
    fig.subplots_adjust(hspace=0.5, left=0.08, right=0.85, top=0.92)
    cmap = plt.get_cmap("tab10")

    for i, (group, communitiesDicts) in enumerate(dict.items()):
        data_matrix = np.array([[snapshot[fly] for snapshot in communitiesDicts] for fly in allFlies])
        ax = axes[i]

        # Show the community heatmap
        ax.imshow(data_matrix, aspect="auto", cmap=cmap, vmin=0, vmax=9)
        ax.set_title(group)

        # X ticks
        ticksX = np.arange(0, len(communitiesDicts)+1, step=10)
        ticksX[0] = 1
        ax.set_xticks(ticksX)
        ax.set_xticklabels(ticksX)

        # Y ticks
        ax.set_yticks(np.arange(len(allFlies)))
        ax.set_yticklabels(allFlies)

        # creates separate legend for subplot
        community_ids = np.unique(data_matrix)
        legend_labels = [f"Izolirana mušica" if j == 0 else f"{j}. zajednica" for j in community_ids]
        patches = [mpatches.Patch(color=cmap(j), label=legend_labels[k]) for k, j in enumerate(community_ids)]

        ax.legend(
            handles=patches,
            title="Zajednice",
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            borderaxespad=0.
        )

    fig.supxlabel("Redni broj snimka mreže (" + labels["snapshotSize"] + " sekundi)", fontsize=12)
    fig.supylabel("Nazivi mušica", fontsize=12)
    fig.suptitle(
        labels["detectionAlgorithm"] +
        " - Pripadnost mušica zajednicama kroz vrijeme " + labels["weights"],
        fontsize=14,
        y=0.98
    )
    plt.show()


# create heatmap for flies' preference
def plot_heatmap(matrixDict, labels, negative):
    if negative:
        num = -1
    else:
        num = 0

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.tight_layout(pad=5)
    axes_flat = axes.flatten()

    for i, (group, df) in enumerate(matrixDict.items()):
        ax = axes_flat[i]
        sb.heatmap(
            df, vmin=num, vmax=1, annot=True, linewidths=.5, ax=ax,
            annot_kws={"fontsize": 9}
        )
        ax.set_title(group)

    # hide the unused subplot (the 4th one)
    if len(matrixDict) < 4:
        axes_flat[-1].axis('off')

    # set a main title for the entire figure
    fig.suptitle(
        labels["detectionAlgorithm"] + " - Preferencije zajedničkih mušica " +
        labels["weights"] + ", " + labels["snapshotSize"] + " sekundi",
        fontsize=14
    )
    fig.supxlabel('Mušice', fontsize=12)
    fig.supylabel('Mušice', fontsize=12)

    plt.show()


# create boxplot for distribution visualization
def plot_boxplot(dicts, labels, accumulated, p_values):
    if accumulated:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.boxplot(dicts.values(), labels=dicts.keys())
        ax.set_ylim(0, 1)

        add_significance_bars(ax, p_values[0], 1, 2, 0.73)
        add_significance_bars(ax, p_values[1], 2, 3, 0.78)
        add_significance_bars(ax, p_values[2], 1, 3, 0.83)
        
        ax.set_xlabel('Grupa mušica ('+ labels["snapshotSize"] +" sekundi)")
        ax.set_ylabel('Koeficijenti preferencije')
        ax.set_title("Distribucija koeficijenta preferencije po grupama ("+ 
                  labels["detectionAlgorithm"] + ") "+ labels["weights"])
    else:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.tight_layout(pad=4)

        for i, (group, dataDict) in enumerate(dicts.items()):
            ax = axes[i]
            ax.boxplot(dataDict.values(), labels=dataDict.keys())
            ax.set_ylim(0, 1)
            ax.set_title(group)

        fig.text(0.5, 0.04, 'Redni broj promatranja ('+ labels["snapshotSize"] +' sekundi)',
                 ha='center', fontsize=12)
        fig.text(0.04, 0.5, 'Koeficijent preferencije', va='center',
                 rotation='vertical', fontsize=12)
        plt.suptitle("Distribucija koeficijenta preferencije po promatranjima ("+
                     labels["detectionAlgorithm"] + ") "+ labels["weights"])
        plt.subplots_adjust(top=0.9, bottom=0.11, left=0.1, right=0.95)
    plt.show()


# Add significance bars with custom symbols and sizes based on p-value.
def add_significance_bars(ax, p_value, x1, x2, y):
    y_offset = 0.02
    ax.plot([x1, x1, x2, x2], [y, y + y_offset, y + y_offset, y], color='black')
    
    if p_value < 0.001:
        ax.text((x1 + x2) / 2, y + y_offset + 0.005, '***', fontsize=16, ha='center', color='red')
    elif p_value < 0.01:
        ax.text((x1 + x2) / 2, y + y_offset + 0.005, '**', fontsize=16, ha='center', color='orange')
    elif p_value < 0.05:
        ax.text((x1 + x2) / 2, y + y_offset + 0.005, '*', fontsize=16, ha='center', color='green')