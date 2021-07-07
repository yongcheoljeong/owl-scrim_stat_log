import pandas as pd 
import numpy as np 
import glob
import os 
from StatAbbr import *
from MySQLConnection import *
from sqlalchemy import exc 
from MapNameList import * 
from tqdm import tqdm

class PETH():
    def __init__(self, FinalStatName=None):
        self.set_import_type()
        self.set_search_condition()
        self.set_period()
        if FinalStatName is None: 
            pass 
        else:
            self.FinalStatName = FinalStatName

    def set_import_type(self, import_type='sql'):
        self.import_type = import_type 

    def set_df_init(self):
        if self.import_type == 'sql': # import FinalStat from sql
            dbname = 'scrimloganalysis'
            tablename = 'finalstat'
            match_id = self.FinalStatName.split('_')[0] + '_' + self.FinalStatName.split('_')[1]
            mapname = self.FinalStatName.split('_')[3].split('.')[0]
            if mapname in mapname_typocorrection.keys():
                mapname = mapname_typocorrection[mapname]
            if mapname in mapnamelist: 
                num_map = 1
            else: 
                num_map = mapname[-1]
            sql = f'SELECT * FROM {tablename} WHERE `MatchId`="{match_id}" AND `num_map`={num_map} AND `Map`="{mapname}";'
            print(sql)
            self.df_init = pd.read_sql(sql=sql, con=MySQLConnection(dbname=dbname).engine)
            # self.df_init = MySQLConnection(dbname='scrim_finalstat').read_table_as_df(self.FinalStatName)
        elif self.import_type == 'csv': # improt FinalStat from csv
            self.FinalStatCsvName = self.FinalStatName
            path_FinalStat = r'G:\공유 드라이브\NYXL Scrim Log\FinalStat'
            FinalStat = pd.read_csv(os.path.join(path_FinalStat, self.FinalStatCsvName))
            self.df_init = FinalStat.reset_index()

    def set_search_condition(self, event_name='FinalBlows/s', threshold=1):
        if event_name is None: 
            pass 
        else: 
            self.event_name = event_name 
            self.threshold = threshold
            self.stat_name_abbr = StatAbbr[self.event_name] # Abbreviation of event_name

    def set_period(self, period=10):
        if period is None: 
            pass 
        else: 
            self.period = period 

    def find_events(self):
        self.set_df_init()
        df_event_onset = self.df_init[self.df_init[self.event_name] >= self.threshold]
        
        return df_event_onset

    def set_PETH(self):
        df_event_onset = self.find_events()
        
        if len(df_event_onset) == 0: # event가 한 번도 일어나지 않았을 때
            df_PETH = pd.DataFrame({'MatchId':[], 'num_map':[], 'Map':[], 'Section':[], 'RoundName':[], 'num_Event':[], 'ref_Team':[], 'ref_Player':[], 'ref_Hero':[], 'ref_Event':[], 'Team':[], 'Player':[], 'Hero':[], 'Timestamp':[]})
        else:
            idx_col = ['MatchId', 'Map', 'Section', 'RoundName', 'Team', 'Player', 'Hero', 'Timestamp']
            num_Event = 0
            df_list = []
            for multi_idx, row in df_event_onset.iterrows():
                num_Event += 1
                # set reference vars
                ref_match_id = row['MatchId']
                ref_map_name = row['Map']
                ref_team_name = row['Team']
                ref_player_name = row['Player']
                ref_hero_name = row['Hero']

                # align FinalStat by event onset
                event_onset = row['Timestamp']
                df_event_recorder = self.df_init[(self.df_init['Timestamp'] >= (event_onset - (self.period + 1))) & (self.df_init['Timestamp'] <= (event_onset + (self.period + 1)))]
                df_event_recorder = df_event_recorder.copy() # make a copy to avoid SettingWithCopyWarning
                df_event_recorder['EventOnset'] = event_onset
                df_event_recorder['Timestamp'] -= event_onset
                df_event_recorder['Timestamp'] = df_event_recorder['Timestamp'].astype(int) # Timestamp 소숫점 자리 버림
                
                # reference columns
                df_event_recorder['ref_Team'] = ref_team_name
                df_event_recorder['ref_Player'] = ref_player_name
                df_event_recorder['ref_Hero'] = ref_hero_name
                df_event_recorder['ref_Event'] = self.event_name
                df_event_recorder['num_Event'] = num_Event 

                # concat
                df_list.append(df_event_recorder)

            df_PETH = pd.concat(df_list)            
            df_PETH = df_PETH.set_index(['MatchId', 'num_map', 'Map', 'Section', 'RoundName', 'num_Event', 'ref_Team', 'ref_Player', 'ref_Hero', 'ref_Event', 'Team', 'Player', 'Hero', 'Timestamp'])

        return df_PETH 

    def get_PETH(self):
        df_PETH = self.set_PETH()

        return df_PETH

    def export_to_csv(self, save_dir=r'G:\공유 드라이브\NYXL Scrim Log\PETH'):
        # Transform event_name to Abbr
        self.get_PETH().to_csv(save_dir + f'/PETH_{self.stat_name_abbr}_{self.FinalStatCsvName}')

    def update_PETH(self, save_dir=r'G:\공유 드라이브\NYXL Scrim Log\PETH'):
        # set path
        filepath = r'G:\공유 드라이브\NYXL Scrim Log\FinalStat'
        filelist = os.listdir(filepath)
        csv_filelist = [x for x in filelist if x.endswith('.csv')]
        updated_csv = f'FilesUpdated_{self.stat_name_abbr}.txt'
        
        # open updated filelist
        f = open(os.path.join(filepath, updated_csv), 'r+')
        lines = f.readlines()
        updated_filelist = []

        for line in lines:
            updated_filelist.append(line.replace('\n', ''))

        # sort files to be updated
        csv_filelist_to_update = list(set(csv_filelist) - set(updated_filelist))
        csv_filelist_to_update.sort()

        # export to csv in PETH folder
        for filename in csv_filelist_to_update:
            file_PETH = PETH(filename)
            file_PETH.set_search_condition(event_name=self.event_name, threshold=self.threshold)
            file_PETH.export_to_csv()

            f.write(filename+'\n')
            print(f'File Exported: {filename}')

        f.close()
    
    def update_PETH_to_sql(self):
        def get_filelist_all(): 
            # set path
            filepath = r'G:/공유 드라이브/NYXL Scrim Log/Csv/'
            filelist = os.listdir(filepath)
            csv_filelist = [x for x in filelist if x.endswith('.csv')]

            return csv_filelist
            
        def get_filelist_updated():
            filepath = r'G:/공유 드라이브/NYXL Scrim Log/Csv/'
            updated_csv = f'FilesUpdated_{self.stat_name_abbr}_MySQL.txt'
            f = open(os.path.join(filepath, updated_csv), 'r+')
            lines = f.readlines()
            updated_filelist = []

            for line in lines:
                updated_filelist.append(line.replace('\n', ''))
            
            f.close()
            
            return updated_filelist

        filelist_FinalStat = get_filelist_all() # all filelist
        filelist_updated = get_filelist_updated() # updated filelist

        # sort files to be updated
        filelist_to_update = list(set(filelist_FinalStat) - set(filelist_updated))
        filelist_to_update.sort()

        # export
        filepath = r'G:/공유 드라이브/NYXL Scrim Log/Csv/'
        updated_csv = f'FilesUpdated_{self.stat_name_abbr}_MySQL.txt'
        for filename in tqdm(filelist_to_update):
            f = open(os.path.join(filepath, updated_csv), 'a')
            file_PETH = PETH(filename)
            file_PETH.set_import_type('sql')
            file_PETH.set_search_condition(event_name=self.event_name, threshold=self.threshold)
            input_PETH = file_PETH.get_PETH()
            df_sql = MySQLConnection(input_df=input_PETH.reset_index(), dbname='scrimloganalysis') # reset_index to export to mysql db
            print('Data Exporting...')
            try: # Insert dataframe into DB except duplicated primary keys
                df_sql.export_to_db(table_name='peth', if_exists='append')
                f.write(filename+'\n')
                print(f'File Exported: {filename}_{file_PETH.stat_name_abbr} to {df_sql.dbname}')
            except exc.IntegrityError:
                f.write(filename+'\n') 
                print('IntegrigyError')
            f.close()