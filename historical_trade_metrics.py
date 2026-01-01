#!.venv/Scripts/python

import os
import sys
import numpy as np
import pandas as pd
import datetime
import time
import argparse
import configparser
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")


def calculate_ratios(no_of_losing_trades, no_of_winning_trades, avg_loss_pct, avg_gain_pct):
    batting_avg = no_of_winning_trades * 100 / (no_of_winning_trades + no_of_losing_trades)
    win_loss_ratio = -1 * avg_gain_pct / avg_loss_pct
    adj_win_loss_ratio = (-1 * batting_avg * avg_gain_pct) / ((100 - batting_avg) * avg_loss_pct)

    return batting_avg, win_loss_ratio, adj_win_loss_ratio


def read_pnl_file(pnl_file, broker):
    if broker == 'kite':
        try:
            pnl_df = pd.read_excel(Path('input') / pnl_file, skiprows=36, header=1, usecols='B:N')
        except:
            print(f'{pnl_file} not found.')
            sys.exit()
    
    elif broker == 'groww':
        try:
            pnl_df = pd.read_excel(Path('input') / pnl_file, skiprows=24)
        except:
            print(f'{pnl_file} not found.')
            sys.exit()

        pnl_df = pnl_df.iloc[:pnl_df.index[pnl_df['Stock name'].isnull()][0], :]
        pnl_df['Realized P&L Pct.'] = 100 * pnl_df.loc[:, 'Realised P&L'] / pnl_df.loc[:, 'Buy value']
    
    elif broker == 'dhan':
        try:
            pnl_df = pd.read_excel(Path('input') / pnl_file, skiprows=13)
        except:
            print(f'file {pnl_file} not found.')
            sys.exit()
        
        pnl_df = pnl_df.iloc[: pnl_df.index[pnl_df['Sr.'] == 'F&O Segment'][0], :]
        pnl_df = pnl_df.dropna(subset=['Sr.'])
        pnl_df['Realized P&L Pct.'] = 100 * pnl_df.loc[:, 'Realised P&L'] / pnl_df.loc[:, 'Buy Value']
    
    pnl_df = pnl_df.rename(columns={"Realised P&L": "Realized P&L"})

    return pnl_df


def calculate_total_charges(pnl_file, broker):
    if broker == 'kite':
        all_charges = pd.read_excel(Path('input') / pnl_file, skiprows=13, nrows=2, usecols='B:C').iloc[:,1]
        all_charges = all_charges.apply(lambda x: -x if x > 0 else x)
        total_charges = all_charges.sum()

    elif broker == 'groww':
        groww_pnl = pd.read_excel(Path('input') / pnl_file, usecols="A:B", index_col=0, nrows=20)
        total_charges = -groww_pnl.iloc[11:11+8,0].sum()
    
    elif broker == 'dhan':
        dhan_pnl_df = pd.read_excel(Path('input') / pnl_file, skiprows=6, nrows=1)
        total_charges = -dhan_pnl_df.loc[0, 'Total Charges']
    
    return total_charges


def calculate_metrics(pnl_df, total_charges=0):
    realized_pnl = total_charges + pnl_df['Realized P&L'].sum()

    loss_condition = pnl_df['Realized P&L'] <= 0
    win_condition = np.logical_not(loss_condition)
    
    no_of_losing_trades = loss_condition.sum()
    no_of_winning_trades = win_condition.sum()

    avg_loss = pnl_df.loc[loss_condition, 'Realized P&L'].mean()
    avg_gain = pnl_df.loc[win_condition, 'Realized P&L'].mean()

    avg_loss_pct = pnl_df.loc[loss_condition, 'Realized P&L Pct.'].mean()
    avg_gain_pct = pnl_df.loc[win_condition, 'Realized P&L Pct.'].mean()

    batting_avg, win_loss_ratio, adj_win_loss_ratio = calculate_ratios(no_of_losing_trades, no_of_winning_trades,
                                                                       avg_loss_pct, avg_gain_pct)

    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
            batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def create_historical_df(pnl_file, date, broker):
    pnl_df = read_pnl_file(pnl_file, broker)
    total_charges = calculate_total_charges(pnl_file, broker)

    (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct,
     avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl) = calculate_metrics(pnl_df, total_charges)
    
    y = [(date, no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
          batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)]
    rba_df = pd.DataFrame(y, columns=['upto_date', 'no_of_losing_trades', 'no_of_winning_trades',
                                      'avg_loss', 'avg_gain', 'avg_loss_pct', 'avg_gain_pct',
                                      'batting_avg', 'win_loss_ratio', 'adj_win_loss_ratio', 'realized_pnl'])

    try:
        data = pd.read_csv(Path('output') / f'trade_metrics_{broker}.csv')
    except FileNotFoundError:
        print(f"No historical trade metrics data found for {broker} account.")
        print("New trade metrics file will be generated.")
        return rba_df

    rba_df = pd.concat([data, rba_df], ignore_index=True)

    return rba_df


if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--kite", help="read Kite P&L statement", action="store_true")
    parser.add_argument("--groww", help="read Groww P&L statement", action="store_true")
    parser.add_argument("--dhan", help="read Dhan P&L statement", action="store_true")

    args = parser.parse_args()
    all_brokers = args._get_kwargs()
    broker_args_passed = list(filter(lambda x: x[1], all_brokers))

    # parse configuration from user
    config = configparser.ConfigParser()
    config.read('client_id.ini')

    year, month, t_date = time.localtime()[:3]
    date = datetime.date(year, month, t_date)

    kite_pnl_file = 'pnl-{0}.xlsx'.format(config['client.id']['kiteclientid'])

    yesterday = date - datetime.timedelta(1)
    yesterday_str = "-".join(yesterday.isoformat().split('-')[::-1]) # yesterday's date as a string in the format DD-MM-YYYY
    groww_client_code = config['client.id']['growwclientcode']
    groww_valid_input_files = list(Path('input').glob(f'Stocks_PnL_Report_{groww_client_code}_*{yesterday_str}.xlsx'))
    groww_pnl_file = groww_valid_input_files[0].name if groww_valid_input_files else ''

    dhan_pnl_file = 'PNL_REPORT.xls'
    input_pnl_files = {
        'kite': kite_pnl_file,
        'groww': groww_pnl_file,
        'dhan': dhan_pnl_file
    }

    for broker in broker_args_passed:
        print(f"Running through {broker[0]} data")
        pnl_file = input_pnl_files[broker[0]]
        rba_df = create_historical_df(pnl_file, date, broker[0])
        rba_df.to_csv(Path('output') / f'trade_metrics_{broker[0]}.csv', index=False)
        try:
            os.remove(os.path.join(os.getcwd(), 'input', pnl_file))
            # os.system("copy risk_reward_2025.csv rba_metrics.csv")
        except Exception as e:
            print(e)

    print("\nData processing complete.")
    print("Application closing...")
