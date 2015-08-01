#Embedded file name: C:\Users\Dylan\Documents\GitHub\rcfbscraper\Python\Play.py
import re
import CONST

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

    def Set_Play_Ints(self, info):
        for i in range(0, len(info)):
            try:
                info[i] = int(info[i])
                continue
            except:
                if 'NA' == info[i] and i != CONST.Y_SPOT:
                    info[i] = 0

            if i == CONST.CLK:
                info[i] = self.Set_Clock(info[i])

        return info

    def Set_Clock(self, input_clk):
        if None == re.search('\\d{1,2}:\\d{1,2}', input_clk):
            print 'WARNING: Clock not set!\n'
            return input_clk
        else:
            time = re.findall('\\d{1,2}:\\d{1,2}', input_clk)
            time = time[0].split(':')
            return 60 * int(time[0]) + int(time[1])

    def Sack_Occurred(self):
        if 'Sack' == self.data[CONST.REST]:
            self.Sack = 1
            self.Sack_Yard = self.data[CONST.Y_DESC]
        elif None != re.search('(sack)', self.data[CONST.P_REST]):
            self.Sack = 1
            self.Sack_Yard = self.data[CONST.Y_DESC]

    def Fumble_Check(self, next_play):
        if 'Fumble' == self.data[CONST.REST]:
            self.Fumble = 1
            self.Fumble_Forced = 1
            if next_play.data[CONST.OFF] == self.data[CONST.DEF] and self.data[CONST.CODE] == next_play.data[CONST.CODE]:
                if self.data[CONST.QTR] == 2 and next_play.data[CONST.QTR] == 3:
                    print 'WARNING: Play ' + str(self.data[CONST.P_NUM]) + ' appears to have a turnover at halftime. Recovering team unknown. Marking as a turnover.\n'
                self.Fumble_Lost = 1
                self.Fumble_Ret = 1
        elif 'Touchdown' == self.data[CONST.REST]:
            if None != re.search('fumble', self.data[CONST.P_REST], re.IGNORECASE):
                self.Fumble = 1
                self.Fumble_Forced = 1
                if next_play.data[CONST.TYPE] == 'Extra.Point' or next_play.data[CONST.TYPE] == 'Two.Point.Attempt':
                    if self.Same_Offense(next_play):
                        self.Fumble_Lost = 0
                    else:
                        self.Fumble_Lost = 1
                        self.Fumble_Ret = 1
                        self.Fumble_Ret_TD = 1
        if None != re.search('fumble', self.data[CONST.P_REST], re.IGNORECASE):
            if self.Fumble == 0:
                print 'WARNING: Play ' + str(self.data[CONST.P_NUM]) + " looks like a fumble, but one isn't marked down!"
                print self.data[CONST.P_REST]

    def Rushing_Touchdown_Occurred(self):
        if self.data[CONST.REST] == 'Touchdown' and self.Fumble_Lost == 0:
            self.Rush_TD = 1

    def Completion(self, next_play):
        if 'Completion' == self.data[CONST.REST]:
            self.Pass_Comp = 1
        elif 'Touchdown' == self.data[CONST.REST]:
            if self.Fumble_Lost == 1 or self.Pass_Int == 1:
                if None != re.search('(intercept)', self.data[CONST.P_REST]):
                    self.Pass_Comp = 0
                elif None != re.search('(fumble)', self.data[CONST.P_REST]):
                    if None != re.search('(sack)', self.data[CONST.P_REST]):
                        self.Pass_Comp = 0
                    elif None != re.search('(pass)', self.data[CONST.P_REST]):
                        self.Pass_Comp = 1
            else:
                self.Pass_Comp = 1
        elif 'Fumble' == self.data[CONST.REST]:
            if None != re.search('(sack)', self.data[CONST.P_REST]):
                self.Pass_Comp = 0
            elif None != re.search('(pass)', self.data[CONST.P_REST]):
                self.Pass_Comp = 1
        else:
            self.Pass_Comp = 0

    def Interception(self):
        if self.data[CONST.REST] == 'Interception':
            self.Pass_Int = 1
            self.Int_Ret = 1
        elif self.data[CONST.REST] == 'Touchdown':
            if None != re.search('intercept', self.data[CONST.P_REST], re.IGNORECASE):
                self.Pass_Int = 1
                self.Int_Ret = 1
                self.Int_Ret_TD = 1

    def Passing_Touchdown_Occurred(self):
        if self.data[CONST.REST] == 'Touchdown' and self.Fumble_Lost == 0 and self.Pass_Int == 0:
            self.Pass_TD = 1

    def Same_Offense(self, next_play):
        if next_play.data[CONST.OFF] == self.data[CONST.OFF]:
            return True
        if next_play.data[CONST.OFF] == self.data[CONST.DEF]:
            return False

    def Two_Pt_Conv_Successful(self, next_play):
        if self.data[CONST.O_PT] + 2 == next_play.data[CONST.O_PT]:
            self.Off_2XP_Made = 1
            self.Def_2XP_Made = 1

    def Safety_Occurred(self, next_play):
        if self.data[CONST.QTR] == 2 and next_play.data[CONST.QTR] == 3:
            if self.data[CONST.DEF] == next_play.data[CONST.DEF]:
                if self.data[CONST.D_PT] + 2 == next_play.data[CONST.D_PT]:
                    self.Safety = 1
            elif self.data[CONST.D_PT] + 2 == next_play.data[CONST.O_PT]:
                self.Safety = 1
        if self.data[CONST.CODE] != next_play.data[CONST.CODE]:
            try:
                if self.data[CONST.SPOT] - self.data[CONST.Y_DESC] >= 100:
                    self.Safety = 1
            except:
                self.Safety = 0

        if 'Kickoff' == next_play.data[CONST.TYPE]:
            if self.data[CONST.D_PT] + 2 == next_play.data[CONST.D_PT]:
                self.Safety = 1

    def First_Down(self, next_play):
        if self.Same_Offense(next_play) == 1 and next_play.data[CONST.DOWN] == 1:
            if self.Rush_Att == 1 and self.Rush_Yard >= self.data[CONST.DIST]:
                self.First_Down_Rush = 1
            elif self.Pass_Att == 1 and self.Pass_Yard >= self.data[CONST.DIST]:
                self.First_Down_Pass = 1
            elif self.Penalty == 1:
                self.First_Down_Penalty = 1
            else:
                print 'WARNING: Play ' + str(self.data[CONST.P_NUM]) + " had a first down, but didn't get enough yards for one! Returning 0."
                print self.data[CONST.P_REST]
                print 'Yards gained: ' + str(self.data[CONST.Y_DESC])
                print 'Yards needed: ' + str(self.data[CONST.DIST]) + '\n'
                self.first_down = 0
        elif self.Same_Offense(next_play) and self.data[CONST.DIST] < self.data[CONST.Y_DESC]:
            if next_play.data[CONST.QTR] == 3 and self.data[CONST.QTR] == 2 or next_play.data[CONST.CODE] != self.data[CONST.CODE]:
                if self.Rush_Att == 1:
                    self.First_Down_Rush = 1
                elif self.Pass_Att == 1 and Pass_Yard >= self.data[CONST.DIST]:
                    self.First_Down_Pass = 1
            elif 'Penalty' == next_play.data[CONST.TYPE]:
                self.First_Down_Penalty = 0
            elif None != re.search('penal', self.data[CONST.P_REST], re.IGNORECASE):
                self.First_Down_Penalty = 0
            elif 0 == self.data[CONST.DIST]:
                self.First_Down_Pass = 0
            elif self.Fumble_Lost == 1 and Rush_Yard >= self.data[CONST.DIST]:
                self.First_Down_Rush = 1
            elif self.Fumble_Lost == 1 and Pass_Yard >= self.data[CONST.DIST]:
                self.First_Down_Pass = 1
            else:
                print 'WARNING: Play ' + str(self.data[CONST.P_NUM]) + " didn't have a first down, but got enough yards for one! Returning 0."
                print self.data[CONST.P_REST]
                print 'Yards gained: ' + str(self.data[CONST.Y_DESC])
                print 'Yards needed: ' + str(self.data[CONST.DIST]) + '\n'
