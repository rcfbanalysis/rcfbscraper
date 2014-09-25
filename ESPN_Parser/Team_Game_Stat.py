import re
from Rushing_Play import *

# Holds the data for a team-game stats
class Team_Game_Stat:

    # Constructor
    def __init__(self, game_code, team_code):
        self.Game_Code = game_code
        self.Team_Code = team_code
        self.Rush_Att = 0
        self.Rush_Yard = 0
        self.Rush_TD = 0
        self.Pass_Att = 0
        self.Pass_Comp = 0
        self.Pass_Yard = 0
        self.Pass_TD = 0
        self.Pass_Int = 0
        self.Pass_Conv = 0 #NA
        self.Kickoff_Ret = 0
        self.Kickoff_Ret_Yard = 0
        self.Kickoff_Ret_TD = 0
        self.Punt_Ret = 0
        self.Punt_Ret_Yard = 0
        self.Punt_Ret_TD = 0
        self.Fum_Ret = 0
        self.Fum_Ret_Yard = 0 #NA
        self.Fum_Ret_TD = 0
        self.Int_Ret = 0
        self.Int_Ret_Yard = 0 #NA
        self.Int_Ret_TD = 0
        self.Misc_Ret = 0 #NA
        self.Misc_Ret_Yard = 0 #NA
        self.Misc_Ret_TD = 0 #NA
        self.Field_Goal_Att = 0
        self.Field_Goal_Made = 0
        self.Off_XP_Kick_Att = 0
        self.Off_XP_Kick_Made = 0
        self.Off_2XP_Att = 0 #NA
        self.Off_2XP_Made = 0 #NA
        self.Def_2XP_Att = 0 #NA
        self.Def_2XP_Made = 0 #NA
        self.Safety = 0     # incomplete (only checks passing and rushing plays)
        self.Points = 0
        self.Punt = 0
        self.Punt_Yard = 0
        self.Kickoff = 0
        self.Kickoff_Yard = 0
        self.Kickoff_Touchback = 0
        self.Kickoff_Out_Of_Bounds = 0
        self.Kickoff_Onsides = 0 #NA
        self.Fumble = 0
        self.Fum_Lost = 0
        self.Tackle_Solo = 0 #NA
        self.Tackle_Assist = 0 #NA
        self.Tackle_For_Loss = 0
        self.Tackle_For_Loss_Yard = 0
        self.Sack = 0
        self.Sack_Yard = 0
        self.QB_Hurry = 0 #NA
        self.Fum_Forced = 0
        self.Pass_Broken_Up = 0 #NA
        self.Kick_Punt_Blocked = 0 #NA
        self.First_Down_Rush = 0
        self.First_Down_Pass = 0
        self.First_Down_Penalty = 0
        self.Time_Of_Possession = 0
        self.Penalty = 0
        self.Penalty_Yard = 0 # inaccurate
        self.Third_Down_Att = 0
        self.Third_Down_Conv = 0
        self.Fourth_Down_Att = 0
        self.Fourth_Down_Conv = 0
        self.Red_Zone_Att = 0
        self.Red_Zone_TD = 0 #NA
        self.Red_Zone_Field_Goal = 0 #NA


    # =============================================================================================================
    # Kickoff
    # =============================================================================================================
    def Add_Off_Kickoff_Stats(self, ret_yards, td, fumble, fumble_lost, extra_point, returned):
        if returned:
            self.Kickoff_Ret += 1
            self.Kickoff_Ret_Yard += ret_yards
            self.Kickoff_Ret_TD += td
            self.Fumble += fumble
            self.Fum_Lost += fumble_lost
            if td == 1 and fumble_lost == 0 and extra_point > -1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point

    def Add_Def_Kickoff_Stats(self, yardage, touchback, out_of_bounds, td, fumble, fumble_lost, extra_point):
        self.Kickoff += 1
        if yardage != "NA":
            self.Kickoff_Yard += yardage
        self.Kickoff_Touchback += touchback
        self.Kickoff_Out_Of_Bounds += out_of_bounds
        self.Fum_Ret += fumble_lost
        if fumble == 1:
            self.Fum_Forced += 1
        if fumble_lost == 1 and td == 1:
            self.Fum_Ret_TD += td
            if extra_point > -1 and td == 1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point


    # =============================================================================================================
    # Punt
    # =============================================================================================================
    def Add_Off_Punt_Stats(self, ret_yards, td, fumble, fumble_lost, extra_point, returned):
        if returned:
            self.Punt_Ret += 1
            self.Punt_Ret_Yard += ret_yards
            self.Punt_Ret_TD += td
            self.Fumble += fumble
            self.Fum_Lost += fumble_lost
            if td == 1 and fumble_lost == 0 and extra_point > -1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point

    def Add_Def_Punt_Stats(self, yardage, td, fumble, fumble_lost, extra_point):
        self.Punt += 1
        if yardage != "NA":
            self.Punt_Yard += yardage
        self.Fum_Ret += fumble_lost
        if fumble == 1:
            self.Fum_Forced += 1
        if fumble_lost == 1 and td == 1:
            self.Fum_Ret_TD += td
            if extra_point > -1 and td == 1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point


    # =============================================================================================================
    # Field goal
    # =============================================================================================================
    def Add_Field_Goal_Off_Stats(self, kicker, distance, result, red_zone):
        self.Field_Goal_Att += 1
        self.Field_Goal_Made += (1 if result == "GOOD" else 0)
        if red_zone == 1 and result == "GOOD":
            self.Red_Zone_Field_Goal += 1


    # =============================================================================================================
    # Rush
    # =============================================================================================================
    def Add_Off_Rush_Stats(self, rush_play, extra_point, play_info, red_zone):
        self.Rush_Att += 1
        self.Rush_Yard += rush_play.Yards
        self.Rush_TD += rush_play.Touchdown
        self.Fumble += rush_play.Fumble
        self.Fum_Lost += rush_play.Fumble_Lost
        if rush_play.Touchdown == 1 and rush_play.Fumble_Lost == 0 and extra_point > -1:
            self.Off_XP_Kick_Att += 1
            self.Off_XP_Kick_Made += extra_point
        self.First_Down_Rush += rush_play.First_down
        (down, dist, team, pos) = self.Get_Play_Info(play_info)
        if down > -1:
            if down == 3:
                self.Third_Down_Att += 1
            if down == 3 and rush_play.First_down == 1:
                self.Third_Down_Conv += 1
            if down == 4:
                self.Fourth_Down_Att += 1
            if down == 4 and rush_play.First_down == 1:
                self.Fourth_Down_Conv += 1
        if rush_play.Touchdown == 1 and rush_play.Fumble_Lost == 0 and red_zone == 1:
            self.Red_Zone_TD += 1

    def Add_Def_Rush_Stats(self, rush_play, td, extra_point):
        self.Fum_Ret += rush_play.Fumble_Lost
        if rush_play.Fumble_Lost == 1:
            self.Fum_Ret_TD += td
            if extra_point > -1 and td == 1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point
        self.Safety += rush_play.Safety
        if rush_play.Yards < 0:
            self.Tackle_For_Loss += 1
            self.Tackle_For_Loss_Yard += rush_play.Yards
        self.Sack += rush_play.Sack
        if rush_play.Sack == 1:
            self.Sack_Yard += rush_play.Yards
        self.Fum_Forced += rush_play.Fumble


    # =============================================================================================================
    # Pass
    # =============================================================================================================
    def Add_Off_Pass_Stats(self, pass_play, extra_point, play_info, red_zone):
        self.Pass_Att += 1
        self.Pass_Comp += pass_play.Completion
        self.Pass_Yard += pass_play.Yards
        self.Pass_TD += pass_play.Touchdown
        self.Pass_Int += pass_play.Interception
        self.Pass_Conv += 0     # still don't know what this is exactly
        self.Fumble += pass_play.Fumble
        self.Fum_Lost += pass_play.Fumble_Lost
        if pass_play.Touchdown == 1 and pass_play.Interception + pass_play.Fumble_Lost == 0 and extra_point > -1:
            self.Off_XP_Kick_Att += 1
            self.Off_XP_Kick_Made += extra_point
        self.First_Down_Pass += pass_play.First_down
        (down, dist, team, pos) = self.Get_Play_Info(play_info)
        if down > -1:
            if down == 3:
                self.Third_Down_Att += 1
            if down == 3 and pass_play.First_down == 1:
                self.Third_Down_Conv += 1
            if down == 4:
                self.Fourth_Down_Att += 1
            if down == 4 and pass_play.First_down == 1:
                self.Fourth_Down_Conv += 1
        if pass_play.Touchdown == 1 and pass_play.Fumble_Lost == 0 and red_zone == 1:
            self.Red_Zone_TD += 1

    def Add_Def_Pass_Stats(self, pass_play, td, extra_point):
        self.Int_Ret += pass_play.Interception
        if pass_play.Interception == 1:
            self.Int_Ret_TD += td
            if td == 1 and extra_point > -1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point
        self.Fum_Ret += pass_play.Fumble_Lost
        if pass_play.Fumble_Lost == 1:
            self.Fum_Ret_TD += td
            if extra_point > -1 and td == 1:
                self.Off_XP_Kick_Att += 1
                self.Off_XP_Kick_Made += extra_point
        self.Safety += pass_play.Safety
        if pass_play.Yards < 0:
            self.Tackle_For_Loss += 1
            self.Tackle_For_Loss_Yard += pass_play.Yards
        self.Sack += pass_play.Sack
        if pass_play.Sack == 1:
            self.Sack_Yard += pass_play.Yards
        self.Fum_Forced += pass_play.Fumble


    # =============================================================================================================
    # Penalty
    # =============================================================================================================
    def Add_Off_Penalty_Stats(self, penalty):
        self.First_Down_Penalty += penalty.First_down

    def Add_Def_Penalty_Stats(self, penalty):
        self.Penalty += 1
        self.Penalty_Yard += penalty.Yards


    def Get_Play_Info(self, play_info):
        m = re.match(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?:(?P<team>\D+) (?P<pos>\d+)|(?P<fifty>50)))", play_info)
        if m == None:
            print "\nWARNING: No play info found"
            raw_input(play_info)
            return (-1, -1, -1, -1)
        down = int(m.group("down"))
        dist = m.group("dist")
        if None == m.group("fifty"):
            team = m.group("team")
            pos = int(m.group("pos"))
        else:
            pos = 50
        if m.group("dist") == "Goal":
            dist = pos
        return (down, int(dist), m.group("team"), pos)


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
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Kickoff_Ret))
        OutputArray.append(str(self.Kickoff_Ret_Yard))
        OutputArray.append(str(self.Kickoff_Ret_TD))
        OutputArray.append(str(self.Punt_Ret))
        OutputArray.append(str(self.Punt_Ret_Yard))
        OutputArray.append(str(self.Punt_Ret_TD))
        OutputArray.append(str(self.Fum_Ret))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fum_Ret_TD))
        OutputArray.append(str(self.Int_Ret))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Int_Ret_TD))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Field_Goal_Att))
        OutputArray.append(str(self.Field_Goal_Made))
        OutputArray.append(str(self.Off_XP_Kick_Att))
        OutputArray.append(str(self.Off_XP_Kick_Made))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Safety))
        OutputArray.append(str(self.Points))
        OutputArray.append(str(self.Punt))
        OutputArray.append(str(self.Punt_Yard))
        OutputArray.append(str(self.Kickoff))
        OutputArray.append(str(self.Kickoff_Yard))
        OutputArray.append(str(self.Kickoff_Touchback))
        OutputArray.append(str(self.Kickoff_Out_Of_Bounds))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fumble))
        OutputArray.append(str(self.Fum_Lost))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Tackle_For_Loss))
        OutputArray.append(str(self.Tackle_For_Loss_Yard))
        OutputArray.append(str(self.Sack))
        OutputArray.append(str(self.Sack_Yard))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fum_Forced))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
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
