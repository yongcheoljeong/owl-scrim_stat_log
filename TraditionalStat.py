from abc import *

class TraditionalStat(metaclass=ABCMeta):
    def __init__(self, input_df=None):
        self.stat_category: str = 'TraditionalStat'
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


class Cooldown1Percent(TraditionalStat):
    def __init__(self, input_df=None):
        self.stat_level = 'Hero'
        self.stat_name = 'Cooldown 1%'

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Cooldown 1']
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
            max_cooldown = hero_col['Cooldown 1'].max().max()
            if max_cooldown == 0:
                max_cooldown = 1
            hero_col['new_col'] = hero_col['Cooldown 1'] / max_cooldown
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
        self.stat_name = 'Cooldown 2%'

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Cooldown 2']
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
            max_cooldown = hero_col['Cooldown 2'].max().max()
            if max_cooldown == 0:
                max_cooldown = 1
            hero_col['new_col'] = hero_col['Cooldown 2'] / max_cooldown
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