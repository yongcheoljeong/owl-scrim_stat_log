import pandas as pd 
import numpy as np 
import glob
import os 
from StatAbbr import *

class PETH():
    def __init__(self, FinalStatCsvName=None):
        self.set_search_condition()
        self.set_period()
        if FinalStatCsvName is None: 
            pass 
        else: 
            self.FinalStatCsvName = FinalStatCsvName 
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
        df_event_onset = self.df_init[self.df_init[self.event_name] >= self.threshold]
        
        return df_event_onset

    def set_PETH(self):
        df_event_onset = self.find_events()
        idx_col = ['MatchId', 'Map', 'Section', 'RoundName', 'Team', 'Player', 'Hero', 'Timestamp']
        df_PETH = pd.DataFrame()
        for multi_idx, row in df_event_onset.iterrows():
            # set reference vars
            ref_match_id = row['MatchId']
            ref_map_name = row['Map']
            ref_team_name = row['Team']
            ref_player_name = row['Player']
            ref_hero_name = row['Hero']

            # align FinalStat by event onset
            event_onset = row['Timestamp']
            df_event_recorder = self.df_init[(self.df_init['Timestamp'] >= (event_onset - (self.period + 1))) & (self.df_init['Timestamp'] <= (event_onset + (self.period + 1)))]
            df_event_recorder['Timestamp'] -= event_onset
            df_event_recorder['Timestamp'] = df_event_recorder['Timestamp'].astype(int) # Timestamp 소숫점 자리 버림
            
            # reference columns
            df_event_recorder['ref_Team'] = ref_team_name
            df_event_recorder['ref_Player'] = ref_player_name
            df_event_recorder['ref_Hero'] = ref_hero_name
            df_event_recorder['ref_Event'] = self.event_name

            # concat
            df_PETH = pd.concat([df_PETH, df_event_recorder], ignore_index=True)

        df_PETH = df_PETH.set_index(['MatchId', 'Map', 'Section', 'RoundName', 'ref_Team', 'ref_Player', 'ref_Hero', 'ref_Event', 'Team', 'Player', 'Hero', 'Timestamp'])

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
        # csv_filelist = glob.glob(os.path.join(filepath, 'FinalStat_*.csv'))
        updated_csv = f'FilesUpdated_{self.stat_name_abbr}.txt'
        
        # open updated filelist
        f = open(os.path.join(filepath, updated_csv), 'r+')
        lines = f.readlines()
        updated_filelist = []

        for line in lines:
            updated_filelist.append(line.replace('\n', ''))

        # sort files to be updated
        csv_filelist_to_export = list(set(csv_filelist) - set(updated_filelist))

        # export to csv in PETH folder
        for filename in csv_filelist_to_export:
            file_PETH = PETH(filename)
            file_PETH.set_search_condition(event_name=self.event_name, threshold=self.threshold)
            file_PETH.export_to_csv()

            f.write(filename+'\n')
            print(f'File Exported: {filename}')

        f.close()