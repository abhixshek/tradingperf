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


def calc_kite(pnl_file):
    try:
        metrics_df = pd.read_excel(Path('input') / pnl_file, skiprows=36, header=1, usecols='B:N')
    except:
        print(f'{pnl_file} not found.')
        sys.exit()

    loss_condition = metrics_df['Realized P&L'] <= 0
    win_condition = np.logical_not(loss_condition)
    
    no_of_losing_trades = loss_condition.sum()
    no_of_winning_trades = win_condition.sum()

    avg_loss = metrics_df.loc[loss_condition, 'Realized P&L'].mean()
    avg_gain = metrics_df.loc[win_condition, 'Realized P&L'].mean()

    avg_loss_pct = metrics_df.loc[loss_condition, 'Realized P&L Pct.'].mean()
    avg_gain_pct = metrics_df.loc[win_condition, 'Realized P&L Pct.'].mean()

    batting_avg, win_loss_ratio, adj_win_loss_ratio = calculate_ratios(no_of_losing_trades, no_of_winning_trades,
                                                                       avg_loss_pct, avg_gain_pct)

    realized_pnl = pd.read_excel(Path('input') / pnl_file, skiprows=13, nrows=3, usecols='B:C').iloc[:,1]
    realized_pnl[0] = -1 * realized_pnl[0]
    realized_pnl = realized_pnl.sum()

    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
            batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def calc_groww(groww_pnl_file):
    try:
        groww_metrics_df = pd.read_excel(Path('input') / groww_pnl_file, skiprows=24)
    except:
        print(f'{groww_pnl_file} not found.')
        sys.exit() 

    groww_metrics_df = groww_metrics_df.iloc[:groww_metrics_df.index[groww_metrics_df['Stock name'].isnull()][0], :]
    groww_metrics_df['Realised P&L%'] = 100 * groww_metrics_df.loc[:, 'Realised P&L'] / groww_metrics_df.loc[:, 'Buy value']

    loss_condition = groww_metrics_df['Realised P&L'] <= 0
    win_condition = np.logical_not(loss_condition)

    no_of_losing_trades = loss_condition.sum()
    no_of_winning_trades = win_condition.sum()
    
    avg_loss = groww_metrics_df.loc[loss_condition, 'Realised P&L'].mean()
    avg_gain = groww_metrics_df.loc[win_condition, 'Realised P&L'].mean()
    
    avg_loss_pct = groww_metrics_df.loc[loss_condition, 'Realised P&L%'].mean()
    avg_gain_pct = groww_metrics_df.loc[win_condition, 'Realised P&L%'].mean()

    batting_avg, win_loss_ratio, adj_win_loss_ratio = calculate_ratios(no_of_losing_trades, no_of_winning_trades,
                                                                       avg_loss_pct, avg_gain_pct)
    
    groww_pnl = pd.read_excel(Path('input') / groww_pnl_file, usecols="A:B", index_col=0, nrows=20)
    realized_pnl = -groww_pnl.iloc[11:11+8,0].sum() + groww_metrics_df['Realised P&L'].sum()
    
    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
            batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def calc_dhan(dhan_pnl_file='PNL_REPORT.xls'):
    try:
        dhan_df = pd.read_excel(Path('input') / 'PNL_REPORT.xls', skiprows=13)
    except:
        print(f'file {dhan_pnl_file} not found.')
        sys.exit()

    dhan_df = dhan_df.iloc[: dhan_df.index[dhan_df['Sr.'] == 'F&O Segment'][0], :]
    dhan_df = dhan_df.dropna(subset=['Sr.'])
    dhan_df['Realised P&L%'] = 100 * dhan_df.loc[:, 'Realised P&L'] / dhan_df.loc[:, 'Buy Value']

    loss_condition = dhan_df['Realised P&L'] <= 0
    win_condition = np.logical_not(loss_condition)

    no_of_losing_trades = loss_condition.sum()
    no_of_winning_trades = win_condition.sum()

    avg_loss = dhan_df.loc[loss_condition, 'Realised P&L'].mean()
    avg_gain = dhan_df.loc[win_condition, 'Realised P&L'].mean()

    avg_loss_pct = dhan_df.loc[loss_condition, 'Realised P&L%'].mean()
    avg_gain_pct = dhan_df.loc[win_condition, 'Realised P&L%'].mean()

    batting_avg, win_loss_ratio, adj_win_loss_ratio = calculate_ratios(no_of_losing_trades, no_of_winning_trades,
                                                                       avg_loss_pct, avg_gain_pct)

    dhan_pnl_df = pd.read_excel(Path('input') / 'PNL_REPORT.xls', skiprows=6, nrows=1)
    realized_pnl = -dhan_pnl_df.loc[0, 'Total Charges'] + sum(dhan_df['Realised P&L'])

    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
            batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def create_historical_df(pnl_file, date, broker, calc_function):
    (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct,
     avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl) = calc_function(pnl_file)
    
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
    groww_pnl_file = f"Stocks_PnL_Report_{groww_client_code}_12-10-2024_{yesterday_str}.xlsx"
    # TODO 12-10-2024 is a hard-coded date. it wont apply to other users of your code

    dhan_pnl_file = 'PNL_REPORT.xls'
    input_pnl_files = {
        'kite': kite_pnl_file,
        'groww': groww_pnl_file,
        'dhan': dhan_pnl_file
    }

    calc_functions = {
        'kite': calc_kite,
        'groww': calc_groww,
        'dhan': calc_dhan
    }

    for broker in broker_args_passed:
        print(f"Running through {broker[0]} data")
        pnl_file = input_pnl_files[broker[0]]
        calc_function = calc_functions[broker[0]]
        rba_df = create_historical_df(pnl_file, date, broker[0], calc_function)
        rba_df.to_csv(Path('output') / f'trade_metrics_{broker[0]}.csv', index=False)
        try:
            os.remove(os.path.join(os.getcwd(), 'input', pnl_file))
            # os.system("copy risk_reward_2025.csv rba_metrics.csv")
        except Exception as e:
            print(e)

    print("\nData processing complete.")
    print("Application closing...")
