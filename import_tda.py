from application.frameworks import database
import pandas as pd
from datetime import datetime
import csv
from glob import glob
import os

data_dir = 'account_files'
files = glob(os.path.join(data_dir, '*AccountStatement.csv'))

def generate_contract_name(symbol, exp_dt, contract_type, strike):
    strike_str = str(strike)
    lefts, rights = strike_str.split('.')
    strike_formatted = f'{lefts.zfill(5)}{rights.ljust(3, "0")}'
    return (
        f'{symbol}'
        f'{exp_dt.strftime("%y%m%d")}'
        f'{contract_type[0]}'
        f'{strike_formatted}'
    )

data = []
for f in files:
    r = csv.reader(open(f))
    l = list(r)
    firm = 'TD Ameritrade'
    account_number = l[0][0].split()[3]
    account = f'{firm} - {account_number}'
    s = l.index([x for x in l if x and x[0].startswith('Account Trade')][0])
    se = l[s:].index([])
    e = s + se
    h = l[s+1]
    ll = list(filter(None, l[s+2:e]))
    si = h.index('Symbol')
    for row in ll:
        symbol = row[h.index('Symbol')]
        # exclude futures
        if '/' in symbol: continue
        quantity = abs(int(row[h.index('Qty')]))
        side = row[h.index('Side')]
        prefix = 'B' if side == 'BUY' else 'S'
        pos_effect = row[h.index('Pos Effect')]
        suffix = 'TO' if pos_effect == 'TO OPEN' else 'TC'
        action = prefix + suffix
        date_pre = row[h.index('Exec Time')].strip()
        date_noclock = date_pre.split()[0]
        date_dt = datetime.strptime(date_noclock, '%m/%d/%y')
        contract_type = row[h.index('Type')]
        price_raw = row[h.index('Price')]
        price = float(price_raw) * 100.0 * quantity
        exp_raw = row[h.index('Exp')]
        exp_dt = datetime.strptime(exp_raw, '%d %b %y')
        exp = exp_dt.strftime('%Y-%m-%d')
        strike = float(row[h.index('Strike')])
        symbol = row[h.index('Symbol')]
        contract_name = generate_contract_name(symbol, exp_dt, contract_type, strike)
        cost_basis = price / quantity / 100.0
        extra_fields = {
            'tx_price': price,
            'contract_name': contract_name,
            'date': date_dt,
            'account': account,
            'tx_quantity': quantity,
            'action': action,
            'symbol': symbol,
            'strike': strike,
            'expiration': exp,
            'contract_type': contract_type,
            'tx_cost_basis': cost_basis,
        }
        data.append(extra_fields)

if data:
    df = pd.DataFrame(data)
    #dff = df.sort_values('date').drop_duplicates().copy()
    dff = df.sort_values('date').copy()
    
    db = database.Database()
    dff.to_sql('transactions_tda', db.conn, if_exists='replace', index=False)
