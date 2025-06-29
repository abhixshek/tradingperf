import os
import sys
import pandas as pd
import datetime
import time
import argparse
import warnings
warnings.filterwarnings("ignore")


def calc(pnl_file):
    try:
        metrics_df = pd.read_excel(pnl_file, skiprows=36, header=1, usecols='B:N')
    except:
        print('file not found.')
        sys.exit()

    no_of_losing_trades = len(metrics_df[metrics_df['Realized P&L'] <= 0]['Realized P&L'])
    no_of_winning_trades = len(metrics_df[metrics_df['Realized P&L'] > 0]['Realized P&L'])

    avg_loss = metrics_df[metrics_df['Realized P&L'] <= 0]['Realized P&L'].mean()
    avg_gain = metrics_df[metrics_df['Realized P&L'] > 0]['Realized P&L'].mean()

    avg_loss_pct = metrics_df[metrics_df['Realized P&L Pct.'] <= 0]['Realized P&L Pct.'].mean()
    avg_gain_pct = metrics_df[metrics_df['Realized P&L Pct.'] > 0]['Realized P&L Pct.'].mean()

    batting_avg = no_of_winning_trades * 100 / (no_of_winning_trades + no_of_losing_trades)
    win_loss_ratio = -1 * avg_gain_pct / avg_loss_pct
    adj_win_loss_ratio = (-1 * batting_avg * avg_gain_pct) / ((100-batting_avg) * avg_loss_pct)

    realized_pnl = pd.read_excel(pnl_file, skiprows=13, nrows=3, usecols='B:C').iloc[:,1]
    realized_pnl[0] = -1 * realized_pnl[0]
    realized_pnl = realized_pnl.sum()

    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def calc_groww_demat(groww_pnl_file):
    try:
        groww_metrics_df = pd.read_excel(groww_pnl_file, skiprows=24)
    except:
        print('file not found.')
        sys.exit() 

    groww_metrics_df = groww_metrics_df.iloc[:groww_metrics_df.index[groww_metrics_df['Stock name'].isnull()][0], :]
    groww_metrics_df['Realised P&L%'] = 100 * groww_metrics_df.loc[:, 'Realised P&L'] / groww_metrics_df.loc[:, 'Buy value']
    
    no_of_losing_trades = len(groww_metrics_df[groww_metrics_df['Realised P&L'] <= 0]['Realised P&L'])
    no_of_winning_trades = len(groww_metrics_df[groww_metrics_df['Realised P&L'] > 0]['Realised P&L'])
    
    avg_loss = groww_metrics_df[groww_metrics_df['Realised P&L'] <= 0]['Realised P&L'].mean()
    avg_gain = groww_metrics_df[groww_metrics_df['Realised P&L'] > 0]['Realised P&L'].mean()
    
    avg_loss_pct = groww_metrics_df[groww_metrics_df['Realised P&L%'] <= 0]['Realised P&L%'].mean()
    avg_gain_pct = groww_metrics_df[groww_metrics_df['Realised P&L%'] > 0]['Realised P&L%'].mean()
    
    batting_avg = no_of_winning_trades * 100 / (no_of_winning_trades + no_of_losing_trades)
    win_loss_ratio = -1 * avg_gain_pct / avg_loss_pct
    adj_win_loss_ratio = (-1 * batting_avg * avg_gain_pct) / ((100-batting_avg) * avg_loss_pct)
    
    groww_pnl = pd.read_excel(groww_pnl_file, usecols="A:B", index_col=0, nrows=20)
    realized_pnl = -groww_pnl.iloc[11:11+8,0].sum() + groww_metrics_df['Realised P&L'].sum()
    
    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def calc_dhan_demat(dhan_pnl_file='PNL_REPORT.xls'):
    try:
        dhan_df = pd.read_excel('PNL_REPORT.xls', skiprows=13)
    except:
        print(f'file {dhan_pnl_file} not found.')
        sys.exit()

    dhan_df = dhan_df.iloc[: dhan_df.index[dhan_df['Sr.'] == 'F&O Segment'][0], :]
    dhan_df = dhan_df.dropna(subset=['Sr.'])
    dhan_df['Realised P&L%'] = 100 * dhan_df.loc[:, 'Realised P&L'] / dhan_df.loc[:, 'Buy Value']

    no_of_losing_trades = len(dhan_df[dhan_df['Realised P&L'] <= 0]['Realised P&L'])
    no_of_winning_trades = len(dhan_df[dhan_df['Realised P&L'] > 0]['Realised P&L'])

    avg_loss = dhan_df[dhan_df['Realised P&L'] <= 0]['Realised P&L'].mean()
    avg_gain = dhan_df[dhan_df['Realised P&L'] > 0]['Realised P&L'].mean()

    avg_loss_pct = dhan_df[dhan_df['Realised P&L%'] <= 0]['Realised P&L%'].mean()
    avg_gain_pct = dhan_df[dhan_df['Realised P&L%'] > 0]['Realised P&L%'].mean()

    batting_avg = no_of_winning_trades * 100 / (no_of_winning_trades + no_of_losing_trades)
    win_loss_ratio = -1 * avg_gain_pct / avg_loss_pct
    adj_win_loss_ratio = (-1 * batting_avg * avg_gain_pct) / ((100-batting_avg) * avg_loss_pct)

    dhan_pnl_df = pd.read_excel('PNL_REPORT.xls', skiprows=6, nrows=1)
    realized_pnl = -dhan_pnl_df.loc[0, 'Total Charges'] + sum(dhan_df['Realised P&L'])

    return (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)


