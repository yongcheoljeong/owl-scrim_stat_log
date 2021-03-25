from abc import *
import pandas as pd 

class TraditionalStat(metaclass=ABCMeta):
    def __init__(self, input_df=None):
        self.stat_category: str = 'TraditionalStat'
        stat_level: str # Match, Map, Section, Team, Player, Hero
        stat_name: str
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

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

class TimePlayed(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Player'
        self.stat_name = 'TimePlayed'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = []
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        df_stat = df_init
        df_stat[f'{self.stat_name}'] = df_init['Timestamp']

        df_stat = df_stat[self.idx_col+[f'{self.stat_name}']]

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result


class AllDamageDealt(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Player'
        self.stat_name = 'AllDamageDealt'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['HeroDamageDealt', 'BarrierDamageDealt']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        stat_level_list = df_init[self.stat_level].unique() 

        df_stat = pd.DataFrame()
        for stat_level in stat_level_list:
            stat_level_col = df_init[df_init[f'{self.stat_level}'] == stat_level]
            
            stat_level_col['new_col'] = stat_level_col['HeroDamageDealt'] + stat_level_col['BarrierDamageDealt']
            stat_level_col.rename(columns={'new_col':f'{self.stat_name}'}, inplace=True)

            df_stat = pd.concat([df_stat, stat_level_col])

        df_stat = df_stat[self.idx_col+[f'{self.stat_name}']]

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class Cooldown1Percent(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Hero'
        self.stat_name = 'Cooldown1%'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Cooldown1']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        # slice df_init by heroes
        hero_list = df_init['Hero'].unique() 

        df_stat = pd.DataFrame()
        for hero in hero_list:
            hero_col = df_init[df_init['Hero'] == hero]
            max_cooldown = hero_col['Cooldown1'].max().max()
            if max_cooldown == 0:
                max_cooldown = 1
            hero_col['new_col'] = hero_col['Cooldown1'] / max_cooldown
            hero_col.rename(columns={'new_col':f'{self.stat_name}'}, inplace=True)

            df_stat = pd.concat([df_stat, hero_col])

        df_stat = df_stat[self.idx_col+[f'{self.stat_name}']]

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class Cooldown2Percent(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Hero'
        self.stat_name = 'Cooldown2%'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Cooldown2']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        # slice df_init by heroes
        hero_list = df_init['Hero'].unique() 

        df_stat = pd.DataFrame()
        for hero in hero_list:
            hero_col = df_init[df_init['Hero'] == hero]
            max_cooldown = hero_col['Cooldown2'].max().max()
            if max_cooldown == 0:
                max_cooldown = 1
            hero_col['new_col'] = hero_col['Cooldown2'] / max_cooldown
            hero_col.rename(columns={'new_col':f'{self.stat_name}'}, inplace=True)

            df_stat = pd.concat([df_stat, hero_col])

        df_stat = df_stat[self.idx_col+[f'{self.stat_name}']]

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class HealthPercent(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Hero'
        self.stat_name = 'Health%'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Health']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        # slice df_init by heroes
        hero_list = df_init['Hero'].unique() 

        df_stat = pd.DataFrame()
        for hero in hero_list:
            hero_col = df_init[df_init['Hero'] == hero]
            max_health = hero_col.loc[min(hero_col.index),'Health']
            print(hero, max_health)
            hero_col['new_col'] = hero_col['Health'] / max_health
            hero_col.rename(columns={'new_col':f'{self.stat_name}'}, inplace=True)

            df_stat = pd.concat([df_stat, hero_col], ignore_index=True)

        df_stat = df_stat[self.idx_col+[f'{self.stat_name}']]

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result


class NumAlive(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Team'
        self.stat_name = 'NumAlive'
        self.input_df = input_df
        self.idx_col = ['MatchId', 'Map', 'Section', 'Point', 'RoundName', 'Timestamp', 'Team', 'Player', 'Hero']

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['IsAlive']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        # NumAlive of each team
        df_player_alive = df_init.groupby(by=[x for x in self.idx_col if x not in ['Hero']]).mean()
        df_player_alive[df_player_alive['IsAlive'] < 1]['IsAlive'] = 0 # replace to 0 if IsAlive < 1. This is required where a player change hero in one second.
        df_stat = df_player_alive.groupby(by=[x for x in self.idx_col if x not in ['Player', 'Hero']]).sum()

        df_stat.rename(columns={'IsAlive':f'{self.stat_name}'}, inplace=True)

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_result = pd.merge(self.input_df, df_stat, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result