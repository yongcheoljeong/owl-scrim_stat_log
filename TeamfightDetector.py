import pandas as pd 

class TeamfightDetector():
   
    def __init__(self, input_df=None):
        version = '1.1'
        self.input_df = input_df

        # MatchId
        self.MatchId = self.input_df.index.unique('MatchId')[0]
        # Map 
        self.Map = self.input_df.index.unique('Map')[0]
        # section list 
        self.section_list = self.input_df.index.unique('Section')
        # team names
        team_name_list = self.input_df.index.unique('Team')
        self.team_one_name = 'NYE'
        self.team_two_name = [x for x in team_name_list if x != self.team_one_name][0]

        # idx_col
        self.idx_col = ['MatchId', 'Map', 'Section', 'Timestamp', 'Team', 'RoundName', 'Point', 'Player', 'Hero']

    def ready_df_init(self):
        df_init = self.input_df.reset_index()

        requirement_col = ['HeroDamageDealt/s', 'FinalBlows/s', 'RCP']
        ready_col = self.idx_col + requirement_col
        df_init = df_init[ready_col]

        # split 'hero_level_stats', 'team_level_stats', 'map_level_stats'
        hero_level_stats = df_init.groupby(by=[x for x in self.idx_col if x not in ['Team', 'RoundName', 'Point', 'Player', 'Hero']]).sum()[['HeroDamageDealt/s', 'FinalBlows/s']]
        map_level_stats = df_init.groupby(by=[x for x in self.idx_col if x not in ['Team', 'RoundName', 'Point', 'Player', 'Hero']]).max()[['RCP']]
        df_init = pd.merge(hero_level_stats, map_level_stats, how='outer', left_index=True, right_index=True)

        return df_init 
    
    def roll_df_init(self):
        df_init = self.ready_df_init()

        section_list = df_init.index.unique('Section')

        TF_rolling = pd.DataFrame()
        for section in section_list:
            df_tmp = df_init.xs(section, level='Section', drop_level=False)
            TF_rolling_tmp = df_tmp.rolling(window=10, min_periods=1).sum() #.fillna(df_tmp) # default window=10 sec v1.1
            TF_rolling = pd.concat([TF_rolling, TF_rolling_tmp])

        TF_rolling = TF_rolling.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).sum()[['HeroDamageDealt/s', 'FinalBlows/s']] # For RCP not rolling
        TF_rolling.rename(columns={'HeroDamageDealt/s':'HDD', 'FinalBlows/s':'FB'}, inplace=True)

        RCP = df_init.groupby(by=['MatchId', 'Map', 'Section', 'Timestamp']).max()[['RCP']] # For RCP not rolling
        TF_rolling = pd.merge(TF_rolling, RCP, how='outer', left_index=True, right_index=True) # For RCP not rolling

        return TF_rolling

    def set_TF_info(self): 
        TF_rolling = self.roll_df_init()


        def TFWinnerDetector():
            '''
            TF_RCP_sum 만으로 winner 판단하면 안 되는 예시:
            (20210325_01, Dorado, 1, TF#3) 처럼 마지막에 급격하게 RCP 변화가 있을 경우 TF 전반적으로 HZS가 유리했더라도 마지막에 NYE가 한타 뒤집어버리는 경우
            (20210325_01, Temple of Anubis, 2, TF#1) 위와 같은 경우
            그럼 마지막 RCP 높은 쪽으로 승리 팀을 판단하면 되나? 이것도 안됨.
            마지막 RCP 높은 쪽으로 winner 판단하면 안 되는 예시:
            (20210325_02, Dorado, 0, TF#4) 처럼 일방적으로 TAL 쪽에서 FB 기록했지만 리스폰이 돌면서 한타 마지막에만 순간적으로 RCP가 NYE 쪽으로 기운 경우


            '''
        TF_info = pd.DataFrame()
        for section in self.section_list:
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
                    TF_winner_list.append(self.team_one_name)
                elif TF_RCP_sum == 0:
                    TF_winner_list.append('draw')
                else:
                    TF_winner_list.append(self.team_two_name)
            TF_time_range['TF_order'] = TF_order_list
            TF_time_range['TF_winner'] = TF_winner_list
            TF_time_range['TF_duration'] = TF_duration_list
            TF_time_range['TF_RCP_sum'] = TF_RCP_list

            TF_time_range['MatchId'] = self.MatchId
            TF_time_range['Map'] = self.Map
            TF_time_range['Section'] = section

            TF_info = pd.concat([TF_info, TF_time_range])
        
        return TF_info

    def get_df_result(self): 
        TF_info = self.set_TF_info()

        tmp_merge = pd.DataFrame()
        for section in self.section_list:
            tmp = self.input_df.xs(section, level='Section', drop_level=False)
            tmp = tmp.reset_index().set_index('Timestamp')
            TF_info_tmp = TF_info[TF_info['Section'] == section]
            for idx in TF_info_tmp.index:
                start, end = TF_info_tmp.loc[idx, 'TF_start_time'], TF_info_tmp.loc[idx, 'TF_end_time']
                tmp.loc[start:end, 'TF_order'] = TF_info_tmp.loc[idx, 'TF_order']
                tmp.loc[start:end, 'TF_winner'] = TF_info_tmp.loc[idx, 'TF_winner']
                tmp.loc[start:end, 'TF_duration'] = TF_info_tmp.loc[idx, 'TF_duration']
                tmp.loc[start:end, 'TF_RCP_sum'] = TF_info_tmp.loc[idx, 'TF_RCP_sum']
            
            tmp_merge = pd.concat([tmp_merge, tmp])
        
        df_result = tmp_merge 

        return df_result
        
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
    시작 조건 5. HDD 가 {no_FB_duration} 범위에서 최소값일 경우

    <종료 조건>
    종료 조건 0. TF 진행 중 = True
    종료 조건 1. FB = 0 이 {no_FB_duration=10}초 이상
    종료 조건 2. time = ts_map_end_time
    종료 조건 3. FB가 있었어야
    종료 조건 4. while FB == 0 & HDD <= {HDD_lull_cut}
    종료 조건 5. 2s 동안 mean(HDD) < HDD_threshold 

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
    HDD_lull_cut = 600
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
            if df_rolling.loc[idx : idx + no_FB_duration, 'FB'].sum() == 0:
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
        
        def condition4(idx): # while FB == 0 for 0~+8 & HDD <= {HDD_lull_cut}
            if (df_rolling.loc[idx : idx + (no_FB_duration - possible_time_variance), 'FB'].sum() == 0) & (df_rolling.loc[idx, 'HDD'] <= HDD_lull_cut):
                cond4 = True
            else:
                cond4 = False
            return cond4
        
        def condition5(idx): # 2s 동안 mean(HDD) < HDD_threshold 
            if df_rolling.loc[idx : idx + possible_time_variance, 'HDD'].mean() < HDD_threshold:
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
