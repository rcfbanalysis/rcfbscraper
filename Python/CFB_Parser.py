
# ===== IMPORTS ==================================================
import re
import CONST


# ===== CLASSES ==================================================

# Holds the data for a passing play
class Passing_Play:
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


# ===== FUNCTIONS ==================================================

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
	team_match = "NULL"
	code = "0"
	str_name = re.sub("[\.()]", "", str_name)
	for name in team_names:
		if None != re.search(re.sub("[\.()]", "", name), str_name):		# there is a match
			if longest_match < len(name):	# this match is longer
				longest_match = len(name)
				code = team_codes[name]
				team_match = re.sub("[\.()]", "", name)
	if code == "0":
		print "WARNING: Team \"" + str_name + "\" has an undefined code!"
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
	passing_plays.append(Play_Header())
	prev_game_code = 0
	for i in range(1, len(data)):

		# Get previous play data
		if i > 1:
			prev_play = Set_Play_Ints(data[i-1])
		else:
			prev_play = [0] * len(data)

		# Get this play
		play_info = Set_Play_Ints(data[i])

		# Get next play
		if i + 1 < len(data):
			next_play = Set_Play_Ints(data[i+1])
		else:
			next_play = [0] * len(data)
		
		if None != re.search("Lafayette", str(play_info[6]) + str(play_info[7])):	# Ignore Lafayette game for now due to bug. *** REMOVE LATER ***
			continue

		if play_info[CONST.CODE] != prev_game_code:	# new game, reset play count
			play_num = 1
		else:
			play_num += 1

		prev_game_code = play_info[CONST.CODE]

		# Found a passing play, parse the data to gather info
		if None != re.search("pass", play_info[CONST.TYPE], re.IGNORECASE):
			game_code = play_info[CONST.CODE]
			team_code = play_info[CONST.OFF]
			passer = "NULL"
			receiver = "NULL"
			completion = Passing_Is_Completion(prev_play, play_info, next_play)
			yards = play_info[CONST.Y_DESC]
			touchdown = Passing_Is_Touchdown(prev_play, play_info, next_play, completion)
			interception = Passing_Is_Interception(prev_play, play_info, next_play)
			first_down = Passing_Is_1st_Down(prev_play, play_info, next_play)
			dropped = 0		# currently no drop data
			play = Passing_Play(game_code, play_num, team_code, passer, receiver, completion, yards, touchdown, interception, first_down, dropped)
			passing_plays.append(play.Compile_Play())

	return passing_plays


# Determines whether a passing play was a completion
def Passing_Is_Completion(prev_play, play_info, next_play):
	if play_info[CONST.REST] == "Completion":
		return 1
	# If TD, try to use the extra point / 2 pt conversion to determine who got the TD. If that doesn't work, check for INT.
	elif play_info[CONST.REST] == "Touchdown":
		if next_play[CONST.TYPE] == "Extra.Point" or next_play[CONST.TYPE] == "Two.Point.Attempt":	# next play is extra point
			return Same_Offense(play_info, next_play)
		else:	# extra point not found, using INT
			if None != re.search("intercept", play_info[CONST.P_REST], re.IGNORECASE):	# interception for touchdown
				return 0
			else:
				return 1
	# If Fumble, try to use the extra point / 2 pt conversion to determine who got the TD. If that doesn't work, assume offense got it.
	elif play_info[CONST.REST] == "Fumble":
		if next_play[CONST.TYPE] == "Extra.Point" or next_play[CONST.TYPE] == "Two.Point.Attempt":	# next play is extra point
			return Same_Offense(play_info, next_play)
		else:
			return 1
	else:
		return 0


# Determines whether a passing play was a touchdown (for the offense)
def Passing_Is_Touchdown(prev_play, play_info, next_play, completion):
	if play_info[CONST.REST] == "Touchdown" and completion == 1:
		return 1
	else:
		return 0


# Determines whether a passing play was an interception
def Passing_Is_Interception(prev_play, play_info, next_play):
	if play_info[CONST.REST] == "Interception":
		return 1
	elif play_info[CONST.REST] == "Touchdown":
		if None != re.search("intercept", play_info[CONST.P_REST], re.IGNORECASE):	# interception for touchdown
			return 1
		else:
			return 0
	else:
		return 0


# Determines whether a passing play was an interception
def Passing_Is_1st_Down(prev_play, play_info, next_play):
	if Same_Offense(play_info, next_play) and next_play[CONST.DOWN] == 1:
		if play_info[CONST.DIST] <= play_info[CONST.Y_DESC]:
			return 1
		elif None != re.search(r"penal", play_info[CONST.P_REST], re.IGNORECASE):	# check for things that would explain anamoly
			return 0
		else:
			print "WARNING: Showing this team got a first down, but didn't get enough yards for one! Returning 0."
			print play_info
			print "Yards gained: " + str(play_info[CONST.Y_DESC])
			print "Yards needed: " + str(play_info[CONST.DIST])
			return 0
	elif play_info[CONST.DIST] < play_info[CONST.Y_DESC]:	# yards gained > needed, but no 1st down
		if next_play[CONST.QTR] > play_info[CONST.QTR] or next_play[CONST.CODE] != play_info[CONST.CODE]:	# got a first down, but end of half/game
			return 1
		elif next_play[CONST.TYPE] == "Penalty":	# next play penalty explains the anamoly
			return 0
		elif play_info[CONST.DIST] == 0:			# "And Goal" explains the anamoly
			return 0
		elif None != re.search(r"(touchdown)|(inter)|(fumble)", play_info[CONST.P_REST], re.IGNORECASE):	# check for things that would explain anamoly
			return 1
		else:
			print "WARNING: Showing this team didn't get a first down, but got enough yards for one! Returning 0."
			print "Yards gained: " + str(play_info[CONST.Y_DESC])
			print "Yards needed: " + str(play_info[CONST.DIST])
			print play_info
			return 0

	else:
		return 0


# Checks if the next play has the same offense
def Same_Offense(play_info, next_play):
	if next_play[CONST.OFF] == play_info[CONST.OFF]:
		return 1
	elif next_play[CONST.OFF] == play_info[CONST.DEF]:
		return 0


# Returns the header for a play type
def Play_Header():
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


# Sets the appropriate cells in play info from /u/millsGT49 data to integers
def Set_Play_Ints(play_info):
	not_int_list = [CONST.CLK, CONST.TYPE, CONST.REST, CONST.P_INFO, CONST.P_REST, CONST.H_TEAM, CONST.A_TEAM, CONST.CODE]
	for i in range(0, len(play_info)):
		try:					# convert to int
			play_info[i] = int(play_info[i])
			continue
		except:					# is a string
			pass
		if i == CONST.CLK:		# convert clock
			play_info[i] = Set_Clock(play_info[i])
	return play_info


# Finds the time in input string and sets the clock
def Set_Clock(input_clk):
	if None == re.search(r"\d{1,2}:\d{1,2}", input_clk):
		print "WARNING: Clock not set!"
		return input_clk
	else:
		time = re.findall(r"\d{1,2}:\d{1,2}", input_clk)
		time = time[0].split(":")
		return 60*int(time[0]) + int(time[1])


# ===== MAIN FUNCTION ==================================================
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


# ===== END PARSING ==================================================
print "Done! Press ENTER to continue."
raw_input()