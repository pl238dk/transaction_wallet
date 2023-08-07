from application.frameworks import database
import pandas as pd

with database.Database() as db:
    #output = db.query_table('accounts')
    df = pd.read_sql_query('SELECT * FROM transactions', db.conn)
    df.to_csv('transactions.csv')
    df = pd.read_sql_query('SELECT * FROM transactions_fid', db.conn)
    df.to_csv('transactions_fid.csv')
    df = pd.read_sql_query('SELECT * FROM transactions_tda', db.conn)
    df.to_csv('transactions_tda.csv')
    df = pd.read_sql_query('SELECT * FROM accounts', db.conn)
    df.to_csv('accounts.csv')