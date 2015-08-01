import re
import C

# Holds the data for a play
class Play_Attributes:

	def __init__(self, pos, down, dist):
		self.Pos = 5*pos
		self.Down = down + 1
		self.Dist = dist
		self.Plays = 0
		self.Runs = 0
		self.Rush_Yards = []
		self.Rush_Exp_Yards = 0
		self.Rush_Pts = []
		self.Rush_Exp_Pts = 0
		self.Passes = 0
		self.Pass_Yards = []
		self.Pass_Exp_Yards = 0
		self.Pass_Pts = []
		self.Pass_Exp_Pts = 0
		self.Sacks = 0
		self.Sack_Yards = []
		self.Sack_Exp_Yards = 0
		self.Sack_Pts = []
		self.Sack_Exp_Pts = 0
		self.Punts = 0
		self.FGs = 0
		self.Expected_Yards = 0
		self.Expected_Pts = 0

	# Gets averages for play types
	def Get_Expected_Yards(self):
		if self.Runs > 0:
			self.Rush_Exp_Yards = float(reduce(lambda x, y: x + y, self.Rush_Yards)) / self.Runs
		if self.Passes > 0:
			self.Pass_Exp_Yards = float(reduce(lambda x, y: x + y, self.Pass_Yards)) / self.Passes
		if self.Sacks > 0:
			self.Sack_Exp_Yards = float(reduce(lambda x, y: x + y, self.Sack_Yards)) / self.Sacks
		if self.Runs + self.Passes + self.Sacks > 0:
			self.Expected_Yards = (self.Runs*self.Rush_Exp_Yards + self.Passes*self.Pass_Exp_Yards + self.Sacks*self.Sack_Exp_Yards) / (self.Runs + self.Passes + self.Sacks)

	# Gets averages for play types
	def Get_Expected_Points(self):
		if self.Runs > 0:
			self.Rush_Exp_Pts = float(reduce(lambda x, y: x + y, self.Rush_Pts)) / self.Runs
		if self.Passes > 0:
			self.Pass_Exp_Pts = float(reduce(lambda x, y: x + y, self.Pass_Pts)) / self.Passes
		if self.Sacks > 0:
			self.Sack_Exp_Pts = float(reduce(lambda x, y: x + y, self.Sack_Pts)) / self.Sacks
		if self.Runs + self.Passes + self.Sacks > 0:
			self.Expected_Pts = (self.Runs*self.Rush_Exp_Pts + self.Passes*self.Pass_Exp_Pts + self.Sacks*self.Sack_Exp_Pts) / (self.Runs + self.Passes + self.Sacks)


	# Allows data to be written to file
	def Compile_Data(self):
		self.Get_Expected_Yards()
		self.Get_Expected_Points()
		OutputArray = []
		OutputArray.append(str(self.Pos))
		OutputArray.append(str(self.Down))
		OutputArray.append(str(self.Dist))
		OutputArray.append(str(self.Plays))
		OutputArray.append(str(self.Runs))
		OutputArray.append(str(self.Rush_Exp_Yards))
		OutputArray.append(str(self.Rush_Exp_Pts))
		OutputArray.append(str(self.Passes))
		OutputArray.append(str(self.Pass_Exp_Yards))
		OutputArray.append(str(self.Pass_Exp_Pts))
		OutputArray.append(str(self.Sacks))
		OutputArray.append(str(self.Sack_Exp_Yards))
		OutputArray.append(str(self.Sack_Exp_Pts))
		OutputArray.append(str(self.Punts))
		OutputArray.append(str(self.FGs))
		OutputArray.append(str(self.Expected_Yards))
		OutputArray.append(str(self.Expected_Pts))
		return OutputArray

   	# Returns the header for a play type
   	def Header(self):
   		OutputArray = []
   		OutputArray.append("Position")
		OutputArray.append("Down")
		OutputArray.append("Distance")
		OutputArray.append("Plays")
		OutputArray.append("Runs")
		OutputArray.append("Run Yards Exp")
		OutputArray.append("Run Points Exp")
		OutputArray.append("Passes")
		OutputArray.append("Pass Yards Exp")
		OutputArray.append("Pass Points Exp")
		OutputArray.append("Sacks")
		OutputArray.append("Sack Yards Exp")
		OutputArray.append("Sack Points Exp")
		OutputArray.append("Punts")
		OutputArray.append("Field Goals")
		OutputArray.append("Expected Yards")
		OutputArray.append("Expected Points")
		return OutputArray