def kite_trading(pnl_file, date):

    no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl = calc(pnl_file)

    
    y = [(date, no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)]
    rba_df =pd.DataFrame(y, columns=['upto_date', 'no_of_losing_trades', 'no_of_winning_trades', 'avg_loss', 'avg_gain', 'avg_loss_pct', 'avg_gain_pct',
                                     'batting_avg', 'win_loss_ratio', 'adj_win_loss_ratio', 'realized_pnl'])

    try:
        data = pd.read_csv('risk_reward_2025.csv')
        rba_df = pd.concat([data, rba_df], ignore_index=True)
    except:
        pass

    return rba_df


def groww_trading(groww_pnl_file, date):
    (no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct,
     batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl) = calc_groww_demat(groww_pnl_file)
    
    y = [(date, no_of_losing_trades, no_of_winning_trades, avg_loss, avg_gain, avg_loss_pct, avg_gain_pct, batting_avg, win_loss_ratio, adj_win_loss_ratio, realized_pnl)]
    groww_rba_df = pd.DataFrame(y, columns=['upto_date', 'no_of_losing_trades', 'no_of_winning_trades', 'avg_loss', 'avg_gain', 'avg_loss_pct', 'avg_gain_pct',
                                            'batting_avg', 'win_loss_ratio', 'adj_win_loss_ratio', 'realized_pnl'])

    try:
        data = pd.read_csv('risk_reward_2025_groww.csv')
        groww_rba_df = pd.concat([data, groww_rba_df], ignore_index=True)
    except:
        pass

    return groww_rba_df


def dhan_trading(dhan_pnl_file, date):
    (dhan_no_of_losing_trades, dhan_no_of_winning_trades, dhan_avg_loss, dhan_avg_gain, dhan_avg_loss_pct, dhan_avg_gain_pct,
    dhan_batting_avg, dhan_win_loss_ratio, dhan_adj_win_loss_ratio, dhan_realized_pnl) = calc_dhan_demat(dhan_pnl_file)

    y = [(date, dhan_no_of_losing_trades, dhan_no_of_winning_trades, dhan_avg_loss, dhan_avg_gain, dhan_avg_loss_pct, dhan_avg_gain_pct,
         dhan_batting_avg, dhan_win_loss_ratio, dhan_adj_win_loss_ratio, dhan_realized_pnl)]
    dhan_rba_df = pd.DataFrame(y, columns=['upto_date', 'no_of_losing_trades', 'no_of_winning_trades', 'avg_loss', 'avg_gain', 'avg_loss_pct', 'avg_gain_pct',
                                         'batting_avg', 'win_loss_ratio', 'adj_win_loss_ratio', 'realized_pnl'])
    try:
       data = pd.read_csv('risk_reward_2025_dhan.csv')
       dhan_rba_df = pd.concat([data, dhan_rba_df], ignore_index=True)
    except:
       pass

    return dhan_rba_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kite", help="To read Kite P&L statement", action="store_true")
    parser.add_argument("--groww", help="To read Groww P&L statement", action="store_true")
    parser.add_argument("--dhan", help="To read Dhan P&L statement", action="store_true")

    args = parser.parse_args()

    year, month, t_date = time.localtime()[:3]
    date = datetime.date(year, month, t_date)

    kite_pnl_file = ""
    if args.kite:
        rba_df = kite_trading(kite_pnl_file, date)
        rba_df.to_csv('risk_reward_2025.csv', index=False)
        try:
            os.remove(os.path.join(os.getcwd(), kite_pnl_file))
            os.system("copy risk_reward_2025.csv rba_metrics.csv")
        except Exception as e:
            print(e)

    yesterday = date - datetime.timedelta(1)
    yesterday_str = "-".join(yesterday.isoformat().split('-')[::-1]) # yesterday's date as a string in the format DD-MM-YYYY
    groww_client_code = ""
    groww_pnl_file = f"Stocks_PnL_Report_{groww_client_code}_12-10-2024_{yesterday_str}.xlsx"
    if args.groww:
        groww_rba_df = groww_trading(groww_pnl_file, date)
        groww_rba_df.to_csv('risk_reward_2025_groww.csv', index=False)
             
        try:
            os.remove(os.path.join(os.getcwd(), groww_pnl_file))
        except Exception as e:
            print(e)
  
    dhan_pnl_file = 'PNL_REPORT.xls'
    if args.dhan:
        dhan_rba_df = dhan_trading(dhan_pnl_file, date)
        dhan_rba_df.to_csv('risk_reward_2025_dhan.csv', index=False)
        try:
            os.remove(os.path.join(os.getcwd(), dhan_pnl_file))
        except Exception as e:
            print(e)
