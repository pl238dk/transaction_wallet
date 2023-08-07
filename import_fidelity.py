from application.frameworks import database
import pandas as pd
from datetime import datetime
import csv
from glob import glob
import os

data_dir = 'account_files'
files = glob(os.path.join(data_dir, 'Accounts_History*.csv'))

def parse_contract_name(contract_name):
    output = {}
    name = contract_name.split('-')[1]
    #output['contract_name'] = name
    digits = [x.isdigit() for x in name]
    di = digits.index(True)
    symbol = name[:di]
    rest = name[di:]
    #
    letters = [x.isalpha() for x in rest]
    li = letters.index(True)
    exp_flat = rest[:li]
    if len(exp_flat) > 6:
        char = exp_flat[0]
        symbol += char
        exp_flat = exp_flat[1:]
    expp = datetime.strptime(exp_flat, '%y%m%d')
    exppp = expp.strftime('%Y-%m-%d')
    rest = rest[li:]
    #
    digits = [x.isdigit() for x in rest]
    di = digits.index(True)
    contract_type = rest[:di]
    strike = rest[di:]
    if '.' in strike:
        strike_real = float(strike)
    else:
        strike_real = float(strike[:5] + '.' + strike[5:])
    #
    strike_str = str(strike_real)
    lefts, rights = strike_str.split('.')
    strike_formatted = f'{lefts.zfill(5)}{rights.ljust(3, "0")}'
    contract_name_real = (
        f'{symbol}'
        f'{expp.strftime("%y%m%d")}'
        f'{contract_type[0]}'
        f'{strike_formatted}'
    )
    output['symbol'] = symbol
    output['expiration'] = exppp
    output['strike'] = strike_real
    output['contract_name'] = contract_name_real
    output['contract_type'] = 'CALL' if contract_type == 'C' else 'PUT'
    return output

dates_seen = {}
df = []
for f in files:
    data = []
    r = csv.reader(open(f))
    l = list(r)
    firm = 'Fidelity'
    s = l.index([x for x in l if x and x[0].startswith('Run')][0])
    e = l.index([x for x in l if x and x[0].startswith('The ')][0])
    h = l[s]
    ll = list(filter(None, l[s+1:e]))
    si = h.index('Symbol')
    options_only = [x for x in ll if x[si].startswith(' -')]
    for row in options_only:
        extra_fields = parse_contract_name(row[si])
        row_action = row[h.index('Action')]
        if 'BOUGHT' in row_action:
            prefix = 'B'
        elif 'SOLD' in row_action:
            prefix = 'S'
        elif 'EXPIRED' in row_action:
            prefix = 'S'
        elif 'ASSIGNED' in row_action:
            prefix = 'B'
        else:
            prefix = '?'
        if 'OPENING' in row_action:
            suffix = 'TO'
        elif 'CLOSING' in row_action:
            suffix = 'TC'
        elif 'EXPIRED' in row_action:
            suffix = 'TC'
        elif 'ASSIGNED' in row_action:
            suffix = 'TC'
        else:
            suffix = '??'
        action = prefix + suffix
        quantity = int(row[h.index('Quantity')])
        #if quantity == 0: print(row, 'zero quantity')
        date_pre = row[h.index('Run Date')].strip()
        date_dt = datetime.strptime(date_pre, '%m/%d/%Y')
        if date_pre not in dates_seen:
            dates_seen[date_pre] = f
        else:
            if dates_seen[date_pre] != f: continue
        #date = date_dt.strftime('%Y-%m-%d')
        price_raw = row[h.index('Amount ($)')]
        #if not price_raw: print(row, 'no price_raw')
        ###print(row[si], quantity, price_raw)
        price = float(price_raw) if price_raw else 0.0
        account_number = row[h.index('Account')]
        account = f'{firm} - {account_number}'
        cost_basis = abs(price) / abs(quantity) / 100.0
        extra_fields.update({
            'tx_price': abs(price),
            'date': date_dt,
            'account': row[h.index('Account')],
            'tx_quantity': abs(quantity),
            'tx_cost_basis': cost_basis,
            'action': action,
        })
        data.append(extra_fields)
    if len(data) == 0: continue
    if len(df) == 0:
        df = pd.DataFrame(data)
    else:
        df_file = pd.DataFrame(data)
        df = df.merge(df_file, "outer")

if len(df) > 0:
    #df = pd.DataFrame(data)
    #dff = df.sort_values('date').drop_duplicates().copy()
    dff = df.sort_values('date').copy()
    
    db = database.Database()
    dff.to_sql('transactions_fid', db.conn, if_exists='replace', index=False)

###
###
###
#
# add other fields like cost basis
#
###
###
###