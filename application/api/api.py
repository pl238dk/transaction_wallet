print(__name__)
#from flask import current_app as app
from flask import render_template
from flask import request
from flask import Blueprint
#from application.app import framework
from application.app import database
from datetime import datetime
import pandas as pd
import json

bp_api = Blueprint(
    'bp_api',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/api/static',
)

def derive_contract_name(symbol, exp, contract_type, strike):
    date_dt = datetime.strptime(exp, '%Y-%m-%d')
    date = date_dt.strftime('%y%m%d')
    strike_fl = float(strike)
    strike_str = str(strike_fl)
    lefts, rights = strike_str.split('.')
    strike_formatted = f'{lefts.zfill(5)}{rights.ljust(3, "0")}'
    output = (
        f'{symbol}'
        f'{date}'
        f'{contract_type.upper()[0]}'
        f'{strike_formatted}'
    )
    return output

@bp_api.route('/api')
def api():
    return render_template(
        'api.html',
    )

# Account

@bp_api.route('/api/account/get')
def api_account_get():
    with database.Database() as db:
        output = db.query_table('accounts')
    return json.dumps(output)

@bp_api.route('/api/account/set')
def api_account_set():
    args = request.args
    firm = args.get('firm')
    account_type = args.get('account_type')
    nickname = args.get('nickname')
    
    row_data = {
        'firm': firm,
        'account_type': account_type,
        'nickname': nickname,
    }
    
    with database.Database() as db:
        output = db.insert_row('accounts', row_data)
        # backup
        df_backup = pd.read_sql_query('SELECT * FROM accounts', db.conn)
        df_backup.to_csv('accounts.csv')
    return json.dumps(output)

@bp_api.route('/api/account/delete')
def api_account_delete():
    args = request.args
    account_id = args.get('id')
    
    with database.Database() as db:
        output = db.delete_row('accounts', account_id)
    return json.dumps(output)

# Transaction

@bp_api.route('/api/transaction/get')
def api_transaction_get():
    with database.Database() as db:
        output = db.query_table('open_contracts')
    return json.dumps(output)

@bp_api.route('/api/transaction/set')
def api_transaction_set():
    args = request.args
    def two_digit_float(value):
        fl = float(value)
        return f'{fl:.02f}'
    row_data = {
        'date': args.get('tx_date'),
        'symbol': args.get('symbol'),
        'account': args.get('account'),
        'action': args.get('action'),
        'strike': args.get('strike'),
        'contract_type': args.get('contract_type'),
        'expiration': args.get('expiration'),
        'tx_quantity': args.get('tx_quantity'),
        'tx_price': args.get('tx_price'),
    }
    account_raw = row_data['account']
    date = datetime.strptime(row_data['date'], '%Y-%m-%d')
    firm_idx = account_raw.index(' - ')
    firm = account_raw[:firm_idx]
    account = account_raw[firm_idx+3:]
    contract_name = derive_contract_name(
        row_data['symbol'],
        row_data['expiration'],
        row_data['contract_type'],
        row_data['strike'],
    )
    cost_basis = float(row_data['tx_price']) / float(row_data['tx_quantity']) / 100.0
    price = float(row_data['tx_price'])
    strike = float(row_data['strike'])
    quantity_int = int(row_data['tx_quantity'])
    row_data.update({
        'account': account,
        'date': date,
        'tx_price': price,
        'strike': strike,
        'tx_quantity': quantity_int,
        'contract_name': contract_name,
        #'tx_cost_basis': two_digit_float(cost_basis),
        'tx_cost_basis': cost_basis,
    })
    print(row_data)
    df = pd.DataFrame([row_data])
    print(df)
    with database.Database() as db:
        if firm == 'Fidelity':
            #output = db.insert_row('transactions_fid', row_data)
            db.insert_row_via_df('transactions_fid', df)
            # backup
            df_backup = pd.read_sql_query('SELECT * FROM transactions_fid', db.conn)
            df_backup.to_csv('transactions_fid.csv')
        elif firm == 'TD Ameritrade':
            #output = db.insert_row('transactions_tda', row_data)
            db.insert_row_via_df('transactions_tda', df)
            # backup
            df_backup = pd.read_sql_query('SELECT * FROM transactions_tda', db.conn)
            df_backup.to_csv('transactions_tda.csv')
        else:
            print('unknown brokerage')
    return {}

@bp_api.route('/api/transaction/delete')
def api_transaction_delete():
    args = request.args
    transaction_id = args.get('id')
    firm_raw = args.get('account')
    firm = firm_raw.split(' - ')[0]
    print(firm, firm_raw, transaction_id)
    with database.Database() as db:
        if firm == 'Fidelity':
            output = db.delete_row('transactions_fid', transaction_id)
        elif firm == 'TD Ameritrade':
            output = db.delete_row('transactions_tda', transaction_id)
        else:
            print('unknown brokerage')
            output = {}
    return json.dumps(output)