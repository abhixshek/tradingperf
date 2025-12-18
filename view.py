import sys
import webbrowser
from colorama import Back, Fore, Style
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


def plot_metric(data, metric='realized_pnl'):
    plt.figure(facecolor=(0.8, 0.8, 0.8), figsize=(12, 12))
    plt.plot(data['upto_date'], data[metric], "b")
    spacing = 20 if len(data) > 100 else 10
    plt.xticks(data['upto_date'][::spacing], rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # today = datetime.now()
    # filename = '{}_{}_{}'.format(today.year, today.month, today.day)
    # plt.savefig(f'{filename}.png')

    # webbrowser.open('https://console.zerodha.com/verified/') #TODO make it configurable, passed by user


def display(data):
    # data['return'] = data.loc[:,'realized_pnl'] / e * 100
    # data = data[['upto_date','no_of_losing_trades','no_of_winning_trades','avg_loss','avg_gain',
    # 'avg_loss_pct','avg_gain_pct','batting_avg','win_loss_ratio','adj_win_loss_ratio']]
    # print(data.to_string())
    # print()

    win_loss_ratio = data.loc[len(data) - 1, "win_loss_ratio"]
    batting_avg = data.loc[len(data) - 1, "batting_avg"]
    if win_loss_ratio < 3.0:
        idx_last_row = len(data) - (data.to_string()[::-1].find('\n') + 1)
        print(data.to_string()[:idx_last_row + 1] + Fore.RED + data.to_string()[idx_last_row + 1:] + Style.RESET_ALL)
    else:
        print(data.to_string())
    print()
    avg_loss = data.loc[len(data) - 1, "avg_loss"]
    print(
        "In a market that is giving, your base/typical positions should be "
        + Fore.YELLOW + f"{-avg_loss * 100 / 5:.2f}" + Style.RESET_ALL
    )

    plot_metric(data)


def display_net_pnl():
    output_dir = Path('.') / 'output'

    for idx, file in enumerate(output_dir.glob('trade_metrics*')):
        metric_df = pd.read_csv(file)[['upto_date', 'realized_pnl']]
        broker = file.name.split(".")[0].split("_")[-1]
        metric_df.columns = ['upto_date', f'realized_pnl_{broker}']
        if idx == 0:
            final_df = metric_df
        else:
            final_df = final_df.merge(metric_df, on="upto_date", how="outer")

    for col in final_df.columns:
        final_df.loc[:final_df[col].first_valid_index() - 1, col] = 0

    final_df = final_df.ffill()
    net_pnl = final_df.iloc[:, 1:].values.sum(axis=1)
    final_df['net'] = net_pnl

    plot_metric(final_df, 'net')


if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--kite", help="read Kite trade_metrics file", action="store_true")
    group.add_argument("--groww", help="read Groww trade_metrics file", action="store_true")
    group.add_argument("--dhan", help="read Dhan trade_metrics file", action="store_true")
    group.add_argument("--all", help="read all trade_metrics files to compute net P&L value across all accounts", action="store_true")

    args = parser.parse_args()

    if args.kite:
        metrics_file = 'trade_metrics_kite.csv'
    elif args.groww:
        metrics_file = 'trade_metrics_groww.csv'
    elif args.dhan:
        metrics_file = 'trade_metrics_dhan.csv'
    elif args.all:
        metrics_files = ['trade_metrics_kite.csv', 'trade_metrics_groww.csv', 'trade_metrics_dhan.csv']

    if not args.all:
        data = pd.read_csv(Path('.') / 'output' / metrics_file)
        display(data)
    elif args.all:
        display_net_pnl()
