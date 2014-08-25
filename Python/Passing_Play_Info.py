import re
import CONST
from Passing_Play import *

# Holds the data row from a play
class Passing_Play_Info:

	# Constructor
	def __init__(self, info):
		self.data = self.Set_Play_Ints(info)
		self.play_num = 0
		self.turnover = 0
		self.completion = 0
		self.touchdown = 0
		self.interception = 0
		self.first_down = 0
		self.sack = 0
		self.safety = 0
		self.team_1 = self.data[CONST.OFF]
		self.team_2 = self.data[CONST.DEF]


	# Sets the appropriate cells in play info from /u/millsGT49 data to integers
	def Set_Play_Ints(self, info):
		for i in range(0, len(info)):
			try:					# convert to int
				info[i] = int(info[i])
				continue
			except:					# is a string
				pass
			if i == CONST.CLK:		# convert clock
				info[i] = self.Set_Clock(info[i])
		return info


	# Finds the time in input string and sets the clock
	def Set_Clock(self, input_clk):
		if None == re.search(r"\d{1,2}:\d{1,2}", input_clk):
			print "WARNING: Clock not set!\n"
			return input_clk
		else:
			time = re.findall(r"\d{1,2}:\d{1,2}", input_clk)
			time = time[0].split(":")
			return 60*int(time[0]) + int(time[1])


	# Checks for a turnover on a passing play
	def Turnover_Occurred(self, next_play):

		# Play result is a fumble/interception. Make sure the defense got the ball.
		if "Interception" == self.data[CONST.REST] or "Fumble" == self.data[CONST.REST]:
			if next_play.data[CONST.OFF] == self.data[CONST.DEF] and self.data[CONST.CODE] == next_play.data[CONST.CODE]:	# looks like the defense got the ball
				if self.data[CONST.QTR] == 2 and next_play.data[CONST.QTR] == 3:	# turnover occurred right at halftime. Mark as turnover and warn.
					print "WARNING: Play " + str(self.data[CONST.P_NUM]) + " appears to have a turnover at halftime. Recovering team unknown. Marking as a turnover.\n"
				self.turnover = 1
			else:	# looks like the offense got the ball back
				self.turnover = 0

		# Play result is a touchdown. Check who got the touchdown by using the extra point/2 point conversion.
		elif "Touchdown" == self.data[CONST.REST]:
			if next_play.data[CONST.TYPE] == "Extra.Point" or next_play.data[CONST.TYPE] == "Two.Point.Attempt":	# next play is extra point
				if self.Same_Offense(next_play):	# if the offense got a TD, no turnover occurred
					self.turnover = 0
				else:
					self.turnover = 1
			else:	# extra point not found, using INT
				if None != re.search("(intercept)|(fumble)", self.data[CONST.P_REST], re.IGNORECASE):	# looks like an turnover for touchdown
					self.turnover = 1
				else:
					self.turnover = 0
		else:
			self.turnover = 0


	# Determines whether a passing play was a completion
	def Completion(self, next_play):

		# Obvious case
		if "Completion" == self.data[CONST.REST]:
			self.completion = 1

		# If TD, check for a turnover. If none occurred, assume a completion
		elif "Touchdown" == self.data[CONST.REST]:
			if self.turnover == 1:
				if None != re.search(r"(intercept)", self.data[CONST.P_REST]):	# if turnover was interception
					self.completion = 0
				elif None != re.search(r"(fumble)", self.data[CONST.P_REST]):	# if turnover was fumble, check if the ball was passed or the QB was sacked
					if None != re.search(r"(sack)", self.data[CONST.P_REST]):	# on sack, assume QB fumbled
						self.completion = 0
					elif None != re.search(r"(pass)", self.data[CONST.P_REST]):	# if pass got off, assume receiver fumbled after completion
						self.completion = 1
			else:
				self.completion = 1

		# If Fumble, try to use the extra point / 2 pt conversion to determine who got the TD. If that doesn't work, assume offense got it.
		elif "Fumble" == self.data[CONST.REST]:
			if None != re.search(r"(sack)", self.data[CONST.P_REST]):	# on sack, assume QB fumbled
				self.completion = 0
			elif None != re.search(r"(pass)", self.data[CONST.P_REST]):	# if pass got off, assume receiver fumbled after completion
				self.completion = 1
		else:
			self.completion = 0


	# Checks if the next play has the same offense
	def Same_Offense(self, next_play):
		if next_play.data[CONST.OFF] == self.data[CONST.OFF]:
			return 1
		elif next_play.data[CONST.OFF] == self.data[CONST.DEF]:
			return 0


	# Determines whether a passing play was a touchdown (for the offense)
	def Touchdown_Occurred(self):
		if self.data[CONST.REST] == "Touchdown" and self.turnover == 0:
			self.touchdown = 1
		else:
			self.touchdown = 0


	# Determines whether a passing play was an interception (assuming there was a turnover)
	def Interception(self):
		if self.data[CONST.REST] == "Interception":	# obvious case
			self.interception = 1
		elif self.data[CONST.REST] == "Touchdown":	# touchdown may have been via interception
			if None != re.search("intercept", self.data[CONST.P_REST], re.IGNORECASE):	# interception for touchdown
				self.interception = 1
			else:
				self.interception = 0
		else:
			self.interception = 0


	# Determines whether a passing play was an 1st down
	def First_Down(self, next_play):

		# Looks like a 1st down
		if self.Same_Offense(next_play) and next_play.data[CONST.DOWN] == 1:
			if self.data[CONST.DIST] <= self.data[CONST.Y_DESC]:	# make sure yards needed <= yards gained
				self.first_down = 1
			elif None != re.search(r"penal", self.data[CONST.P_REST], re.IGNORECASE):	# check for things that would explain anamoly
				self.first_down = 0
			else:
				print "WARNING: Play " + str(self.data[CONST.P_NUM]) + " had a first down, but didn't get enough yards for one! Returning 0."
				print self.data[CONST.P_REST]
				print "Yards gained: " + str(self.data[CONST.Y_DESC])
				print "Yards needed: " + str(self.data[CONST.DIST]) + "\n"
				self.first_down = 0

		# Yards gained > needed, but no 1st down
		elif self.data[CONST.DIST] < self.data[CONST.Y_DESC]:
			if (next_play.data[CONST.QTR] == 3 and self.data[CONST.QTR] == 2) or next_play.data[CONST.CODE] != self.data[CONST.CODE]:
				self.first_down = 1 									# got a first down, but end of half/game
			elif "Penalty" == next_play.data[CONST.TYPE]:	# next play penalty explains the anamoly
				self.first_down = 0
			elif 0 == self.data[CONST.DIST]:				# "And Goal" explains the anamoly
				self.first_down = 0
			elif None != re.search(r"(touchdown)|(inter)|(fumble)", self.data[CONST.P_REST], re.IGNORECASE):	# check for things that would explain anamoly
				self.first_down = 1
			else:
				print "WARNING: Play " + str(self.data[CONST.P_NUM]) + " didn't have a first down, but got enough yards for one! Returning 0."
				print self.data[CONST.P_REST]
				print "Yards gained: " + str(self.data[CONST.Y_DESC])
				print "Yards needed: " + str(self.data[CONST.DIST]) + "\n"
				self.first_down = 0
		else:
			self.first_down = 0


	# Determines whether or not a sack occurred
	def Sack_Occurred(self):
		# First check the play result (more rigorous/quicker)
		if "Sack" == self.data[CONST.REST]:
			self.sack = 1
		# Next, look for 'sack' in the detailed play result
		elif None != re.search(r"(sack)", self.data[CONST.P_REST]):
			self.sack = 1
		else:
			self.sack = 0


	# Determines whether or not a safety occurred
	def Safety_Occurred(self, next_play):
		# Check if it was the last play before halftime
		if self.data[CONST.QTR] == 2 and next_play.data[CONST.QTR] == 3:
			if self.data[CONST.DEF] == next_play.data[CONST.DEF]:	# find which team got the sack and check if they got 2 points
				if self.data[CONST.D_PT] + 2 == next_play.data[CONST.D_PT]:
					self.safety = 1
				else:
					self.safety = 0
			else:
				if self.data[CONST.D_PT] + 2 == next_play.data[CONST.O_PT]:
					self.safety = 1
				else:
					self.safety = 0
		# Check if it was the last play of the game
		if self.data[CONST.CODE] != next_play.data[CONST.CODE]:
			try:
				if self.data[CONST.SPOT] - self.data[CONST.Y_DESC] >= 100:	# if so, must rely on change in yardage
					self.safety = 1
				else:
					self.safety = 0
			except:
				self.safety = 0
		# Check for a sack under normal circumstances
		if "Kickoff" == next_play.data[CONST.TYPE]:
			if self.data[CONST.D_PT] + 2 == next_play.data[CONST.D_PT]:
				self.safety = 1
			else:
				self.safety = 0
		else:
			self.safety = 0
