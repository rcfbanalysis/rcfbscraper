# ================================================================
# ===== IMPORTS ==================================================
# ================================================================
import re
import CONST


# ================================================================
# ===== CLASSES ==================================================
# ================================================================

# Holds the data for a passing play
class Passing_Play:

	# Constructor
	def __init__(self, game_code, play_num, team_code, passer, receiver, completion, yards, touchdown, interception, first_down, dropped):
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
		return OutputArray


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
	def Passing_Turnover_Occured(self, next_play):

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
				if None != re.search("intercept", self.data[CONST.P_REST], re.IGNORECASE):	# looks like an interception for touchdown
					self.turnover = 1
				else:
					self.turnover = 0
		else:
			self.turnover = 0


	# Determines whether a passing play was a completion
	def Passing_Is_Completion(self, next_play):

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
	def Passing_Is_Touchdown(self):
		if self.data[CONST.REST] == "Touchdown" and self.turnover == 0:
			self.touchdown = 1
		else:
			self.touchdown = 0


	# Determines whether a passing play was an interception
	def Passing_Is_Interception(self):
		if self.data[CONST.REST] == "Interception":	# obvious case
			self.interception = 1
		elif self.data[CONST.REST] == "Touchdown":	# touchdown may have been via interception
			if None != re.search("intercept", self.data[CONST.P_REST], re.IGNORECASE):	# interception for touchdown
				self.interception = 1
			else:
				self.interception = 0
		else:
			self.interception = 0


	# Determines whether a passing play was an interception
	def Passing_Is_1st_Down(self, next_play):

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


# ==================================================================
# ===== FUNCTIONS ==================================================
# ==================================================================

# Returns the contents of a .csv file in an array
def Read_CSV(file_name):
	print "Reading \"" + str(file_name) + "\" data.\n"
	data_file = open(file_name, "r")
	data = []
	for row in data_file:
		data.append(row.strip("\n").split(","))
	data_file.close()
	# Remove parenthesis from the data
	for i in range(0, len(data)):
		for j in range(0, len(data[i])):
			data[i][j] = re.sub("\"", "", data[i][j])
	return data


# Writes the contents of an array to a .csv file
def Write_CSV(file_name, data):
	print "Writing \"" + str(file_name) + "\" data.\n"
	data_file = open(file_name, "w")
	for row in data:
		data_file.write(",".join(row) + "\n")
	data_file.close()
	return data


# Returns the team code and conference code for each 2014 team
def Read_Team_Data():
	# Open file and read data into an array
	file_name = "team_alt.csv"
	data = Read_CSV(file_name)
	data.pop(0)	# remove data header
	# Seperate the data and return
	team_codes = {}
	team_confs = {}
	for row in data:
		team_codes[row[1]] = row[0]
		team_confs[row[1]] = row[2]
	team_names = team_codes.keys()
	return (team_names, team_codes, team_confs)


# Replaces the team name string with a numerical team code
def Get_Team_Code(str_name, team_names, team_codes):
	longest_match = 0
	team_match = "NA"
	code = "0"
	str_name = re.sub("[\.()]", "", str_name)
	for name in team_names:
		if None != re.search(re.sub("[\.()]", "", name), str_name):		# there is a match
			if longest_match < len(name):	# this match is longer
				longest_match = len(name)
				code = team_codes[name]
				team_match = re.sub("[\.()]", "", name)
	if code == "0":
		print "WARNING: Team \"" + str_name + "\" has an undefined code!\n"
		raw_input()
	return code


