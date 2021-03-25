import pandas as pd 

class TeamfightDetector():
   
    def __init__(self, input_df=None):
        version = '1.0'
        self.input_df = input_df

        # status checking variables
        self.is_TF_ongoing = False 
        self.FB_happened = False 
        self.FB_silence = False 

        # TF timestamps variables
        self.TF_start_time_stamps = []
        self.TF_end_time_stamps = []

        # threshold variables
        self.HDD_threshold = 500
        self.HDD_lull_cut = 500
        self.FB_threshold = 0
        self.possible_time_variance = 2
        self.no_FB_duration = 10

        # idx_col
        self.idx_col = ['MatchId', 'Map', 'Section', 'RoundName', 'Timestamp', 'Point', 'Team', 'Player', 'Hero']

    def roll_df_input(self):
        df_init = self.df_input.reset_index()
        section_list = df_init['Section'].unique()
        df_init = df_init.groupby(by=self.idx_col).sum()

        TF_rolling = pd.DataFrame()
        for section in section_list:
            df_tmp = df_init.xs(section, level='Section', drop_level=False)
            TF_rolling_tmp = df_tmp.groupby(by=[x for x in self.idx_col if x not in ['Point', 'Team', 'Player', 'Hero']]).sum()
            TF_rolling_tmp = TF_rolling_tmp.rolling(window=10, center=True).sum().fillna(TF_rolling_tmp) # default window=10 sec
            TF_rolling = pd.concat([TF_rolling, TF_rolling_tmp])

        TF_rolling = TF_rolling.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).sum()[['HeroDamageDealt/s', 'FinalBlows/s']]
        TF_rolling.rename(columns={'HeroDamageDealt/s':'HDD', 'FinalBlows/s':'FB'}, inplace=True)

        RCP = df_init.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).max()[['RCP']]

        TF_rolling = pd.merge(TF_rolling, RCP, how='outer', left_index=True, right_index=True)
        pass

    def detect_teamfight(self): 
        pass 

    def get_teamfight_info(self): 
        pass 







class TeamfightConditions(): 
    def __init__(self):
        self.is_TF_ongoing
        self.FB_happened
        self.FB_silence

class TeamfightStartConditions(TeamfightConditions):
    '''
    <시작 조건>
    시작 조건 0. TF 중 = False
    시작 조건 1. time > 이전 TF 종료 시간
    시작 조건 2. HDD >= {HDD_threshold=500} (time - )
    시작 조건 3. FB > 0, time - {possible_time_variance=1}
    시작 조건 4. HDD >= {HDD_threshold=500} 시간 이후, first FB=False 상태로 HDD < {HDD_lull_cut=50} 생기면 이전 HDD time 제외
    '''
    def __init__(self): 
        pass 

    def cond0(): 
        pass 
    def cond1(): 
        pass

    def check_signal(self):
        pass

class TeamfightEndConditions(TeamfightConditions):
    '''
    <종료 조건>
    종료 조건 0. TF 진행 중 = True
    종료 조건 1. FB = 0 이 {no_FB_duration=10}초 이상
    종료 조건 2. time = ts_map_end_time

    *stagger
    *길어지는 한타
    FB 0 되고 10s동안 추가 킬이 없어야 한타 종료로 인정
    '''
    def cond0(self): 
        pass 

    def cond1(self): 
        pass 

    def check_signal(self):
        pass
        

