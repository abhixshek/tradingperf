Track your trading performance metrics.

Broker platforms supported include Kite, Groww and Dhan.

Steps to run the script:
1. Download your P&L statements from any of the above broker platforms
2. In your terminal, run: `python historical_trade_metrics.py [--kite] [--groww] [--dhan]`

To get more information, run: 
````bash
$ python historical_trade_metrics.py -h
usage: historical_trade_metrics.py [-h] [--kite] [--groww] [--dhan]

optional arguments:
  -h, --help  show this help message and exit
  --kite      To read Kite P&L statement
  --groww     To read Groww P&L statement
  --dhan      To read Dhan P&L statement

````
