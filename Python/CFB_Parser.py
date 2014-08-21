# ================================================================
# ===== IMPORTS ==================================================
# ================================================================
import re
import CONST
from Passing_Play import *
from Passing_Play_Info import *


# ========================================================================
# ===== CLASSES UNDER DEVELOPMENT ========================================
# ========================================================================




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
			play_info.Passing_Is_Sack()
			# Finalize all the data for the play
			game_code = play_info.data[CONST.CODE]
			play_num = play_info.play_num
			team_code = play_info.data[CONST.OFF]
			completion = play_info.completion
			yards = play_info.data[CONST.Y_DESC]
			touchdown = play_info.touchdown
			interception = play_info.interception
			first_down = play_info.first_down
			sack = play_info.sack
			play = Passing_Play(game_code, play_num, team_code, "NA", "NA", completion, yards, touchdown, interception, first_down, 0, sack)
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
	OutputArray.append("Sack")
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