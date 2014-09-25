#Embedded file name: C:\Users\Dylan\Documents\GitHub\rcfbscraper\Python\Play.py
import re

class Play:

    def __init__(self, data):
        self.data = self.Set_Play_Ints(data)
        self.Rush_Att = 0
        self.Rush_Yard = 0
        self.Rush_TD = 0
        self.Pass_Att = 0
        self.Pass_Comp = 0
        self.Pass_Yard = 0
        self.Pass_TD = 0
        self.Pass_Int = 0
        self.Pass_Conv = 0
        self.Kickoff_Ret = 0
        self.Kickoff_Ret_Yard = 0
        self.Kickoff_Ret_TD = 0
        self.Punt_Ret = 0
        self.Punt_Ret_Yard = 0
        self.Punt_Ret_TD = 0
        self.Fum_Ret = 0
        self.Fum_Ret_Yard = 0
        self.Fum_Ret_TD = 0
        self.Int_Ret = 0
        self.Int_Ret_Yard = 0
        self.Int_Ret_TD = 0
        self.Misc_Ret = 0
        self.Misc_Ret_Yard = 0
        self.Misc_Ret_TD = 0
        self.Field_Goal_Att = 0
        self.Field_Goal_Made = 0
        self.Off_XP_Kick_Att = 0
        self.Off_XP_Kick_Made = 0
        self.Off_2XP_Att = 0
        self.Off_2XP_Made = 0
        self.Def_2XP_Att = 0
        self.Def_2XP_Made = 0
        self.Safety = 0
        self.Points = 0
        self.Punt = 0
        self.Punt_Yard = 0
        self.Kickoff = 0
        self.Kickoff_Yard = 0
        self.Kickoff_Touchback = 0
        self.Kickoff_Out_Of_Bounds = 0
        self.Kickoff_Onsides = 0
        self.Fumble = 0
        self.Fumble_Lost = 0
        self.Tackle_Solo = 0
        self.Tackle_Assist = 0
        self.Tackle_For_Loss = 0
        self.Tackle_For_Loss_Yard = 0
        self.Sack = 0
        self.Sack_Yard = 0
        self.QB_Hurry = 0
        self.Fumble_Forced = 0
        self.Pass_Broken_Up = 0
        self.Kick_Punt_Blocked = 0
        self.First_Down_Rush = 0
        self.First_Down_Pass = 0
        self.First_Down_Penalty = 0
        self.Time_Of_Possession = 0
        self.Penalty = 0
        self.Penalty_Yard = 0
        self.Third_Down_Att = 0
        self.Third_Down_Conv = 0
        self.Fourth_Down_Att = 0
        self.Fourth_Down_Conv = 0
        self.Red_Zone_Att = 0
        self.Red_Zone_TD = 0
        self.Red_Zone_Field_Goal = 0

    def Set_Clock(self, input_clk):
        if None == re.search('\\d{1,2}:\\d{1,2}', input_clk):
            print 'WARNING: Clock not set!\n'
            return input_clk
        else:
            time = re.findall('\\d{1,2}:\\d{1,2}', input_clk)
            time = time[0].split(':')
            return 60 * int(time[0]) + int(time[1])

    def Sack_Occurred(self):
        stuff = 0

    def Fumble_Check(self, next_play):
        stuff = 0

    def Rushing_Touchdown_Occurred(self):
        stuff = 0

    def Completion(self, next_play):
        stuff = 0

    def Interception(self):
        stuff = 0

    def Passing_Touchdown_Occurred(self):
        stuff = 0

    def Same_Offense(self, next_play):
        stuff = 0

    def Two_Pt_Conv_Successful(self, next_play):
        stuff = 0

    def Safety_Occurred(self, next_play):
        stuff = 0

    def First_Down(self, next_play):
        stuff = 0
