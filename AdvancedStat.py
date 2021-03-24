from abc import *

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
        stat_version = '1.0'

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col : list
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_stat_g = df_stat.groupby(by=self.idx_col).sum()
        df_result = pd.merge(self.input_df, df_stat_g, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class RCPv2(AdvancedStat):
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