'''
'''
# TF detector
def TF_detector(df_rolling):
    '''
    parameters: dataframe
    <시작 조건>
    시작 조건 0. TF 중 = False
    시작 조건 1. time > 이전 TF 종료 시간
    시작 조건 2. HDD >= {HDD_threshold=500} (time - )
    시작 조건 3. FB > 0, time - {possible_time_variance=1}
    시작 조건 4. HDD >= {HDD_threshold=500} 시간 이후, first FB=False 상태로 HDD < {HDD_lull_cut=50} 생기면 이전 HDD time 제외

    <종료 조건>
    종료 조건 0. TF 진행 중 = True
    종료 조건 1. FB = 0 이 {no_FB_duration=10}초 이상
    종료 조건 2. time = ts_map_end_time

    *stagger
    *길어지는 한타
    FB 0 되고 10s동안 추가 킬이 없어야 한타 종료로 인정

    return:     TF_timestamps: dataframe of [['match_id', 'map_num', 'TF_start_time_stamps', 'TF_end_time_stamps']]
    '''
    global is_TF_ongoing
    is_TF_ongoing = False
    global FB_happened
    FB_happened = False
    global FB_silence
    FB_silence = False

    TF_start_time_stamps = []
    TF_end_time_stamps = []

    HDD_threshold = 500
    HDD_lull_cut = 500
    FB_threshold = 0
    possible_time_variance = 2
    no_FB_duration = 10

    # start condition
    def TF_start(idx):
        global is_TF_ongoing
        global FB_happened
        global FB_silence
        
        def condition0(): # TF 중 = False
            global is_TF_ongoing
            if is_TF_ongoing == True:
                cond0 = False
            else:
                cond0 = True
            return cond0

        def condition1(idx): # time > 이전 TF 종료 시간
            if (idx < df_rolling.index[-1]) == True:
                cond1 = True
            else:
                cond1 = False
            return cond1

        def condition2(idx): # HDD >= {HDD_threshold}
            if df_rolling.loc[idx, 'HDD'] > HDD_threshold:
                cond2 = True
            else:
                cond2 = False
            return cond2 
        
        def condition3(idx): # FB > 0
            global FB_happened
            if df_rolling.loc[idx, 'FB'] > FB_threshold:
                cond3 = True
                FB_happened = True # toggle on
            else:
                cond3 = False
            return cond3
        
        def condition4(idx): # HDD가 오르는 추세에 있어야
            if (df_rolling.loc[idx - no_FB_duration : idx, 'HDD'].mean() <= df_rolling.loc[idx : idx + no_FB_duration, 'HDD'].mean()) == True:
                cond4 = True
            else:
                cond4 = False
            return cond4 
        
        def condition5(idx): # HDD 가 {no_FB_duration} 범위에서 최소값일 경우
            if (df_rolling.loc[idx, 'HDD'] <= df_rolling.loc[idx : idx + no_FB_duration, 'HDD'].min()) == True:
                cond5 = True
            else:
                cond5 = False
            return cond5 


        # check if start_condition == True
        start_condition = condition0() & condition1(idx) & ( (condition2(idx) & condition4(idx) & condition5(idx)) | condition3(idx) ) 
        
        if start_condition == True:
            is_TF_ongoing = True # toggle on
            FB_silence = False # toggle off

        return is_TF_ongoing
    
    # end condition
    def TF_end(idx):
        global is_TF_ongoing
        global FB_happened
        global FB_silence

        def condition0(): # TF 진행 중 = True
            global is_TF_ongoing
            if is_TF_ongoing == True:
                cond0 = True
            else:
                cond0 = False 
            return cond0

        def condition1(idx): # FB = 0 이 {no_FB_duration}초 이상 유지될 때
            global FB_silence
            if df_rolling.loc[idx: idx + no_FB_duration, 'FB'].sum() == 0:
                cond1 = True 
                FB_silence = True # toggle on
            else:
                cond1 = False
            return cond1 
        
        def condition2(idx): # time = ts_map_end_time (Map이 종료됐을 때)
            if idx == df_rolling.index[-1]:
                cond2 = True
            else:
                cond2 = False
            return cond2
        
        def condition3(idx): # FB > 0
            global FB_happened
            if df_rolling.loc[idx, 'FB'] > FB_threshold:
                cond3 = True
                FB_happened = True # toggle on
            else:
                cond3 = False
            return cond3
        
        def condition4(idx): # while FB == 0 & HDD <= {HDD_lull_cut}
            if (df_rolling.loc[idx, 'FB'] == 0) & (df_rolling.loc[idx, 'HDD'] <= HDD_lull_cut):
                cond4 = True
            else:
                cond4 = False
            return cond4
        
        def condition5(idx): # 2s 동안 mean(HDD) < HDD_threshold 
            if df_rolling.loc[idx:idx + 2, 'HDD'].mean() < HDD_threshold:
                cond5 = True
            else:
                cond5 = False
            return cond5

        # init FB_happened
        condition3(idx)

        # check if end_condition == True
        end_condition = ( condition0() & ((condition1(idx) & condition5(idx)) & FB_happened) | (FB_happened & condition4(idx)) ) | condition2(idx)

        if end_condition == True:
            is_TF_ongoing = False # toggle off
            FB_happened = False # toggle off

        return is_TF_ongoing

    TF_status = []

    for idx in df_rolling.index:
        if is_TF_ongoing == False:
            TF_status.append(TF_start(idx))
        else:
            TF_status.append(TF_end(idx))

    df_rolling['TF_status'] = TF_status

    return df_rolling # [['RCP', 'HDD', 'FB', 'TF_status']], index=UTC timestamp


