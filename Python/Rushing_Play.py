import re
import CONST
from Passing_Play import *
from Passing_Play_Info import *

# Holds the data for a passing play
class Rushing_Play:

	# Constructor
	def __init__(self, game_code, play_num, team_code, rusher, yards, touchdown, first_down, fumble, fumble_lost, sack, safety, team_1, team_2):
		self.Game_Code = game_code
		self.Play_Num = play_num
		self.Team_Code = team_code
		self.Rusher = rusher
		self.Attempt = 1
		self.Yards = yards
		self.Touchdown = touchdown
		self.First_down = first_down
		self.Fumble = fumble
		self.Fumble_Lost = fumble_lost
		self.Sack = sack
		self.Safety = safety
		self.team_1 = team_1
		self.team_2 = team_2


	# Returns an array of relavent information
	def Compile_Play(self):
		OutputArray = []
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Play_Num))
		OutputArray.append(str(self.Team_Code))
		OutputArray.append(str(self.Rusher))
		OutputArray.append(str(self.Attempt))
		OutputArray.append(str(self.Yards))
		OutputArray.append(str(self.Touchdown))
		OutputArray.append(str(self.First_down))
		OutputArray.append(str(self.Fumble))
		OutputArray.append(str(self.Fumble_Lost))
		OutputArray.append(str(self.Sack))
		OutputArray.append(str(self.Safety))
		return OutputArray