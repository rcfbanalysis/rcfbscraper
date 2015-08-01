import re
import C

# Holds the data for a team-game stats
class Team_Game_Stat:

    # Constructor
    def __init__(self, game_code, team_code, play):
        self.Game_Code = int(game_code)
        self.Team_Code = int(team_code)
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
        self.Fum_Lost = 0
        self.Tackle_Solo = 0
        self.Tackle_Assist = 0
        self.Tackle_For_Loss = 0
        self.Tackle_For_Loss_Yard = 0
        self.Sack = 0
        self.Sack_Yard = 0
        self.QB_Hurry = 0
        self.Fum_Forced = 0
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

        # not included in file
        self.Yard_Line = 0
        self.Next_Yard_Line = 0
        if self.Team_Code != 0:
            self.Is_Home = self.Check_If_Home(play)


    # Gleans relevent data from a play
    def Extract_Play_Data(self, play, next_play):

        # Don't count bad plays
        if play[C.DIR] == "ERROR":
            return 1

        # Get play basics
        turnover = self.Check_Turnover(play)
        no_play = self.Check_No_Play(play)
        self.Yard_Line = self.Convert_Yard_Line(play)
        self.Next_Yard_Line = self.Convert_Yard_Line(next_play)
        ptype = play[C.TYPE]

        # Get rushing stats
        if ptype == "RUSH" and no_play == 0:
            #print play[C.DESC]
            self.Rush_Att += 1
            self.Rush_Yard += self.Add_Yards(ptype, play)
            if turnover == 0:
                self.Rush_TD += self.Check_TD(play)
            self.First_Down_Rush += self.Check_First_Down(play, next_play, ptype)

        # Get passing stats
        if ptype == "PASS" and no_play == 0:
            #print play[C.DESC]
            self.Pass_Att += 1
            self.Pass_Comp += self.Check_Completion(play)
            self.Pass_Yard += self.Add_Yards(ptype, play)
            if turnover == 0:
                self.Pass_TD += self.Check_TD(play)
            self.Pass_Int += self.Check_Interception(play)
            self.First_Down_Pass += self.Check_First_Down(play, next_play, ptype)

        # Get sack stats
        if ptype == "SACKED" and no_play == 0:
            #print play[C.DESC]
            self.Rush_Att += 1
            self.Rush_Yard += self.Add_Yards(ptype, play)

        # Check for score
        score_loc = C.HSCR if self.Is_Home else C.VSCR
        try:
            score = int(play[score_loc])
            self.Points = score if score > 0 else self.Points
        except:
            pass

        return 0


    # Converts 0-50-0 yard scale to 0-100
    def Convert_Yard_Line(self, play):
        try:
            direction = int(play[C.DIR])
            yard_line = int(play[C.YARD])
        except:
            return -1000
        if self.Team_Code == direction:
            return 100 - yard_line
        else:
            return yard_line


    # Checks if this team is home or away
    def Check_If_Home(self, play):
        try:
            if int(play[C.HOME]) == self.Team_Code:
                return True
            else:
                return False
        except:
            print "WARNING: I can't tell if this team is home or away"
            print "         Game Code: " + str(self.Game_Code)
            print "         Team Code: " + str(self.Team_Code)
            raw_input()
            return False


    # Checks if a turnover occurred
    def Check_Turnover(self, play):
        m = re.search(r"(?P<fum>FUMBLE)|(?P<int>INTERCEPT)", play[C.DESC])
        if None == m:           # no match
            return 0
        if m.group("fum"):      # fumble
            return 1
        elif m.group("int"):    # interception
            return 1
        else:
            return 0


    # Checks if a play is removed due to penalty
    def Check_No_Play(self, play):
        if len(play[C.NOPLY]) == 0:     # no field
            return 0
        elif int(play[C.NOPLY]) == 0:   # 0
            return 0
        elif int(play[C.NOPLY]) == 1:   # 1
            return 1


    # Checks if a pass play was complete occurred
    def Check_Completion(self, play):
        try:
            return int(play[C.COMP])
        except:
            return 0


    # Checks if a (rush/pass) play is a touchdown (assuming "no play" == 0)
    def Check_TD(self, play):
        try:
            if int(play[C.ISTD]) == 1:
                return 1
            else:
                return 0
        except:
            return 0


    # Checks if a pass play was an interception (assuming "no play" == 0)
    def Check_Interception(self, play):
        m = re.search(r"INTERCEPTED", play[C.DESC])
        if m:
            return 1
        else:
            return 0


    # Checks if a (rush/pass) play resulted in a first down (assuming "no play" == 0))
    def Check_First_Down(self, play, next_play, ptype):
        try:
            next_offense = int(next_play[C.OFF])
        except:
            return 0
        if next_play[C.DOWN] == "1" and next_offense == self.Team_Code:
            try:
                dist_needed = int(play[C.DIST])
            except:
                return 1
            too_few_yards = True if self.Add_Yards(ptype, play) < dist_needed else False 
            m = re.search(r"FUMBLE", play[C.DESC])
            if (m or (play[C.PEN] == "1" and play[C.PEND] != "1")) and too_few_yards:
                return 0
            elif too_few_yards:
                print "WARNING: This team may not have actually gotten a first down"
                print "         " + str(play[C.DOWN])
                print "         " + str(play[C.DIST])
                print "         " + str(self.Add_Yards(ptype, play))
                print "         " + str(play[C.DESC])
                #raw_input()
                return 0
            return 1
        else:
            return 0


    # Adds yards to (rush/sacked/pass) play
    def Add_Yards(self, ptype, play):
        if (ptype == "PASS" and play[C.COMP] == "1") or ptype == "RUSH" or ptype == "SACKED":
            try:
                yards = int(play[C.GAIN])
                return yards
            except:
                # try to manually parse yardage
                m1 = re.search(r"for (?P<yards>-?\d{1,3}) (?:yards|yard)", play[C.DESC])
                m2 = re.search(r"runs (?P<yards>\d{1,3}) (?:yards|yard) for a touchdown", play[C.DESC])
                m3 = re.search(r"for no gain", play[C.DESC])
                m4 = re.search(r"(?P<fum>FUMBLE)|(?P<oob>out of bounds)", play[C.DESC])
                if m1:
                    #print "WARNING: Manually parsed yardage, returning " + str(m1.group("yards"))
                    #print "         " + play[C.DESC]
                    #raw_input()
                    return int(m1.group("yards"))
                elif m2:
                    #print "WARNING: Manually parsed yardage, returning " + str(m2.group("yards"))
                    #print "         " + play[C.DESC]
                    #raw_input()
                    return int(m2.group("yards"))
                elif m3:
                    #print "WARNING: Manually parsed yardage, returning 0"
                    #print "         " + play[C.DESC]
                    #raw_input()
                    return 0
                elif m4:
                    if self.Next_Yard_Line > -1000 and self.Yard_Line > -1000:
                        gained = self.Yard_Line - self.Next_Yard_Line
                    else:
                        gained = 0
                    #print "WARNING: Manually parsed yardage, returning " + str(gained)
                    #print "         " + play[C.DESC]
                    #raw_input()
                    return gained
                else:
                    print "WARNING: No yards added to play"
                    print "         " + play[C.DESC]
                    raw_input()
                    return 0
        else:
            return 0


    # Returns an array of relavent information
    def Compile_Stats(self):
        OutputArray = []
        OutputArray.append(str(self.Team_Code))
        OutputArray.append(str(self.Game_Code))
        OutputArray.append(str(self.Rush_Att))
        OutputArray.append(str(self.Rush_Yard))
        OutputArray.append(str(self.Rush_TD))
        OutputArray.append(str(self.Pass_Att))
        OutputArray.append(str(self.Pass_Comp))
        OutputArray.append(str(self.Pass_Yard))
        OutputArray.append(str(self.Pass_TD))
        OutputArray.append(str(self.Pass_Int))
        OutputArray.append(str(self.Pass_Conv))
        OutputArray.append(str(self.Kickoff_Ret))
        OutputArray.append(str(self.Kickoff_Ret_Yard))
        OutputArray.append(str(self.Kickoff_Ret_TD))
        OutputArray.append(str(self.Punt_Ret))
        OutputArray.append(str(self.Punt_Ret_Yard))
        OutputArray.append(str(self.Punt_Ret_TD))
        OutputArray.append(str(self.Fum_Ret))
        OutputArray.append(str(self.Fum_Ret_Yard))
        OutputArray.append(str(self.Fum_Ret_TD))
        OutputArray.append(str(self.Int_Ret))
        OutputArray.append(str(self.Int_Ret_Yard))
        OutputArray.append(str(self.Int_Ret_TD))
        OutputArray.append(str(self.Misc_Ret))
        OutputArray.append(str(self.Misc_Ret_Yard))
        OutputArray.append(str(self.Misc_Ret_TD))
        OutputArray.append(str(self.Field_Goal_Att))
        OutputArray.append(str(self.Field_Goal_Made))
        OutputArray.append(str(self.Off_XP_Kick_Att))
        OutputArray.append(str(self.Off_XP_Kick_Made))
        OutputArray.append(str(self.Off_2XP_Att))
        OutputArray.append(str(self.Off_2XP_Made))
        OutputArray.append(str(self.Def_2XP_Att))
        OutputArray.append(str(self.Def_2XP_Made))
        OutputArray.append(str(self.Safety))
        OutputArray.append(str(self.Points))
        OutputArray.append(str(self.Punt))
        OutputArray.append(str(self.Punt_Yard))
        OutputArray.append(str(self.Kickoff))
        OutputArray.append(str(self.Kickoff_Yard))
        OutputArray.append(str(self.Kickoff_Touchback))
        OutputArray.append(str(self.Kickoff_Out_Of_Bounds))
        OutputArray.append(str(self.Kickoff_Onsides))
        OutputArray.append(str(self.Fumble))
        OutputArray.append(str(self.Fum_Lost))
        OutputArray.append(str(self.Tackle_Solo))
        OutputArray.append(str(self.Tackle_Assist))
        OutputArray.append(str(self.Tackle_For_Loss))
        OutputArray.append(str(self.Tackle_For_Loss_Yard))
        OutputArray.append(str(self.Sack))
        OutputArray.append(str(self.Sack_Yard))
        OutputArray.append(str(self.QB_Hurry))
        OutputArray.append(str(self.Fum_Forced))
        OutputArray.append(str(self.Pass_Broken_Up))
        OutputArray.append(str(self.Kick_Punt_Blocked))
        OutputArray.append(str(self.First_Down_Rush))
        OutputArray.append(str(self.First_Down_Pass))
        OutputArray.append(str(self.First_Down_Penalty))
        OutputArray.append(str(self.Time_Of_Possession))
        OutputArray.append(str(self.Penalty))
        OutputArray.append(str(self.Penalty_Yard))
        OutputArray.append(str(self.Third_Down_Att))
        OutputArray.append(str(self.Third_Down_Conv))
        OutputArray.append(str(self.Fourth_Down_Att))
        OutputArray.append(str(self.Fourth_Down_Conv))
        OutputArray.append(str(self.Red_Zone_Att))
        OutputArray.append(str(self.Red_Zone_Field_Goal))
        OutputArray.append(str(self.Red_Zone_TD))
        return OutputArray


    # Returns the header for a play type
    def Team_Game_Stats_Header(self):
        OutputArray = []
        OutputArray.append("Team Code")
        OutputArray.append("Game Code")
        OutputArray.append("Rush Att")
        OutputArray.append("Rush Yard")
        OutputArray.append("Rush TD")
        OutputArray.append("Pass Att")
        OutputArray.append("Pass Comp")
        OutputArray.append("Pass Yard")
        OutputArray.append("Pass TD")
        OutputArray.append("Pass Int")
        OutputArray.append("Pass Conv") 
        OutputArray.append("Kickoff Ret") 
        OutputArray.append("Kickoff Ret Yard") 
        OutputArray.append("Kickoff Ret TD") 
        OutputArray.append("Punt Ret") 
        OutputArray.append("Punt Ret Yard") 
        OutputArray.append("Punt Ret TD") 
        OutputArray.append("Fum Ret") 
        OutputArray.append("Fum Ret Yard") 
        OutputArray.append("Fum Ret TD") 
        OutputArray.append("Int Ret") 
        OutputArray.append("Int Ret Yard") 
        OutputArray.append("Int Ret TD") 
        OutputArray.append("Misc Ret") 
        OutputArray.append("Misc Ret Yard") 
        OutputArray.append("Misc Ret TD") 
        OutputArray.append("Field Goal Att") 
        OutputArray.append("Field Goal Made") 
        OutputArray.append("Off XP Kick Att") 
        OutputArray.append("Off XP Kick Made") 
        OutputArray.append("Off 2XP Att") 
        OutputArray.append("Off 2XP Made") 
        OutputArray.append("Def 2XP Att") 
        OutputArray.append("Def 2XP Made") 
        OutputArray.append("Safety")
        OutputArray.append("Points") 
        OutputArray.append("Punt") 
        OutputArray.append("Punt Yard") 
        OutputArray.append("Kickoff") 
        OutputArray.append("Kickoff Yard") 
        OutputArray.append("Kickoff Touchback") 
        OutputArray.append("Kickoff Out-Of-Bounds") 
        OutputArray.append("Kickoff Onside") 
        OutputArray.append("Fumble") 
        OutputArray.append("Fumble Lost") 
        OutputArray.append("Tackle Solo") 
        OutputArray.append("Tackle Assist") 
        OutputArray.append("Tackle For Loss") 
        OutputArray.append("Tackle For Loss Yard") 
        OutputArray.append("Sack")
        OutputArray.append("Sack Yard")
        OutputArray.append("QB Hurry") 
        OutputArray.append("Fumble Forced") 
        OutputArray.append("Pass Broken Up") 
        OutputArray.append("Kick/Punt Blocked") 
        OutputArray.append("1st Down Rush")
        OutputArray.append("1st Down Pass")
        OutputArray.append("1st Down Penalty") 
        OutputArray.append("Time Of Possession") 
        OutputArray.append("Penalty") 
        OutputArray.append("Penalty Yard") 
        OutputArray.append("Third Down Att") 
        OutputArray.append("Third Down Conv") 
        OutputArray.append("Fourth Down Att") 
        OutputArray.append("Fourth Down Conv") 
        OutputArray.append("Red Zone Att") 
        OutputArray.append("Red Zone TD") 
        OutputArray.append("Red Zone Field Goal") 
        return OutputArray
