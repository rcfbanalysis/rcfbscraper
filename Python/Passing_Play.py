import re
import CONST
from Passing_Play import *
from Passing_Play_Info import *

# Holds the data for a passing play
class Passing_Play:

	# Constructor
	def __init__(self, game_code, play_num, team_code, passer, receiver, completion, yards, touchdown, interception, first_down, dropped, sack):
		self.Game_Code = game_code
		self.Play_Num = play_num
		self.Team_Code = team_code
		self.Passer = passer
		self.Receiver = receiver
		self.Attempt = 1
		self.Completion = completion
		self.Yards = yards
		self.Touchdown = touchdown
		self.Interception = interception
		self.First_down = first_down
		self.Dropped = dropped
		self.Sack = sack


	# Returns an array of relavent information
	def Compile_Play(self):
		OutputArray = []
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Play_Num))
		OutputArray.append(str(self.Team_Code))
		OutputArray.append(str(self.Passer))
		OutputArray.append(str(self.Receiver))
		OutputArray.append(str(self.Attempt))
		OutputArray.append(str(self.Completion))
		OutputArray.append(str(self.Yards))
		OutputArray.append(str(self.Touchdown))
		OutputArray.append(str(self.Interception))
		OutputArray.append(str(self.First_down))
		OutputArray.append(str(self.Dropped))
		OutputArray.append(str(self.Sack))
		return OutputArray