import re

# Holds the data for a passing play
class Passing_Play:

	# Constructor
	def __init__(self, game_code, play_num, team_code, passer, completion):
		self.Game_Code = game_code
		self.Play_Num = play_num
		self.Team_Code = team_code
		self.Passer = passer
		self.Receiver = ""
		self.Attempt = 1
		self.Completion = completion
		self.Yards = 0
		self.Touchdown = 0
		self.Interception = 0
		self.First_down = 0
		self.Dropped = 0
		self.Sack = 0
		self.Safety = 0
		self.Fumble = 0
		self.Fumble_Lost = 0


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
		OutputArray.append("NA")
		OutputArray.append(str(self.Sack))
		OutputArray.append(str(self.Safety))
		return OutputArray