'''
'''
# get TF_time_range
def get_true_range(df=None, column='TF_status'):
    '''
    parameters: data: dataframe with timestamp index
                column: target column to arrange
    
    returns:    index tuple
    '''
    range_list = []
    prev_val = False

    for inx, val in df[column].iteritems():
        if prev_val != val:
            if val:
                start = inx
            else:
                range_list.append((start, inx))

        prev_inx = inx
        prev_val = val
    
    TF_time_range = pd.DataFrame(range_list, columns=['TF_start_time', 'TF_end_time'])
    
    return TF_time_range # df[['TF_start_time', 'TF_end_time']]

''' 
'''
# get TF_info
        def TF_info(df_merge):
            df_merge = df_merge.reset_index()
            section_list = df_merge['Section'].unique()
            df_merge = df_merge.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp', 'Team', 'Player', 'Hero']).sum()

            TF_rolling = pd.DataFrame()
            for section in section_list:
                df_tmp = df_merge.xs(section, level='Section', drop_level=False)
                TF_rolling_tmp = df_tmp.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).sum()
                TF_rolling_tmp = TF_rolling_tmp.rolling(window=10, center=True).sum().fillna(TF_rolling_tmp) # default window=10 sec
                TF_rolling = pd.concat([TF_rolling, TF_rolling_tmp])

            TF_rolling = TF_rolling.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).sum()[['HeroDamageDealt/s', 'FinalBlows/s']]
            TF_rolling.rename(columns={'HeroDamageDealt/s':'HDD', 'FinalBlows/s':'FB'}, inplace=True)

            RCP = df_merge.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).max()[['RCP']]

            TF_rolling = pd.merge(TF_rolling, RCP, how='outer', left_index=True, right_index=True)

            TF_info = pd.DataFrame()
            for section in section_list:
                TF_rolling_tmp = TF_rolling.xs(section, level='Section', drop_level=False)
                TF_rolling_tmp = TF_rolling_tmp.reset_index()
                TF_rolling_tmp = TF_rolling_tmp.set_index('Timestamp')
                df_TF = TF_detector(TF_rolling_tmp) # TF_detector
                TF_time_range = get_true_range(df_TF)

                # define TF winner and RCP
                TF_winner_list = []
                TF_order_list = []
                TF_duration_list = []
                TF_RCP_list = []
                TF_order = 0
                
                for idx in TF_time_range.index:
                    TF_order += 1
                    TF_order_list.append(TF_order)
                    TF_duration_list.append((TF_time_range.loc[idx, 'TF_end_time'] - TF_time_range.loc[idx, 'TF_start_time'])) # TF duration in s
                    TF_RCP_sum = TF_rolling_tmp.loc[TF_time_range.loc[idx, 'TF_start_time']:TF_time_range.loc[idx, 'TF_end_time'], 'RCP'].sum()
                    TF_RCP_list.append(TF_RCP_sum) # RCP
                    if TF_RCP_sum > 0:
                        TF_winner_list.append(team_one_name)
                    elif TF_RCP_sum == 0:
                        TF_winner_list.append('draw')
                    else:
                        TF_winner_list.append(team_two_name)
                TF_time_range['TF_order'] = TF_order_list
                TF_time_range['TF_winner'] = TF_winner_list
                TF_time_range['TF_duration'] = TF_duration_list
                TF_time_range['TF_RCP_sum'] = TF_RCP_list

                TF_time_range['MatchId'] = self.match_id
                TF_time_range['Map'] = self.df_init['Map'].unique()[0]
                TF_time_range['Section'] = section

                TF_info = pd.concat([TF_info, TF_time_range])
            
            return TF_info

        self.TF_info = TF_info(df_merge)

        # add TF_info
        tmp_merge = pd.DataFrame()
        for section in section_list:
            tmp = df_merge.xs(section, level='Section', drop_level=False)
            tmp = tmp.reset_index().set_index('Timestamp')
            TF_info_tmp = self.TF_info[self.TF_info['Section'] == section]
            for idx in TF_info_tmp.index:
                start, end = TF_info_tmp.loc[idx, 'TF_start_time'], TF_info_tmp.loc[idx, 'TF_end_time']
                tmp.loc[start:end, 'TF_order'] = TF_info_tmp.loc[idx, 'TF_order']
                tmp.loc[start:end, 'TF_winner'] = TF_info_tmp.loc[idx, 'TF_winner']
                tmp.loc[start:end, 'TF_duration'] = TF_info_tmp.loc[idx, 'TF_duration']
                tmp.loc[start:end, 'TF_RCP_sum'] = TF_info_tmp.loc[idx, 'TF_RCP_sum']
            
            tmp_merge = pd.concat([tmp_merge, tmp])
        
        df_merge = tmp_merge
