# ================================================================
# ===== IMPORTS ==================================================
# ================================================================
import re
import CONST
from Passing_Play import *
from Passing_Play_Info import *
from Rushing_Play import *
from Rushing_Play_Info import *
from Team_Game_Stat import *


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
	passing_plays_print = []
	passing_plays_print.append(Passing_Play_Header())
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
			play_info.Turnover_Occurred(next_play)
			play_info.Completion(next_play)
			play_info.Touchdown_Occurred()
			if play_info.turnover == 1:
				play_info.Interception()
			play_info.First_Down(next_play)
			play_info.Sack_Occurred()
			if play_info.sack == 1:
				continue	# putting sacks into rushing
			play_info.Safety_Occurred(next_play)
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
			safety = play_info.safety
			team_1 = play_info.team_1
			team_2 = play_info.team_2
			play = Passing_Play(game_code, play_num, team_code, "NA", "NA", completion, yards, touchdown, interception, first_down, 0, sack, safety, team_1, team_2)
			passing_plays.append(play)
			passing_plays_print.append(play.Compile_Play())

	return (passing_plays, passing_plays_print)


# Uses season data to find and compile a list of rushing plays
def Get_Rushing_Plays(data):
	rushing_plays = []
	rushing_plays_print = []
	rushing_plays_print.append(Rushing_Play_Header())
	play_num = 0
	for i in range(1, len(data)):

		# Get previous play data
		if i > 1:
			prev_play = Rushing_Play_Info(data[i-1])
		else:
			prev_play = Rushing_Play_Info([0] * len(data[i]))

		# Get this play
		play_info = Rushing_Play_Info(data[i])

		# Get next play
		if i + 1 < len(data):
			next_play = Rushing_Play_Info(data[i+1])
		else:
			next_play = Rushing_Play_Info([0] * len(data[i]))
		
		# Ignore Lafayette game for now due to bug. *** REMOVE LATER ***
		if None != re.search("Lafayette", str(play_info.data[CONST.OFF]) + str(play_info.data[CONST.DEF])):
			continue

		# New game, reset play count
		if play_info.data[CONST.CODE] != prev_play.data[CONST.CODE]:
			play_num = 1
		else:
			play_num += 1
		play_info.play_num = play_num

		# Found a rushing play, parse the data to gather info
		if "Rush" == play_info.data[CONST.TYPE] or "Pass" == play_info.data[CONST.TYPE]:
			# Only include passing plays which are sacks
			play_info.Sack_Occurred()
			if "Pass" == play_info.data[CONST.TYPE] and play_info.sack == 0:
				continue
			play_info.Turnover_Occurred(next_play)
			play_info.Touchdown_Occurred()
			play_info.First_Down(next_play)
			play_info.Safety_Occurred(next_play)
			# Finalize all the data for the play
			game_code = play_info.data[CONST.CODE]
			play_num = play_info.play_num
			team_code = play_info.data[CONST.OFF]
			yards = play_info.data[CONST.Y_DESC]
			touchdown = play_info.touchdown
			first_down = play_info.first_down
			fumble = play_info.fumble
			fumble_lost = play_info.fumble_lost
			sack = play_info.sack
			safety = play_info.safety
			team_1 = play_info.team_1
			team_2 = play_info.team_2
			play = Rushing_Play(game_code, play_num, team_code, "NA", yards, touchdown, first_down, fumble, fumble_lost, sack, safety, team_1, team_2)
			rushing_plays.append(play)
			rushing_plays_print.append(play.Compile_Play())

	return (rushing_plays, rushing_plays_print)


#
def Get_Team_Game_Stats(passing_plays, rushing_plays):
	team_games_stats = []

	# Compile passing plays
	for i in range(0, len(passing_plays)):
		play = passing_plays[i]

		# Check if this game has been done
		same_game = False
		for game in team_games_stats:
			if play.Game_Code == game.Game_Code:
				same_game = True
		if same_game:
			continue

		# Initialize the new games
		new_game_1 = Team_Game_Stat(play.Game_Code, play.team_1)
		new_game_2 = Team_Game_Stat(play.Game_Code, play.team_2)

		# Add the passing plays to each team
		row = i
		while passing_plays[row].Game_Code == play.Game_Code:
			if passing_plays[row].Team_Code == new_game_1.Team_Code:
				new_game_1.Pass_Plays.append(passing_plays[row])
			elif passing_plays[row].Team_Code == new_game_2.Team_Code:
				new_game_2.Pass_Plays.append(passing_plays[row])
			else:
				print "WARNING: Team not found!"
				print new_game_1.Team_Code
				print new_game_2.Team_Code
				print passing_plays[row].Team_Code
				print "\n"
			row += 1
			if row >= len(passing_plays):
				break

		# Get totals and add them to the list
		new_game_1.Get_Passing_Totals()
		new_game_2.Get_Passing_Totals()
		team_games_stats.append(new_game_1)
		team_games_stats.append(new_game_2)

	# Compile rushing plays
	i = 0
	while i < len(team_games_stats):
		game = team_games_stats[i]

		# First find the correct game
		row = i
		while rushing_plays[row].Game_Code != game.Game_Code:
			row += 1

		# Add rushing plays to this game
		while rushing_plays[row].Game_Code == game.Game_Code:
			if rushing_plays[row].Team_Code == game.Team_Code:
				game.Rush_Plays.append(rushing_plays[row])
			row += 1
			if row >= len(rushing_plays):
				break
		game.Get_Rushing_Totals()
		i += 1

	return_games = []
	return_games.append(Team_Game_Stats_Header())
	for game in team_games_stats:
		return_games.append(game.Compile_Stats())
	return return_games


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
	OutputArray.append("Safety")
	return OutputArray


# Returns the header for a play type
def Rushing_Play_Header():
	OutputArray = []
	OutputArray.append("Game Code")
	OutputArray.append("Play Number")
	OutputArray.append("Team Code")
	OutputArray.append("Rusher Player Code")
	OutputArray.append("Attempt")
	OutputArray.append("Yards")
	OutputArray.append("Touchdown")
	OutputArray.append("1st Down")
	OutputArray.append("Fumble")
	OutputArray.append("Fumble Lost")
	OutputArray.append("Sack")
	OutputArray.append("Safety")
	return OutputArray


# Returns the header for a play type
def Team_Game_Stats_Header():
	OutputArray = []
	OutputArray.append("Team Code")
	OutputArray.append("Game Code")
	OutputArray.append("Rush Att")
	OutputArray.append("Rush Yard")
	OutputArray.append("Rush TD")
	OutputArray.append("Pass Att")
	OutputArray.append("Pass Comp")
	OutputArray.append("Pass Yard")
	OutputArray.append("Pass TD")
	OutputArray.append("Pass Int")
	OutputArray.append("Safety")
	OutputArray.append("Sack")
	OutputArray.append("Sack Yard")
	OutputArray.append("1st Down Rush")
	OutputArray.append("1st Down Pass")
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
(passing_plays, passing_plays_print) = Get_Passing_Plays(data)
Write_CSV(file_name, passing_plays_print)

# Compile rushing plays and write to file
file_name = "rush_new.csv"
(rushing_plays, rushing_plays_print) = Get_Rushing_Plays(data)
Write_CSV(file_name, rushing_plays_print)

# Compile game stats and write to file
file_name = "team-game-statistics_new.csv"
team_game_stats = Get_Team_Game_Stats(passing_plays, rushing_plays)
Write_CSV(file_name, team_game_stats)


# ====================================================================
# ===== END PARSING ==================================================
# ====================================================================
print "Done! Press ENTER to continue."
raw_input()