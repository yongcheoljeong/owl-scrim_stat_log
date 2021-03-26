import pandas as pd 
import numpy as np 

class PETH():
    def __init__(self, df_init=None, event_name=None, period=5):
        self.df_init = df_init.reset_index()
        self.period = period 
        self.event_name = event_name

    def find_events(self, of=[]):
        threshold = 1
        event_onsets = self.df_init[self.df_init[self.event_name] >= threshold]

        team_list = event_onsets['Team'].unique()
        player_list = event_onsets['Player'].unique()
        hero_list = event_onsets['Hero'].unique()

        if any(list(set(of) & set(team_list))):
            event_onsets = event_onsets[event_onsets['Team'] == list(set(of) & set(team_list))[0]]
        if any(list(set(of) & set(player_list))):
            event_onsets = event_onsets[event_onsets['Player'] == list(set(of) & set(player_list))[0]]
        if any(list(set(of) & set(hero_list))):
            event_onsets = event_onsets[event_onsets['Hero'] == list(set(of) & set(hero_list))[0]]

        return event_onsets 

    def set_PETH(self, of=[]):
        of = of
        event_onsets = self.find_events(of)
        section_list = event_onsets['Section'].unique()
        
        event_aligned = pd.DataFrame()
        for section in section_list:
            num_event = 0
            events_in_section = event_onsets[event_onsets['Section'] == section]
            df_in_section = self.df_init[self.df_init['Section'] == section].set_index('Timestamp')
            for event_onset in events_in_section['Timestamp']:

                event_recorder = df_in_section.loc[(event_onset)-(self.period+1):(event_onset)+(self.period+1)]
                reindex_timestamp = np.linspace(-self.period, self.period, 2*self.period + 1) # reindex example: [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
                event_recorder = event_recorder.reset_index()

                # replace Timestamp into '-self.period:self.period' scale
                event_recorder['Timestamp'] -= event_onset
                event_recorder['Timestamp'] = event_recorder['Timestamp'].astype(int) # Timestamp 소숫점 자리 버림
                event_recorder['num_event'] = num_event 
                num_event += 1
                event_aligned = pd.concat([event_aligned, event_recorder])
        
        event_aligned = event_aligned.groupby(by=['MatchId', 'Map', 'Section', 'num_event', 'Timestamp', 'Team', 'Player', 'Hero']).sum()
        
        PETH = event_aligned
        return PETH 

    def get_PETH(self, of=[]):
        PETH = self.set_PETH(of=of)

        return PETH
