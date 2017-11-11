import os
import sys

import numpy as np
import requests
try:
    from tqdm import tqdm
except ImportError:
    from va_efficiency.constants import tqdm

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

from va_efficiency.constants import X_JITTER, LABELS, OFFICE_IDS, PROJECT_ROOT
from va_efficiency.data import get_data_for_office


def calculate_efficiency_gap(df):
    terms = list(df.index.levels[0])
    efficiency_gaps = []
    for term in df.index.levels[0]:
        sub_df = df.loc[term]
        efficiency_gaps.append((sub_df['r_wasted'].sum() - sub_df['d_wasted'].sum()) / sub_df['total_votes'].sum())

    return terms, efficiency_gaps


def plot_efficiency_gap(terms, efficiency_gaps, ax, office):
    padded_terms = np.array(terms + [2020]) + X_JITTER[office]
    gaps = np.array(efficiency_gaps + [efficiency_gaps[-1]]) * 100

    ax.step(padded_terms, gaps, where='post', label=LABELS[office])


def main(fname=None, fig_ax=None):
    if fig_ax is None:
        fig, ax = plt.subplots(1, 1)
    else:
        fig, ax = fig_ax

    max_gap = 0
    session = requests.Session()
    for office in tqdm(sorted(OFFICE_IDS)):
        df = get_data_for_office(office, session=session)
        terms, gaps = calculate_efficiency_gap(df)
        max_gap = max(max_gap, max(gaps))
        plot_efficiency_gap(terms, gaps, ax, office)

    ax.set_xlabel('Decade')
    ax.set_ylabel('Efficiency gap, +ve benefits D\n(partisan difference in wasted vote as % of total vote)')
    max_gap = max_gap * 100 + 5
    ax.set_ylim(-max_gap, max_gap)

    ax.axhline(8, linestyle=':', linewidth=1, color='b', label=f'Suggested limit (D)')
    ax.axhline(-8, linestyle=':', linewidth=1, color='r', label='Suggested limit (R)')
    ax.axhline(0, linestyle='--', color='k', label='Parity')

    ax.set_title('VA efficiency gap by districting period, 1947 - 2016')

    ax.legend()
    fig.set_size_inches(12, 8)
    fig.tight_layout()
    if fname:
        plt.savefig(fname, dpi=600)


if __name__ == '__main__':
    fname = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_ROOT, 'figure.png')
    main(fname)
    plt.show()
