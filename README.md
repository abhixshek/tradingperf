Track your trading performance metrics.

Broker platforms supported include Kite, Groww and Dhan.

Steps to run the script:
1. Download your P&L statements from any of the above broker platforms and save them into ./input/ directory.
2. Update client_id.ini file with your account's Client ID
3. In your terminal, run: `python historical_trade_metrics.py [--kite] [--groww] [--dhan]`

To get more information, run: 
````bash
$ python historical_trade_metrics.py -h
usage: historical_trade_metrics.py [-h] [--kite] [--groww] [--dhan]

optional arguments:
  -h, --help  show this help message and exit
  --kite      read Kite P&L statement
  --groww     read Groww P&L statement
  --dhan      read Dhan P&L statement

````

To view the results and graph, run:
````bash
$ python view.py (--kite | --groww | --dhan | --all)
````

To get more information, run:
````bash
$ python view.py -h
usage: view.py [-h] (--kite | --groww | --dhan | --all)

options:
  -h, --help            show this help message and exit
  --kite                read Kite trade_metrics file
  --groww               read Groww trade_metrics file
  --dhan                read Dhan trade_metrics file
  --all                 read all trade_metrics files to compute net P&L value across all account
````
