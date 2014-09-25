import re
import CONST
from Team_Game_Stat import *
from Play import *

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


# Compilies team-game-stats for games
def Get_Team_Game_Stats(data):
	games = []
	game_num = 0

	# First seperate data into seperate games
	i = 1
	while i < len(data):
		game = []
		game.append(data[i])
		i += 1
		play_num = 0
		while data[i][CONST.CODE] == game[play_num][CONST.CODE]:
			game.append(data[i])
			i += 1
			play_num += 1
			if i >= len(data):
				break
		games.append(game)
		game_num += 1

	# Now compile data for each game
	team_game_stats = []
	team_game_stats_print = []
	team_game_stats_print.append(Team_Game_Stats_Header())
	for i in range(0, len(games)):
		game_stats_1 = Team_Game_Stat(games[i][0][CONST.CODE], games[i][0][CONST.OFF])
		game_stats_2 = Team_Game_Stat(games[i][0][CONST.CODE], games[i][0][CONST.DEF])

		for j in range(0, len(games[i])):
			play = Play(games[i][j])

			# Get next play
			if j + 1 < len(games[i]):
				next_play = Play(games[i][j+1])
			else:
				next_play = Play([0] * len(games[i]))

			# Get rushing information
			play.Sack_Occurred()
			play.Fumble_Check(next_play)
			if "Rush" == play.data[CONST.TYPE] or ("Pass" == play.data[CONST.TYPE] and play.Sack == 1):
				play.Rush_Att = 1
				try:
					play.Rush_Yard = play.data[CONST.Y_DESC]
				except:
					play.Rush_Yard = play.data[CONST.Y_DESC]
				play.Rushing_Touchdown_Occurred()

			# Get passing information
			if "Pass" == play.data[CONST.TYPE] and not ("Pass" == play.data[CONST.TYPE] and play.Sack == 1):
				play.Pass_Att = 1
				play.Completion(next_play)
				play.Interception()
				play.Passing_Touchdown_Occurred()
				try:
					play.Pass_Yard = play.data[CONST.Y_DESC]
				except:
					play.Pass_Yard = play.data[CONST.Y_DESC]

			# Get kickoff information
			if "Kickoff" == play.data[CONST.TYPE]:
				play.Kickoff_Ret = 1
				play.Kickoff = 1
				if "Touchdown" == play.data[CONST.REST]:
					play.Kickoff_Ret_TD = 1
				if None != re.search("touchback", play.data[CONST.P_REST], re.IGNORECASE):
					play.Kickoff_Touchback = 1
					play.Kickoff_Ret = 0

			# Points information
			play.Points = play.data[CONST.O_PT]

			# Get punt information
			if "Punt" == play.data[CONST.TYPE]:
				play.Punt = 1
				play.Punt_Ret = 1
				if "Touchdown" == play.data[CONST.REST]:
					play.Punt_Ret_TD = 1
					if None != re.search("block", play.data[CONST.P_REST], re.IGNORECASE):
						play.Kick_Punt_Blocked = 1
				elif "Blocked" == play.data[CONST.REST]:
					play.Kick_Punt_Blocked = 1

			# Get field goal information
			if "Field.Goal" == play.data[CONST.TYPE]:
				play.Field_Goal_Att = 1
				if "Made.FG" == play.data[CONST.REST]:
					play.Field_Goal_Made = 1
				elif "Blocked" == play.data[CONST.REST]:
					play.Kick_Punt_Blocked = 1
				if "Touchdown" == play.data[CONST.REST]:
					if None != re.search("block", play.data[CONST.P_REST], re.IGNORECASE):
						play.Kick_Punt_Blocked = 1

			# Get XP information
			if "Extra.Point" == play.data[CONST.TYPE]:
				play.Off_XP_Kick_Att = 1
				if None != re.search("made", play.data[CONST.P_REST], re.IGNORECASE):
					play.Off_XP_Kick_Made = 1
				if "Blocked" == play.data[CONST.REST]:
					play.Kick_Punt_Blocked = 1

			# Get two point conversion information
			if "Two.Point.Attempt" == play.data[CONST.TYPE]:
				play.Off_2XP_Att = 1
				play.Def_2XP_Att = 1
				play.Two_Pt_Conv_Successful(next_play)

			# Check for a safety
			play.Safety_Occurred(next_play)

			# Get tackles for loss data
			if "Rush" == play.data[CONST.TYPE] or "Pass" == play.data[CONST.TYPE]:
				if None != re.search("loss", play.data[CONST.P_REST], re.IGNORECASE):
					play.Tackle_For_Loss = 1
					try:
						play.Tackle_For_Loss_Yard = play.data[CONST.Y_SPOT]
					except:
						play.Tackle_For_Loss_Yard = play.data[CONST.Y_DESC]

			# Get penalty information
			if "Penalty" == play.data[CONST.TYPE]:
				play.Penalty = 1
				try:
					play.Penalty_Yard = play.data[CONST.Y_SPOT]
				except:
					play.Penalty_Yard = play.data[CONST.Y_DESC]

			# Get first down information
			play.First_Down(next_play)
			if 3 == play.data[CONST.DOWN] and (play.Rush_Att == 1 or play.Pass_Att == 1):
				play.Third_Down_Att = 1
				if play.First_Down_Rush == 1 or play.First_Down_Pass == 1:
					play.Third_Down_Conv = 1
			elif 4 == play.data[CONST.DOWN] and (play.Rush_Att == 1 or play.Pass_Att == 1):
				play.Fourth_Down_Att = 1
				if play.First_Down_Rush == 1 or play.First_Down_Pass == 1:
					play.Fourth_Down_Conv = 1

			# Get time of possession information
			if play.data[CONST.CLK] < 900 and next_play.data[CONST.CLK] < 900:	# normal
				play.Time_Of_Possession = play.data[CONST.CLK] - next_play.data[CONST.CLK]
			elif next_play.data[CONST.CLK] == 900 and play.data[CONST.CODE] == next_play.data[CONST.CODE]:	# end of quarter
				play.Time_Of_Possession = play.data[CONST.CLK]
			elif play.data[CONST.CODE] != next_play.data[CONST.CODE]:	# end of game
				play.Time_Of_Possession = play.data[CONST.CLK]

			# Get red zone information
			if (play.Pass_TD == 1 or play.Rush_TD == 1) and play.data[CONST.SPOT] <= 20:
				play.Red_Zone_TD = 1
			elif play.Field_Goal_Made == 1 and play.data[CONST.SPOT] <= 20:
				play.Red_Zone_Field_Goal = 1

			# Add play stats to team-game-stats
			if int(game_stats_1.Team_Code) == int(play.data[CONST.OFF]):
				game_stats_1.Add_Off_Stats(play)
				game_stats_2.Add_Def_Stats(play)
			elif int(game_stats_2.Team_Code) == int(play.data[CONST.OFF]):
				game_stats_2.Add_Off_Stats(play)
				game_stats_1.Add_Def_Stats(play)

		# Add this game to the array
		team_game_stats.append(game_stats_1)
		team_game_stats.append(game_stats_2)
		team_game_stats_print.append(game_stats_1.Compile_Stats())
		team_game_stats_print.append(game_stats_2.Compile_Stats())

	return (team_game_stats, team_game_stats_print)


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
	OutputArray.append("Pass Conv") 
	OutputArray.append("Kickoff Ret") 
	OutputArray.append("Kickoff Ret Yard") 
	OutputArray.append("Kickoff Ret TD") 
	OutputArray.append("Punt Ret") 
	OutputArray.append("Punt Ret Yard") 
	OutputArray.append("Punt Ret TD") 
	OutputArray.append("Fum Ret") 
	OutputArray.append("Fum Ret Yard") 
	OutputArray.append("Fum Ret TD") 
	OutputArray.append("Int Ret") 
	OutputArray.append("Int Ret Yard") 
	OutputArray.append("Int Ret TD") 
	OutputArray.append("Misc Ret") 
	OutputArray.append("Misc Ret Yard") 
	OutputArray.append("Misc Ret TD") 
	OutputArray.append("Field Goal Att") 
	OutputArray.append("Field Goal Made") 
	OutputArray.append("Off XP Kick Att") 
	OutputArray.append("Off XP Kick Made") 
	OutputArray.append("Off 2XP Att") 
	OutputArray.append("Off 2XP Made") 
	OutputArray.append("Def 2XP Att") 
	OutputArray.append("Def 2XP Made") 
	OutputArray.append("Safety")
	OutputArray.append("Points") 
	OutputArray.append("Punt") 
	OutputArray.append("Punt Yard") 
	OutputArray.append("Kickoff") 
	OutputArray.append("Kickoff Yard") 
	OutputArray.append("Kickoff Touchback") 
	OutputArray.append("Kickoff Out-Of-Bounds") 
	OutputArray.append("Kickoff Onside") 
	OutputArray.append("Fumble") 
	OutputArray.append("Fumble Lost") 
	OutputArray.append("Tackle Solo") 
	OutputArray.append("Tackle Assist") 
	OutputArray.append("Tackle For Loss") 
	OutputArray.append("Tackle For Loss Yard") 
	OutputArray.append("Sack")
	OutputArray.append("Sack Yard")
	OutputArray.append("QB Hurry") 
	OutputArray.append("Fumble Forced") 
	OutputArray.append("Pass Broken Up") 
	OutputArray.append("Kick/Punt Blocked") 
	OutputArray.append("1st Down Rush")
	OutputArray.append("1st Down Pass")
	OutputArray.append("1st Down Penalty") 
	OutputArray.append("Time Of Possession") 
	OutputArray.append("Penalty") 
	OutputArray.append("Penalty Yard") 
	OutputArray.append("Third Down Att") 
	OutputArray.append("Third Down Conv") 
	OutputArray.append("Fourth Down Att") 
	OutputArray.append("Fourth Down Conv") 
	OutputArray.append("Red Zone Att") 
	OutputArray.append("Red Zone TD") 
	OutputArray.append("Red Zone Field Goal") 
	return OutputArray


# ======================================================================
# ===== MAIN FUNCTION ==================================================
# ======================================================================
print "\n"

# Get team data
(team_names, team_codes, team_confs) = Read_Team_Data()

# Read data and replace team names with team codes
week = "Week 2"
file_name = "../" + week + "/play-by-play.csv"
data = Read_CSV(file_name)
data = Replace_Team_Names(data, team_names, team_codes)
Write_CSV("../" + week + "/play-by-play_team-nums.csv", data)

# Compile game data using the play-by-play data
(team_game_stats, team_games_stats_print) = Get_Team_Game_Stats(data)
Write_CSV("../" + week + "/team-game-stats.csv", team_games_stats_print)


# ====================================================================
# ===== END PARSING ==================================================
# ====================================================================
print "Done! Press ENTER to continue."
raw_input()