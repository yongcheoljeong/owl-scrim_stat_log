from abc import *
import pandas as pd 
import numpy as np

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

        def RCP(X, Y):
            Max = X.combine(Y, max)
            RCP = (X**2 - Y**2).div(Max)
            RCP = RCP.fillna(-Y) # fill nan = -Y in case X == 0
            return RCP

        # team_names
        team_name_list = df_init['Team'].unique()
        team_one_name = 'NYE'
        team_two_name = [x for x in team_name_list if x != team_one_name][0]

        # team_one_NumAlive (NYE)
        team_one_NumAlive = df_init[df_init['Team'] == 'NYE']
        team_one_NumAlive = team_one_NumAlive.groupby(by=self.idx_col).max()

        # team_two_NumAlive (Opponent)
        team_two_NumAlive = df_init[df_init['Team'] != 'NYE']
        team_two_NumAlive = team_two_NumAlive.groupby(by=self.idx_col).max()

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
    def __init__(self, input_df=None):
        self.stat_level = 'Team'
        self.stat_name = 'FBValue'
        self.stat_version = '1.0'
        self.idx_col = ['MatchId', 'Map', 'Section', 'Timestamp', 'Team', 'Player', 'Hero']
        self.input_df = input_df

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['NumAlive', 'FinalBlows/s']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init

    def define_df_stat(self): 
        def RCP(X, Y):
            Max = X.combine(Y, max)
            RCP = (X**2 - Y**2).div(Max)
            RCP = RCP.fillna(-Y) # fill nan = -Y in case X == 0
            return RCP

        def FB_value(X, Y, FB):
            FB_value = abs(RCP(X, Y + FB) - RCP(X, Y))
            return FB_value 
                
        df_init = self.ready_df_init()

        # team_names
        team_name_list = df_init['Team'].unique()
        team_one_name = 'NYE'
        team_two_name = [x for x in team_name_list if x != team_one_name][0]
        
        team_one_numalive = df_init.groupby(by=[x for x in self.idx_col if x not in ['Player', 'Hero']])['NumAlive'].max().xs(team_one_name, level='Team', drop_level=False)
        team_two_numalive = df_init.groupby(by=[x for x in self.idx_col if x not in ['Player', 'Hero']])['NumAlive'].max().xs(team_two_name, level='Team', drop_level=False)
        df_group = pd.merge(team_one_numalive, team_two_numalive, how='outer', left_index=True, right_index=True, suffixes=(f'_{team_one_name}', f'_{team_two_name}')).fillna(0)
        df_group = df_group.groupby(by=[x for x in self.idx_col if x not in ['Team', 'Player', 'Hero']]).sum()

        team_one_FB = df_init.groupby(by=self.idx_col)['FinalBlows/s'].max().xs(team_one_name, level='Team', drop_level=False)
        team_two_FB = df_init.groupby(by=self.idx_col)['FinalBlows/s'].max().xs(team_two_name, level='Team', drop_level=False)

        team_one = pd.merge(team_one_FB, df_group, how='outer', left_index=True, right_index=True)
        team_two = pd.merge(team_two_FB, df_group, how='outer', left_index=True, right_index=True)

        # FB value
        team_one_FB_value = FB_value(team_one[f'NumAlive_{team_one_name}'],  team_one[f'NumAlive_{team_two_name}'], team_one['FinalBlows/s'])
        team_two_FB_value = FB_value(team_two[f'NumAlive_{team_two_name}'],  team_two[f'NumAlive_{team_one_name}'], team_two['FinalBlows/s'])

        FB_value = pd.concat([team_one_FB_value, team_two_FB_value]).groupby(by=self.idx_col).max()
        FB_value.rename(f'{self.stat_name}', inplace=True)

        df_stat = FB_value

        return df_stat

    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_result = pd.merge(self.input_df, df_stat, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class DeathRisk(AdvancedStat):
    '''
    Death_risk
    '''
    def __init__(self, input_df=None):
        self.stat_level = 'Team'
        self.stat_name = 'DeathRisk'
        self.stat_version = '1.0'
        self.idx_col = ['MatchId', 'Map', 'Section', 'Timestamp', 'Team', 'Player', 'Hero']
        self.input_df = input_df

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['NumAlive', 'Deaths/s']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init

    def define_df_stat(self): 
        def RCP(X, Y):
            Max = X.combine(Y, max)
            RCP = (X**2 - Y**2).div(Max)
            RCP = RCP.fillna(-Y) # fill nan = -Y in case X == 0
            return RCP
       
        def Death_risk(X, Y, Death):
            Death_risk = abs(RCP(X + Death, Y) - RCP(X, Y))
            return Death_risk
        
        df_init = self.ready_df_init()

        # team_names
        team_name_list = df_init['Team'].unique()
        team_one_name = 'NYE'
        team_two_name = [x for x in team_name_list if x != team_one_name][0]
        
        team_one_numalive = df_init.groupby(by=[x for x in self.idx_col if x not in ['Player', 'Hero']])['NumAlive'].max().xs(team_one_name, level='Team', drop_level=False)
        team_two_numalive = df_init.groupby(by=[x for x in self.idx_col if x not in ['Player', 'Hero']])['NumAlive'].max().xs(team_two_name, level='Team', drop_level=False)
        df_group = pd.merge(team_one_numalive, team_two_numalive, how='outer', left_index=True, right_index=True, suffixes=(f'_{team_one_name}', f'_{team_two_name}')).fillna(0)
        df_group = df_group.groupby(by=[x for x in self.idx_col if x not in ['Team', 'Player', 'Hero']]).sum()

        team_one_Death = df_init.groupby(by=self.idx_col)['Deaths/s'].max().xs(team_one_name, level='Team', drop_level=False)
        team_two_Death = df_init.groupby(by=self.idx_col)['Deaths/s'].max().xs(team_two_name, level='Team', drop_level=False)

        team_one = pd.merge(team_one_Death, df_group, how='outer', left_index=True, right_index=True)
        team_two = pd.merge(team_two_Death, df_group, how='outer', left_index=True, right_index=True)

        # Death_risk
        team_one_Death_risk = Death_risk(team_one[f'NumAlive_{team_one_name}'],  team_one[f'NumAlive_{team_two_name}'], team_one['Deaths/s'])
        team_two_Death_risk = Death_risk(team_two[f'NumAlive_{team_two_name}'],  team_two[f'NumAlive_{team_one_name}'], team_two['Deaths/s'])

        Death_risk = pd.concat([team_one_Death_risk, team_two_Death_risk]).groupby(by=self.idx_col).max()
        Death_risk.rename(f'{self.stat_name}', inplace=True)

        df_stat = Death_risk

        return df_stat

    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_result = pd.merge(self.input_df, df_stat, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result

class DIv2(AdvancedStat):
    '''
    Dominance Index version 2
    DI (Inverse Coefficient of Variation) = (mean(X) / variance(X))
    X = (TF_RCP_sum/TF_duration)
    '''
    def __init__(self, input_df=None):
        self.stat_level = 'Map'
        self.stat_name = 'DominanceIndex'
        self.stat_version = '2.0'
        self.idx_col = ['MatchId', 'Map', 'Section', 'TF_order']
        self.input_df = input_df

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['TF_RCP_sum', 'TF_duration']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()

        df_stat = df_init.groupby(by=self.idx_col).max()
        df_stat['TF_RCP_sum/s'] = df_stat['TF_RCP_sum'].div(df_stat['TF_duration'])

        def DominanceIndex(X):
            DI = X.mean() / X.std()
            return DI
        
        df_stat['DominanceIndex'] = DominanceIndex(df_stat['TF_RCP_sum/s'])
        
        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        df_stat = df_stat.reset_index().set_index(['MatchId', 'Map'])
        df_stat = df_stat['DominanceIndex']
        df_result = pd.merge(self.input_df, df_stat, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result


class ResourceCost(AdvancedStat):
    '''
    Assume that the (Ability Value) = (Ability Cooldown)
    '''
    def __init__(self, input_df=None):
        self.stat_level = 'Team'
        self.stat_name = 'ResourceCost'
        self.stat_version = '1.0'
        self.idx_col = ['MatchId', 'Map', 'Section', 'Team']
        self.input_df = input_df

    def ready_df_init(self):
        input_df = self.input_df.reset_index()
        
        requirement_col = ['Cooldown1', 'Cooldown2', 'CooldownSecondaryFire', 'CooldownCrouching', 'UltimateUsed/s', 'MaxHealth']
        ready_col = self.idx_col + requirement_col
        df_init = input_df[ready_col]

        return df_init
    
    def define_df_stat(self):
        df_init = self.ready_df_init()
        '''
        D.Va MaxHealth == 150 일 때 UltimateUsed/s 카운트 하지 않음. 
        '''
        # df_stat here
        df_stat = df_init.groupby(by=self.idx_col).max()

        def AbilityCost(sum_Cooldown):
            # ability cost here
            Cooldown = (-1 + (1 + 8*sum_Cooldown)^(1/2) / 2)
            return Cooldown
        
        def UltimateCost(df):
            # ultimate cost here
            UC_dict = Resources.UltimateCost
            UU = df['UltimateUsed/s'].sum()
            hero_name = df['Hero'].unique()
            ultimate_cost = UC_dict(key=hero_name) / 5 * UU

            return ultimate_cost
        
        return df_stat
    
    def merge_df_result(self):
        df_stat = self.define_df_stat()
        
        df_result = pd.merge(self.input_df, df_stat, how='outer', left_index=True, right_index=True)

        return df_result
    
    def get_df_result(self):
        df_result = self.merge_df_result()
        return df_result


