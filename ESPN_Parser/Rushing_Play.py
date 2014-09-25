import re

# Holds the data for a passing play
class Rushing_Play:
	def __init__(self, game_code, play_num, team_code, rusher):
		self.Game_Code = game_code
		self.Play_Num = play_num
		self.Team_Code = team_code
		self.Rusher = rusher
		self.Attempt = 1
		self.Yards = 0
		self.Touchdown = 0
		self.First_down = 0
		self.Fumble = 0
		self.Fumble_Lost = 0
		self.Sack = 0
		self.Safety = 0


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