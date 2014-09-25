import re

# Holds data for a penalty
class Penalty:
	def __init__(self, game_code, team_code, play_num):
		self.Game_Code = game_code
		self.Play_Num = play_num
		self.Team_Code = team_code
		self.Type = ""
		self.Yards = 0
		self.No_Play = 0
		self.Player = ""
		self.Field_Pos = 0
		self.Declined = 0
		self.First_down = 0

	def Compile_Play(self):
		OutputArray = []
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Play_Num))
		OutputArray.append(str(self.Team_Code))
		OutputArray.append(str(self.Type))
		OutputArray.append(str(self.Yards))
		OutputArray.append(str(self.No_Play))
		OutputArray.append(str(self.Player))
		OutputArray.append(str(self.Field_Pos))
		OutputArray.append(str(self.Declined))
		return OutputArray