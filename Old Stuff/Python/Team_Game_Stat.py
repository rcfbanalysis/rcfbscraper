import re
import CONST
from Play import *

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


    def Add_Off_Stats(self, play):
        self.Rush_Att += play.Rush_Att
        try:
            self.Rush_Yard += play.Rush_Yard
        except:
            self.Rush_Yard += 0
        self.Rush_TD += play.Rush_TD
        self.Pass_Att += play.Pass_Att
        self.Pass_Comp += play.Pass_Comp
        try:
            self.Pass_Yard += play.Pass_Yard
        except:
            self.Pass_Yard += 0
        self.Pass_TD += play.Pass_TD
        self.Pass_Int += play.Pass_Int
        self.Pass_Conv += play.Pass_Conv
        self.Field_Goal_Att += play.Field_Goal_Att
        self.Field_Goal_Made += play.Field_Goal_Made
        self.Off_XP_Kick_Att += play.Off_XP_Kick_Att
        self.Off_XP_Kick_Made += play.Off_XP_Kick_Made
        self.Off_2XP_Att += play.Off_2XP_Att
        self.Off_2XP_Made += play.Off_2XP_Made
        self.Safety += play.Safety
        self.Points = play.Points
        self.Punt += play.Punt
        self.Punt_Yard += play.Punt_Yard
        self.Kickoff += play.Kickoff
        self.Kickoff_Yard += play.Kickoff_Yard
        self.Kickoff_Touchback += play.Kickoff_Touchback
        self.Kickoff_Out_Of_Bounds += play.Kickoff_Out_Of_Bounds
        self.Kickoff_Onsides += play.Kickoff_Onsides
        self.Fumble += play.Fumble
        self.Fumble_Lost += play.Fumble_Lost
        self.Sack += play.Sack
        self.Sack_Yard += play.Sack_Yard
        self.First_Down_Rush += play.First_Down_Rush
        self.First_Down_Pass += play.First_Down_Pass
        self.First_Down_Penalty += play.First_Down_Penalty
        self.Time_Of_Possession += play.Time_Of_Possession
        self.Penalty += play.Penalty
        try:
            self.Penalty_Yard += play.Penalty_Yard
        except:
            self.Penalty_Yard += 0
        self.Third_Down_Att += play.Third_Down_Att
        self.Third_Down_Conv += play.Third_Down_Conv
        self.Fourth_Down_Att += play.Fourth_Down_Att
        self.Fourth_Down_Conv += play.Fourth_Down_Conv
        self.Red_Zone_Att += play.Red_Zone_Att
        self.Red_Zone_TD += play.Red_Zone_TD
        self.Red_Zone_Field_Goal += play.Red_Zone_Field_Goal


    def Add_Def_Stats(self, play):
        self.Kickoff_Ret += play.Kickoff_Ret
        self.Kickoff_Ret_Yard += play.Kickoff_Ret_Yard
        self.Kickoff_Ret_TD += play.Kickoff_Ret_TD
        self.Punt_Ret += play.Punt_Ret
        self.Punt_Ret_Yard += play.Punt_Ret_Yard
        self.Punt_Ret_TD += play.Punt_Ret_TD
        self.Fum_Ret += play.Fum_Ret
        self.Fum_Ret_Yard += play.Fum_Ret_Yard
        self.Fum_Ret_TD += play.Fum_Ret_TD
        self.Int_Ret += play.Int_Ret
        self.Int_Ret_Yard += play.Int_Ret_Yard
        self.Int_Ret_TD += play.Int_Ret_TD
        self.Misc_Ret += play.Misc_Ret
        self.Misc_Ret_Yard += play.Misc_Ret_Yard
        self.Misc_Ret_TD += play.Misc_Ret_TD
        self.Def_2XP_Att += play.Def_2XP_Att
        self.Def_2XP_Made += play.Def_2XP_Made
        self.Tackle_Solo += play.Tackle_Solo
        self.Tackle_Assist += play.Tackle_Assist
        self.Tackle_For_Loss += play.Tackle_For_Loss
        try:
            self.Tackle_For_Loss_Yard += play.Tackle_For_Loss_Yard
        except:
            self.Tackle_For_Loss_Yard += 0
        self.QB_Hurry += play.QB_Hurry
        self.Fumble_Forced += play.Fumble_Forced
        self.Pass_Broken_Up += play.Pass_Broken_Up
        self.Kick_Punt_Blocked += play.Kick_Punt_Blocked
        self.Penalty += 0
        self.Penalty_Yard += 0


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
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Kickoff_Ret_TD))
        OutputArray.append(str(self.Punt_Ret))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Punt_Ret_TD))
        OutputArray.append(str(self.Fum_Ret))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fum_Ret_TD))
        OutputArray.append(str(self.Int_Ret))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Int_Ret_TD))
        OutputArray.append(str(self.Misc_Ret))
        OutputArray.append(str("NA"))
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
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Kickoff))
        OutputArray.append(str(self.Kickoff_Yard))
        OutputArray.append(str(self.Kickoff_Touchback))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fumble))
        OutputArray.append(str(self.Fumble_Lost))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Tackle_For_Loss))
        OutputArray.append(str(self.Tackle_For_Loss_Yard))
        OutputArray.append(str(self.Sack))
        OutputArray.append(str(self.Sack_Yard))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Fumble_Forced))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Kick_Punt_Blocked))
        OutputArray.append(str(self.First_Down_Rush))
        OutputArray.append(str(self.First_Down_Pass))
        OutputArray.append(str(self.First_Down_Penalty))
        OutputArray.append(str(self.Time_Of_Possession))
        OutputArray.append(str("NA"))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Third_Down_Att))
        OutputArray.append(str(self.Third_Down_Conv))
        OutputArray.append(str(self.Fourth_Down_Att))
        OutputArray.append(str(self.Fourth_Down_Conv))
        OutputArray.append(str("NA"))
        OutputArray.append(str(self.Red_Zone_TD))
        OutputArray.append(str(self.Red_Zone_Field_Goal))
        return OutputArray
