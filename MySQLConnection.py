import pymysql
from sqlalchemy import create_engine 
import pandas as pd 

class MySQLConnection():
    def __init__(self, input_df, dbname='scrim_finalstat', hostname='221.151.212.225', username='imt', pwd='gpdlzjadh', port=3306):
        # define input_df
        self.input_df = input_df
        # dbname
        self.dbname = dbname
        # create engine
        self.engine = create_engine('mysql+pymysql://' + username + ':' + pwd + '@' + hostname + ':' + str(port) + '/' + dbname , echo=False)

    def export_to_db(self, table_name, if_exists='replace'):
        table_name = table_name.lower() # MySQL DB에서 table 이름을 자동으로 소문자로 바꿔주기 때문에 'replace' 기능 쓰려면 필수
        self.input_df.to_sql(name=table_name, con=self.engine, schema=self.dbname, if_exists=if_exists) # if_exsits:{'fail', 'replace', 'append'}