from abc import *
import pandas as pd 

class AdvancedStat(metaclass=ABCMeta):
    def __init__(self, input_df=None):
        self.stat_category: str = 'AdvancedStat'
        stat_level: str # Match, Map, Section, Team, Player, Hero
        stat_name: str
        self.input_df = input_df
        self.idx_col = ['Match_id', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    @abstractmethod
    def ready_df_init(self):
        pass

    @abstractmethod
    def define_df_stat(self):
        pass

    @abstractmethod
    def merge_df_result(self):
        pass

    @abstractmethod 
    def get_df_result(self):
        pass


class RCPv1(AdvancedStat):
    '''
    Relative Combat Power version 1
    '''
    def __init__(self, input_df=None):
        self.stat_level = 'Team'
        self.stat_name = 'RCP'
        self.stat_version = '1.0'
        self.idx_col = ['MatchId', 'Map', 'Section', 'Timestamp', 'Team']
        self.input_df = input_df

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['NumAlive']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        team_name_list = df_init['Team'].unique()
        team_one_name = 'NYE'
        team_two_name = [x for x in team_name_list if x != team_one_name]

        print(team_one_name, team_two_name)

        # team_one_NumAlive (NYE)
        team_one_NumAlive = df_init[df_init['Team'] == 'NYE']
        team_one_NumAlive = team_one_NumAlive.groupby(by=self.idx_col).max()

        display(team_one_NumAlive)

        # team_two_NumAlive (Opponent)
        team_two_NumAlive = df_init[df_init['Team'] != 'NYE']
        team_two_NumAlive = team_two_NumAlive.groupby(by=self.idx_col).max()

        display(team_two_NumAlive)

        df_stat = pd.merge(team_one_NumAlive, team_two_NumAlive, how='outer', on=[x for x in self.idx_col if x not in ['Team']], suffixes=(f'_{team_one_name}', f'_{team_two_name}'))
        df_stat[f'{self.stat_name}'] = (df_stat[f'NumAlive_{team_one_name}']**2 - df_stat[f'NumAlive_{team_two_name}']**2) / (df_stat[[f'NumAlive_{team_one_name}', f'NumAlive_{team_two_name}']].max(axis=1)) # Af = (A0^2 - B0^2)/A0
        df_stat[f'{self.stat_name}'].fillna(0)# fill nan=0 in case NumAlive of all teams == 0

        df_stat = df_stat[f'{self.stat_name}']

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=[x for x in self.idx_col if x not in ['Point', 'Team', 'Player', 'Hero']]).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class FBValue(AdvancedStat):
    '''
    FB_value
    '''
    def __init__(self):
        stat_version = '1.0'
        pass 

    def ready_df_init(self):
        pass 

    def define_df_stat(self): 
        pass 

    def merge_df_result(self): 
        pass 

    def get_df_result(self): 
        pass 

class DeathRisk(AdvancedStat):
    '''
    Death_risk
    '''
    def __init__(self):
        stat_version = '1.0'
        pass 

    def ready_df_init(self):
        pass 

    def define_df_stat(self): 
        pass 

    def merge_df_result(self): 
        pass 

    def get_df_result(self): 
        pass

class DIv1(AdvancedStat):
    '''
    Dominance Index version 1
    '''
    def __init__(self):
        stat_version = '1.0'
        pass 

    def ready_df_init(self):
        pass 

    def define_df_stat(self): 
        pass 

    def merge_df_result(self): 
        pass 

    def get_df_result(self): 
        pass



