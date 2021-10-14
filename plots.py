from typing import List

import matplotlib.pyplot as plt
import numpy as np


def loot_pie(values: List, labels: List) -> None:
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%', pctdistance=0.8)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()


def loot_bars(values: List, labels: List) -> None:
    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = np.arange(len(labels))

    ax.barh(y_pos, values, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Loot')
    ax.set_title('Loot Assignment Totals')

    plt.show()