# Replaces the string team names with team codes, then writes to alternate file
def Replace_Team_Names(data, team_names, team_codes):
	print "Replacing team names with codes...\n"
	prev_off_str = ""
	prev_def_str = ""
	prev_off_code = ""
	prev_def_code = ""
	for row in data[1:]:
		if None != re.search("Lafayette", str(row[6]) + str(row[7])):	# Ignore Lafayette game for now due to bug. *** REMOVE LATER ***
			continue
		if row[6] == prev_off_str and row[7] == prev_def_str:
			row[6] = prev_off_code
			row[7] = prev_def_code
		elif row[6] == prev_def_str and row[7] == prev_off_str:
			row[6] = prev_def_code
			row[7] = prev_off_code
		else:
			prev_off_str = row[6]
			prev_def_str = row[7]
			row[6] = Get_Team_Code(str(row[6]), team_names, team_codes)
			row[7] = Get_Team_Code(str(row[7]), team_names, team_codes)
			prev_off_code = row[6]
			prev_def_code = row[7]
	return data


# Uses season data to find and compile a list of passing plays
def Get_Passing_Plays(data):

	passing_plays = []
	passing_plays.append(Passing_Play_Header())
	play_num = 0
	for i in range(1, len(data)):

		# Get previous play data
		if i > 1:
			prev_play = Passing_Play_Info(data[i-1])
		else:
			prev_play = Passing_Play_Info([0] * len(data[i]))

		# Get this play
		play_info = Passing_Play_Info(data[i])

		# Get next play
		if i + 1 < len(data):
			next_play = Passing_Play_Info(data[i+1])
		else:
			next_play = Passing_Play_Info([0] * len(data[i]))
		
		# Ignore Lafayette game for now due to bug. *** REMOVE LATER ***
		if None != re.search("Lafayette", str(play_info.data[CONST.OFF]) + str(play_info.data[CONST.DEF])):
			continue

		# New game, reset play count
		if play_info.data[CONST.CODE] != prev_play.data[CONST.CODE]:
			play_num = 1
		else:
			play_num += 1
		play_info.play_num = play_num

		# Found a passing play, parse the data to gather info
		if "Pass" == play_info.data[CONST.TYPE]:
			play_info.Passing_Turnover_Occured(next_play)
			play_info.Passing_Is_Completion(next_play)
			play_info.Passing_Is_Touchdown()
			if play_info.turnover == 1:
				play_info.Passing_Is_Interception()
			play_info.Passing_Is_1st_Down(next_play)
			# Finalize all the data for the play
			game_code = play_info.data[CONST.CODE]
			play_num = play_info.play_num
			team_code = play_info.data[CONST.OFF]
			completion = play_info.completion
			yards = play_info.data[CONST.Y_DESC]
			touchdown = play_info.touchdown
			interception = play_info.interception
			first_down = play_info.first_down
			play = Passing_Play(game_code, play_num, team_code, "NA", "NA", completion, yards, touchdown, interception, first_down, 0)
			passing_plays.append(play.Compile_Play())

	return passing_plays


# Returns the header for a play type
def Passing_Play_Header():
	OutputArray = []
	OutputArray.append("Game Code")
	OutputArray.append("Play Number")
	OutputArray.append("Team Code")
	OutputArray.append("Passer Player Code")
	OutputArray.append("Receiver Play Code")
	OutputArray.append("Attempt")
	OutputArray.append("Completion")
	OutputArray.append("Yards")
	OutputArray.append("Touchdown")
	OutputArray.append("Interception")
	OutputArray.append("1st Down")
	OutputArray.append("Dropped")
	return OutputArray


# ======================================================================
# ===== MAIN FUNCTION ==================================================
# ======================================================================
print "\n"

# Get team data
(team_names, team_codes, team_confs) = Read_Team_Data()

# Read data and replace team names with team codes
file_name = "BowlGameData.csv"
data = Read_CSV(file_name)
data = Replace_Team_Names(data, team_names, team_codes)
Write_CSV("BowlGameData_alt.csv", data)

#  Compile passing plays and write to file
file_name = "pass_new.csv"
passing_plays = Get_Passing_Plays(data)
Write_CSV(file_name, passing_plays)


# ====================================================================
# ===== END PARSING ==================================================
# ====================================================================
print "Done! Press ENTER to continue."
raw_input()