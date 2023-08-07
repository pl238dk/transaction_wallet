print(__name__)
import sqlite3
import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('wsgi_wallet.db')
        self.cur = self.conn.cursor()
        self.initialize()
        return
    
    def __enter__(self):
        self.conn = sqlite3.connect('wsgi_wallet.db')
        self.cur = self.conn.cursor()
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return
    
    def initialize(self):
        self.create_table_accounts()
        self.create_table_transactions()
        return
    
    def commit(self):
        self.conn.commit()
        return
    
    def create_table(self, table_name, columns_dict):
        columns_list = [f'{key} {columns_dict[key]}' for key in columns_dict]
        columns_data = ', '.join(columns_list)
        query = (
            f'CREATE TABLE IF NOT EXISTS '
            f'{table_name} '
            f'('
            f'{columns_data}'
            f');'
        )
        self.cur.execute(query)
        self.commit()
        return
    
    def create_table_accounts(self):
        table_name = 'accounts'
        columns_dict = {
            'id': 'INTEGER PRIMARY KEY',
            'firm': 'TEXT',
            'account_type': 'TEXT',
            'nickname': 'TEXT',
        }
        self.create_table(table_name, columns_dict)
        return
    
    def create_table_transactions(self):
        table_name = 'transactions_full'
        columns_dict = {
            'id': 'INTEGER PRIMARY KEY',
            'date': 'TEXT',
            'account': 'TEXT',
            'symbol': 'TEXT',
            'expiration': 'TEXT',
            'strike': 'REAL',
            'contract_name': 'TEXT',
            'action': 'TEXT',
            'contract_type': 'TEXT',
            'tx_quantity': 'INTEGER',
            'total_quantity': 'INTEGER',
            'tx_price': 'REAL',
            'total_price': 'REAL',
            'tx_profit': 'REAL',
            'tx_cost_basis': 'REAL',
            'total_cost_basis': 'REAL',
            'sell_credit': 'REAL',
            'buy_debit': 'REAL',
            'final_credit_debit': 'REAL',
            'still_invested': 'REAL',
            'percent_profit': 'REAL',
            'violation': 'TEXT',
            'violation_time': 'TEXT',
            'violation_count': 'TEXT',
        }
        self.create_table(table_name, columns_dict)
        return
    
    def delete_row(self, table_name, row_id):
        query = (
            f'DELETE FROM '
            f'{table_name} '
            f'WHERE '
            f'rowid == '
            f'{row_id}'
            f';'
        )
        self.cur.execute(query)
        self.commit()
        return
    
    def insert_row(self, table_name, row_dict):
        row_keys = list(row_dict.keys())
        row_keys_data = ', '.join(row_keys)
        row_values = [val.__repr__() for val in row_dict.values()]
        row_values_data = ', '.join(row_values)
        query = (
            f'INSERT INTO '
            f'{table_name} '
            f'('
            f'{row_keys_data}'
            f') VALUES ('
            f'{row_values_data}'
            f');'
        )
        self.cur.execute(query)
        self.commit()
        return
    
    def insert_row_via_df(self, table_name, df):
        df.to_sql(table_name, self.conn, if_exists='append', index=False)
        return
    
    def query_table(self, table_name):
        query = (
            f'SELECT * FROM '
            f'{table_name}'
        )
        query_result = self.cur.execute(query)
        results = query_result.fetchall()
        desc = self.cur.description
        columns = [col[0] for col in desc]
        output = [dict(zip(columns, row)) for row in results]
        return output
    
    def sweep_transactions(self):
        #txs = self.query_transactions()
        
        return