import re
import CONST
from Passing_Play import *
from Passing_Play_Info import *
from Rushing_Play import *
from Rushing_Play_Info import *

# Holds the data for a team-game stats
class Team_Game_Stat:

	# Constructor
	def __init__(self, game_code, team_code):
		self.Game_Code = game_code
		self.Team_Code = team_code
		self.Rush_Att = 0
		self.Rush_Yrd = 0
		self.Rush_TD = 0
		self.Rush_1st = 0
		self.Pass_Att = 0
		self.Pass_Comp = 0
		self.Pass_Yrd = 0
		self.Pass_TD = 0
		self.Pass_Int = 0
		self.Pass_1st = 0
		self.Safeties = 0
		self.Points = 0
		self.Fumble = 0
		self.Fumble_Lst = 0
		self.Sacks = 0
		self.Sack_Yrd = 0
		self.First_Rush = 0
		self.First_Pass = 0
		self.Pass_Plays = []
		self.Rush_Plays = []


	def Get_Passing_Totals(self):
		for play in self.Pass_Plays:
			self.Pass_Att += play.Attempt
			self.Pass_Comp += play.Completion
			try:	# handles "NA" yardage gains
				self.Pass_Yrd += play.Yards
			except:
				pass
			self.Pass_TD += play.Touchdown
			self.Pass_Int += play.Interception
			self.Pass_1st += play.First_down
			self.Safeties += play.Safety
			self.Sacks += play.Sack
			if play.Sack == 1:
				try:	# handles "NA" yardage gains
					self.Sack_Yrd += play.Yards
				except:
					pass


	def Get_Rushing_Totals(self):
		for play in self.Rush_Plays:
			self.Rush_Att += play.Attempt
			try:	# handles "NA" yardage gains
				self.Rush_Yrd += play.Yards
			except:
				pass
			self.Rush_TD += play.Touchdown
			self.Rush_1st += play.First_down
			self.Safeties += play.Safety
			self.Sacks += play.Sack
			if play.Sack == 1:
				try:	# handles "NA" yardage gains
					self.Sack_Yrd += play.Yards
				except:
					pass


	# Returns an array of relavent information
	def Compile_Stats(self):
		OutputArray = []
		OutputArray.append(str(self.Team_Code))
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Rush_Att))
		OutputArray.append(str(self.Rush_Yrd))
		OutputArray.append(str(self.Rush_TD))
		OutputArray.append(str(self.Pass_Att))
		OutputArray.append(str(self.Pass_Comp))
		OutputArray.append(str(self.Pass_Yrd))
		OutputArray.append(str(self.Pass_TD))
		OutputArray.append(str(self.Pass_Int))
		OutputArray.append(str(self.Safeties))
		OutputArray.append(str(self.Sacks))
		OutputArray.append(str(self.Sack_Yrd))
		OutputArray.append(str(self.Pass_1st))
		OutputArray.append(str(self.Rush_1st))
		return OutputArray