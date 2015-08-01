import re

# Holds the data for a drive
class Drive:

	# Constructor
	def __init__(self, game_code, offense, defense, time, quarter, drive_num):
		self.Game_Code = game_code
		self.Offense = offense
		self.Defense = defense
		self.Start_Time = time
		self.Start_Spot = 0
		self.Start_Qrt = quarter
		self.Drive_Num = drive_num
		self.Raw_Pbp_Data = []
		self.Plays = 0
		self.Yards = 0
		self.Stop_Time = 0
		self.Stop_Spot = 0
		self.Stop_Qrt = 0
		self.Time_Of_Pos = 0
		self.Red_Zone_Att = 0
		self.Finished = 0
		self.Play_List = []

		# TO-DO
		self.Start_Reason = 0
		self.Stop_Reason = 0


	# Sets the drive summary
	def Set_Summary(self, plays, yards, time, quarter):
		self.Plays = plays
		self.Yards = yards
		self.Stop_Qrt = quarter
		self.Time_Of_Pos = time
		if self.Start_Qrt == self.Stop_Qrt:
			self.Stop_Time = self.Start_Time - self.Time_Of_Pos
		else:
			self.Stop_Time = 900 - self.Time_Of_Pos
		self.Finished = 1


	# Returns an array of relavent information
	def Compile_Stats(self):
		OutputArray = []
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Drive_Num))
		OutputArray.append(str(self.Offense))
		OutputArray.append(str(self.Start_Qrt))
		OutputArray.append(str(self.Start_Time))
		OutputArray.append(str(self.Start_Spot))
		OutputArray.append(str(self.Start_Reason))
		OutputArray.append(str(self.Stop_Qrt))
		OutputArray.append(str(self.Stop_Time))
		OutputArray.append(str(self.Stop_Spot))
		OutputArray.append(str(self.Stop_Reason))
		OutputArray.append(str(self.Plays))
		OutputArray.append(str(self.Yards))
		OutputArray.append(str(self.Time_Of_Pos))
		OutputArray.append(str(self.Red_Zone_Att))
		OutputArray.append(str(self.Finished))
		return OutputArray


	# Returns the header for a play type
	def Header(self):
		OutputArray = []
		OutputArray.append("Game_Code")
		OutputArray.append("Drive_Num")
		OutputArray.append("Offense")
		OutputArray.append("Start_Qrt")
		OutputArray.append("Start_Time")
		OutputArray.append("Start_Spot")
		OutputArray.append("Start_Reason")
		OutputArray.append("Stop_Qrt")
		OutputArray.append("Stop_Time")
		OutputArray.append("Stop_Spot")
		OutputArray.append("Stop_Reason")
		OutputArray.append("Plays")
		OutputArray.append("Yards")
		OutputArray.append("Time_Of_Pos")
		OutputArray.append("Red_Zone_Att")
		OutputArray.append("Summary_Produced")
		return OutputArray