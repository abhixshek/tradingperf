import sys
import webbrowser
from colorama import Back, Fore, Style
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path


if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--kite", help="Reads trade_metrics file", action="store_true")
    group.add_argument("--groww", help="Reads trade_metrics file", action="store_true")
    group.add_argument("--dhan", help="Reads trade_metrics file", action="store_true")

    args = parser.parse_args()

    if args.kite:
        metrics_file = 'trade_metrics_kite.csv'
    elif args.groww:
        metrics_file = 'trade_metrics_groww.csv'
    elif args.dhan:
        metrics_file = 'trade_metrics_dhan.csv'

    data = pd.read_csv(Path('.') / 'output' / metrics_file)

    # data['return'] = data.loc[:,'realized_pnl'] / e * 100
    # data = data[['upto_date','no_of_losing_trades','no_of_winning_trades','avg_loss','avg_gain','avg_loss_pct','avg_gain_pct','batting_avg','win_loss_ratio','adj_win_loss_ratio']]
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
    print("In a market that is giving, your base/typical positions should be " + Fore.YELLOW + f"{-avg_loss * 100 / 5:.2f}" + Style.RESET_ALL)

    df = pd.read_csv(Path('.') / 'output' / metrics_file)
    plt.figure()
    plt.plot(df['upto_date'], df['realized_pnl'], "b")
    plt.xticks(df['upto_date'][::10],rotation=45)
    #plt.yticks(np.arange(-120000, df['realized_pnl'].max() + 100000, 20000))
    plt.grid(True)
    plt.show()
    # webbrowser.open('https://console.zerodha.com/verified/') #TODO make it configurable, passed by user
