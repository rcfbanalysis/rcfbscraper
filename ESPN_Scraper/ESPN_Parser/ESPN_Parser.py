# ==================================================================
# ===== IMPORTS ====================================================
# ==================================================================
import re
import csv
from os import listdir
from os.path import isdir, isfile, join

from Game import *
from Drive import *
from Play_Stats import *
from Team_Game_Statistics import *


# ==================================================================
# ===== FUNCTIONS ==================================================
# ==================================================================


# ==================================================================
# DEVELOPMENTAL FUNCTIONS
# ==================================================================

# Checks if string is number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Converts pbp date from ESPN to my format
def Convert_PBP_Data(pbp_file):

	# Read in play-by-play data
	print "\nReading raw play-by-play data..."
	pbp_data = Read_CSV(pbp_file)
	print "Done"

	# Read in team and abbreviation data
	team_arr = Read_CSV("../2014 Stats/team.csv")
	team_arr = team_arr[1:]
	try:
		abbv_arr = Read_CSV("../2014 Stats/abbrevations.csv")
	except:
		print "WARNING: abbrevations.csv not found\n"
		abbv_arr = []

	# Find and replace team names
	teams = []
	(team1_code, team1_name, team2_code, team2_name, abbv_arr) = Define_Team_Names(pbp_data, team_arr, abbv_arr)
	pbp_data = Replace_All_Names(pbp_data, team1_name, "t" + team1_code)
	pbp_data = Replace_All_Names(pbp_data, team2_name, "t" + team2_code)
	teams.append([team1_code, team1_name])
	teams.append([team2_code, team2_name])

	# Find and replace home/visitor score abbreviations
	#for play in pbp_data:
	#	if len(play) > 3 and play[2] != "" and not is_number(play[2]):
	#		(visitor_code, visitor_name, abbv_arr) = New_Find_Abbv_Team(play[2], teams, abbv_arr)
	#		(home_code, home_name, abbv_arr) = New_Find_Abbv_Team(play[3], teams, abbv_arr)
	#		break
	visitor_code = team1_code
	visitor_name = team1_name
	home_code = team2_code
	home_name = team2_name
	for play in pbp_data:
		if len(play) > 3 and play[2] != "" and not is_number(play[2]):
			pbp_data = Replace_All_Names(pbp_data, play[2], "t" + visitor_code)
			pbp_data = Replace_All_Names(pbp_data, play[3], "t" + home_code)

	# Find and replace home/visitor spot abbreviations
	for play in pbp_data:
		m = re.match(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?P<team>\D+) (?P<pos>\d+))", play[0])
		if m:
			(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("team"), teams, abbv_arr)
			pbp_data = Replace_All_Names(pbp_data, str(m.group("team")), "t" + code)

	# Find and replace field position abbreviations
	for play in pbp_data:
		if len(play) > 1:
			m = re.search(r"to the (?P<team>\D+) \d{1,2}", play[1])
			if m:
				(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("team"), teams, abbv_arr)
				pbp_data = Replace_All_Names(pbp_data, str(m.group("team")), "t" + code)

	return pbp_data


# Locates the names of the two teams in this game (uses team name in drive switching)
def Define_Team_Names(pbp_data, team_arr, abbv_arr):
	
	# Find the two teams
	team1_code = pbp_data[0][2]
	team2_code = pbp_data[0][3]
	team1_name = ""
	team2_name = ""
	for team in team_arr:
		if int(team[0]) == int(team1_code):
			team1_name = team[1]
		if int(team[0]) == int(team2_code):
			team2_name = team[1]
	if team1_name != "" and team2_name != "":
		return (team1_code, team1_name, team2_code, team2_name, abbv_arr)
	else:
		print pbp_data[0]

	for play in pbp_data:
		m = re.match(r"(?P<offense>\D+) at \d+\:\d+", play[0])
		if m:
			(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("offense"), team_arr, abbv_arr)
			if team1_code == 0:
				team1_code = code
				team1_name = name
			elif team2_code == 0:
				team2_code = code
				team2_name = name
		if team1_code != 0 and team2_code != 0:
			return (team1_code, team1_name, team2_code, team2_name, abbv_arr)


# Locates correct teams for a given abbreviation
def Define_Team_Abbreviation(data, abbv, team_arr, abbv_arr):

	# Look through all abbreviations for a match
	try:
		for i in range(0, len(abbv_arr)):
			if abbv == abbv_arr[i][0]:
				team_num = abbv_arr[i][1]
				team_name = abbv_arr[i][2]
				return (team_num, team_name, abbv_arr)
	except:
		pass

	# If only 2 teams are on the team array, look for the abbreviation under their names
	if len(team_arr) == 2:
		team_abbv_exist = [False] * 2
		for i in range(0, len(team_arr)):
			team = team_arr[i]					# look for this team in the abbreviation array
			for team_abbv in abbv_arr:
				if team[0] == team_abbv[1]:		# this team has available abbreviations
					for j in range(3, len(team_abbv)):
						if team_abbv[j] == abbv:
							team_abbv_exist[i] = True
		# If this abbreviation was filed under one team, return it
		if team_abbv_exist[0] and not team_abbv_exist[1]:
			return (team_arr[0][0], team_arr[0][1], abbv_arr)		# returns (code, name, abbv_arr)
		elif not team_abbv_exist[0] and team_abbv_exist[1]:
			return (team_arr[1][0], team_arr[1][1], abbv_arr)		# returns (code, name, abbv_arr)

	# Rank each team
	team_sort = []
	for i in range(0, len(team_arr)):
		team_sort_tmp = [0] * 3
		team_sort_tmp[1] = team_arr[i][0]
		team_sort_tmp[2] = team_arr[i][1]
		abbv_ltrs = list(abbv)
		team_ltrs = list(team_arr[i][1])
		pos = 0
		tot = 0

		# Find the correlation in naming
		for j in range(0, len(abbv_ltrs)):
			ltr = abbv_ltrs[j]
			if ltr == "U" or None == re.search(r"[a-zA-Z]", ltr):
				continue
			inc = 0
			while None == re.search(ltr, team_ltrs[pos], re.IGNORECASE):
				inc += 1
				pos += 1
				if pos >= len(team_ltrs):
					break
			if pos >= len(team_ltrs):
				tot = 1000
				break
			else:
				tot += inc
		team_sort_tmp[0] = tot
		team_sort.append(team_sort_tmp)
	team_sort = sorted(team_sort, key=lambda arr: arr[0])

	# Check the sorted teams for the correct match
	i = 0
	while i < len(team_sort):
		print "\nGuess: " + str(abbv) + " = " + str(team_sort[i][2])
		if len(team_arr) == 2:
			print str(team_arr[0][1]) + " vs " + str(team_arr[1][1])
		user_in = raw_input("Enter 0 for incorrect match, 1 for correct match, or 2 for unknown: ")
		if user_in == "":		# blank
			print "Please enter 1 or 0"
			continue
		elif user_in == "1":	# correct
			break
		elif user_in == "2":	# not sure
			print "The next option is " + str(team_sort[i + 1][2])
			continue
		elif user_in == "0":	# no match
			i += 1
		else:
			for name in team_arr:	# team name entered
				if user_in == name[1]:
					if abbv_arr != 0:
						abbv_arr.append([abbv, name[0], name[1]])
						Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
					return (name[0], name[1], abbv_arr)
			print user_in + " not found in team array."
		if i == len(team_sort):
			i = 0
	team_code = team_sort[i][1]
	team_name = team_sort[i][2]

	# Check if this team already has an abbreviation set
	for j in range(0, len(abbv_arr)):
		if abbv_arr[j][1] == team_code:
			abbv_arr[j].append(abbv)
			Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
			return (team_code, team_name, abbv_arr)		# returns (code, name, abbv_arr)

	# Save abbreviation array and return team
	if abbv_arr != 0:
		abbv_arr.append([abbv, team_code, team_name])
		Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
	return (team_code, team_name, abbv_arr)		# returns (code, name, abbv_arr)


# Changes an abbreviated team name to its team number
def New_Find_Abbv_Team(abbv, team_arr, abbv_arr):
	# Check if it is already matched
	if abbv_arr != 0:
		for team in abbv_arr:
			if abbv == team[0]:
				return (team[1], team[2], abbv_arr)
	team_sort = []
	for i in range(0, len(team_arr)):
		team_sort_tmp = [0] * 3					# naming correlation
		team_sort_tmp[1] = team_arr[i][0]		# team number
		team_sort_tmp[2] = team_arr[i][1]		# team name
		abbv_ltrs = list(abbv)
		team_ltrs = list(team_arr[i][1])
		pos = 0
		tot = 0
		# Find the correlation in naming
		for j in range(0, len(abbv_ltrs)):
			ltr = abbv_ltrs[j]
			if ltr == "U" or None == re.search(r"[a-zA-Z]", ltr):
				continue
			inc = 0
			while None == re.search(ltr, team_ltrs[pos], re.IGNORECASE):
				inc += 1
				pos += 1
				if pos >= len(team_ltrs):
					break
			if pos >= len(team_ltrs):
				tot = 1000
				break
			else:
				tot += inc
		team_sort_tmp[0] = tot
		team_sort.append(team_sort_tmp)
	team_sort = sorted(team_sort, key=lambda arr: arr[0])
	# Check the sorted teams for the correct match
	i = 0
	while i < len(team_sort):
		if str(abbv) == str(team_sort[i][2]):
			break
		print "\nGuess: " + str(abbv) + " = " + str(team_sort[i][2])
		user_in = raw_input("Enter 0 for incorrect match, 1 for correct match, or 2 for unknown: ")
		for name in team_arr:
			if user_in == name[1]:
				if abbv_arr != 0:
					abbv_arr.append([abbv, name[0], name[1]])
					Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
				return (name[0], name[1], abbv_arr)
		if user_in == "":
			print "Please enter 1 or 0"
			continue
		if user_in == "":
			break
		if user_in == "1":
			break
		if user_in == "2":
			print "The next option is " + str(team_sort[i + 1][2])
			continue
		i += 1
		if i == len(team_sort):
			i = 0
	if abbv_arr != 0:
		abbv_arr.append([abbv, team_sort[i][1], team_sort[i][2]])
		Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)


# Replaces all occurrances of a string with another
def Replace_All_Names(pbp_data, name, number):
	k = re.compile(r"\b%s\b" % name, re.I)						# replaces whole word abbreviations
	for i in range(0, len(pbp_data)):
		for j in range(0, len(pbp_data[i])):
			pbp_data[i][j] = k.sub(number, pbp_data[i][j])
	k = re.compile(r"\b%s(?P<spot>\d{1,2})\b" % name, re.I)		# replaces spot abbreviations (ex: BAYLOR49)
	for i in range(0, len(pbp_data)):
		for j in range(0, len(pbp_data[i])):
			m = k.search(pbp_data[i][j])
			if m:
				pbp_data[i][j] = k.sub(number + " " + str(m.group("spot")), pbp_data[i][j])
	return pbp_data


# Puts all play-by-play data into drives
def Compile_Drives(pbp_data, game):
	drives = []
	cur_drive = Drive(0, 0, 0, 0, 0, 0)
	cur_drive.Finished = 1
	for play in pbp_data:
		game.Set_Quarter(play)
		start = re.match(r"t(?P<offense>\d+) at (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		stop = re.match(r"t(?P<team>\d+) DRIVE TOTALS\: (?P<plays>\d+) play(?:s)?\, (?:\-)?(?P<yards>\d+) (?:yards|yard|yds|yd)\, (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		if start:	# Check for the start of a new drive
			if int(start.group("offense")) == game.Home:
				offense = game.Home
				defense = game.Visitor
			elif int(start.group("offense")) == game.Visitor:
				offense = game.Visitor
				defense = game.Home
			else:
				print int(start.group("offense"))
				print game.Home
				print game.Visitor
			start_time = Set_Clock(start.group("min"), start.group("sec"))
			if cur_drive.Finished != 1 and cur_drive.Game_Code != 0:
				print "WARNING: Drive summary never produced"
				drives.append(cur_drive)
			cur_drive = Drive(game.Code, offense, defense, start_time, game.Current_Qrt, len(drives) + 1)
		elif stop:	# Check for the end of a drive
			plays = int(stop.group("plays"))
			yards = int(stop.group("yards"))
			stop_time = Set_Clock(stop.group("min"), stop.group("sec"))
			cur_drive.Set_Summary(plays, yards, stop_time, game.Current_Qrt)
			if cur_drive.Game_Code != 0:
				drives.append(cur_drive)
		else:		# Add play to drives
			cur_drive.Raw_Pbp_Data.append(play)
	return drives


# ==================================================================
# ==================================================================


# Returns the contents of a .csv file in an array
def Read_CSV(file_name):
	data = []
	with open(file_name, "r") as csvfile:
		data_reader = csv.reader(csvfile)
		for row in data_reader:
			data.append(row)
	for i in range(0, len(data)):
		for j in range(0, len(data[i])):
			data[i][j] = re.sub("\"", "", data[i][j])
	return data


# Writes the contents of data to a .csv file
def Write_CSV(data, file_name):
	with open(file_name, "w") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)


# Changes an abbreviated team name to its team number
def Find_Abbv_Team(data, abbv, team_arr, abbv_arr, approved_abbv):
	for i in range(0, len(abbv_arr)):
		if abbv == abbv_arr[i][0]:
			approved = False
			for abbv_app in approved_abbv:
				if abbv_app == abbv:
					approved = True
			if len(abbv) > 4 or approved:
				team_num = abbv_arr[i][1]
				team_name = abbv_arr[i][2]
				return (team_num, team_name, abbv_arr)
			print "\nGuess: " + str(abbv) + " = " + str(abbv_arr[i][2])
			user_in = raw_input("Enter 0 for incorrect match or 2 for unknown: ")
			if user_in == "2":
				dataline = 0
				while None == re.match(r"(?P<team>.+) at \d{0,2}\:\d{2}", data[dataline][0]):
					dataline += 1
				while user_in == "2":
					print data[dataline][0]
					user_in = raw_input("Enter 0 for incorrect match or 2 for unknown: ")
					dataline += 1
					while None == re.match(r"(?P<team>.+) at \d{0,2}\:\d{2}", data[dataline][0]):
						dataline += 1
			if user_in != 0:
				approved_abbv.append(abbv)
				team_num = abbv_arr[i][1]
				team_name = abbv_arr[i][2]
				return (team_num, team_name, abbv_arr)

	team_sort = []
	for i in range(0, len(team_arr)):
		team_sort_tmp = [0] * 3
		team_sort_tmp[1] = team_arr[i][0]
		team_sort_tmp[2] = team_arr[i][1]
		abbv_ltrs = list(abbv)
		team_ltrs = list(team_arr[i][1])
		pos = 0
		tot = 0
		for j in range(0, len(abbv_ltrs)):
			ltr = abbv_ltrs[j]
			if ltr == "U" or None == re.search(r"[a-zA-Z]", ltr):
				continue
			inc = 0
			while None == re.search(ltr, team_ltrs[pos], re.IGNORECASE):
				inc += 1
				pos += 1
				if pos >= len(team_ltrs):
					break
			if pos >= len(team_ltrs):
				tot = 1000
				break
			else:
				tot += inc
		team_sort_tmp[0] = tot
		team_sort.append(team_sort_tmp)
	team_sort = sorted(team_sort, key=lambda arr: arr[0])
	i = 0
	dataline = 3
	while None == re.match(r"(?P<team>.+) at \d{0,2}\:\d{2}", data[dataline][0]):
		dataline += 1
	while i < len(team_sort):
		print "\nGuess: " + str(abbv) + " = " + str(team_sort[i][2])
		user_in = raw_input("Enter 1 for correct match or 2 for unknown: ")
		if user_in == "":
			print "Please enter 1 or 0"
			continue
		if user_in == "":
			break
		while user_in == "2":
			print data[dataline][0]
			user_in = raw_input("Enter 1 for correct match or 2 for unknown: ")
			dataline += 1
			while None == re.match(r"(?P<team>.+) at \d{0,2}\:\d{2}", data[dataline][0]):
				dataline += 1
		if user_in == "1":
			break
		i += 1
	abbv_arr.append([abbv, team_sort[i][1], team_sort[i][2]])
	Write_CSV(abbv_arr, "../2014 Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)


# Finds the two teams in this game
def Find_Teams(data, abbv_arr):
	# Fin the two teams
	team1 = 0
	team2 = 0
	team1_name = 0
	team2_name = 0
	for play in data:
		m = re.match(r"(?P<offense>\D+) at \d+\:\d+", play[0])
		if m:
			(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("offense"), team_arr, abbv_arr, approved_abbv)
			if team1 == 0:
				team1 = number
				team1_name = name
			elif team2 == 0:
				team2 = number
				team2_name = name
		if team1 > 0 and team2 > 0:
			break
	# Which is home/visitor?
	home_team = 0
	visitor_team = 0
	for play in data:
		if play[2] != "":
			(number1, name1, abbv_arr) = Find_Abbv_Team(data, play[2], team_arr, abbv_arr, approved_abbv)
			(number2, name2, abbv_arr) = Find_Abbv_Team(data, play[3], team_arr, abbv_arr, approved_abbv)
			if number1 == team1:
				return (team1, team1_name, team2, team2_name)	# return (visitor, home)
			else:
				return (team2, team2_name, team1, team1_name)	# return (visitor, home)


# Parses all plays for data
def Parse_Plays(game_num, data, team_arr, abbv_arr, visitor, home, approved_abbv):
	# current data
	quarter = 0
	play_num = 0
	offense = 0
	defense = 0
	home_score = 0
	visitor_score = 0
	red_zone = 0
	# penalties
	home_penalties = []
	visitor_penalties = []
	home_penalties_print = []
	visitor_penalties_print = []
	# rushing plays
	home_rushing_plays = []
	visitor_rushing_plays = []
	home_rushing_plays_print = []
	visitor_rushing_plays_print = []
	# passing plays
	home_passing_plays = []
	visitor_passing_plays = []
	home_passing_plays_print = []
	visitor_passing_plays_print = []
	# team-game-stats
	home_team_game_stats = Team_Game_Stat(game_num, home)
	visitor_team_game_stats = Team_Game_Stat(game_num, visitor)

	# Read play by play data
	for play in data:
		quarter = Set_Quarter(play)		# check for new quarter
		play_desc = play[1]

		# =============================================================================================================
		# Check for start of a new drive
		# =============================================================================================================
		m = re.match(r"(?P<offense>\D+) at (?P<time>\d{0,2}\:\d{0,2})", play[0])
		if m:
			(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("offense"), team_arr, abbv_arr, approved_abbv)
			if offense == number and m.group("time") != "15:00":
				print "\nWARNING: This drive may not have switched"
				print play[0]
			offense = number
			defense = visitor if offense == home else home
			red_zone = 0

		# =============================================================================================================
		# Check for red zone attempt
		# =============================================================================================================
		(down, dist, f_half, pos) = Get_Play_Info(play[0], offense)
		if down > -1:
			if pos != 50:
				(number, name, abbv_arr) = Find_Abbv_Team(data, f_half, team_arr, abbv_arr, approved_abbv)
				pos = Get_Field_Pos(number, offense, pos)
			if down > -1 and pos <= 20 and red_zone == 0:
				red_zone = 1
				if home == offense:
					home_team_game_stats.Red_Zone_Att += 1
				elif visitor == offense:
					visitor_team_game_stats.Red_Zone_Att += 1

		# =============================================================================================================
		# Check for drive summary
		# =============================================================================================================
		m = re.match(r"((?P<team>\D+) DRIVE TOTALS\: (?P<plays>\d+) play(?:s)?\, (?P<yards>\d+) (?:yards|yard|yds|yd)\, (?P<min>\d{1,2})\:(?P<sec>\d{2}))", play[0])
		if m:
			(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
			if home == number:
				home_team_game_stats.Time_Of_Possession += Set_Clock(m.group("min"), m.group("sec"))
			elif visitor == number:
				visitor_team_game_stats.Time_Of_Possession += Set_Clock(m.group("min"), m.group("sec"))

		# =============================================================================================================
		# Check for coin toss
		# =============================================================================================================
		m = re.match(r"((?P<team>\D+) (?:wins|won).*toss.*)", play_desc)
		if m:
			#print m.group("team") + " wins toss.\n"
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)

		# =============================================================================================================
		# Check for end of quarter
		# =============================================================================================================
		m = re.match(r"(End of (?P<Qrt>\d)(?:st|nd|rd|th) Quarter)", play_desc)
		if m:
			quarter_end = int(m.group("Qrt"))
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)

		# =============================================================================================================
		# Check for timeout
		# =============================================================================================================
		m = re.match(r"(Timeout (?P<team>\D+), clock (?P<time>\d{2}\:\d{2}))", play_desc)
		if m:
			team_timeout = m.group("team")
			timeout_time = m.group("time")
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)

		# =============================================================================================================
		# Check for no play
		# =============================================================================================================
		m = re.search(r"(NO PLAY\s*\W*\s*)", play_desc)
		if m:
			# remove everything before penalty
			m = re.match(r"(?P<remove>.+)PENALTY", play_desc, re.IGNORECASE)
			play_desc = re.sub(re.escape(m.group("remove")), "", play_desc)

		# =============================================================================================================
		# Check for kickoff
		# =============================================================================================================
		m = re.match("((?P<kicker>\D+) kickoff\s+)", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get kicker
			kicker = m.group("kicker")
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# get yardage
			m = re.match(r"(for (?P<yards>\d+) (?:yards|yard|yds|yd)\s*\W*\s*)", play_desc)
			if m:
				yards = int(m.group("yards"))
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				yards = "NA"
			# get returner
			m = re.match(r"((?P<returner>\D+) return\s*)", play_desc)
			if m:
				returner = m.group("returner")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				returner = ""
			# get return yards
			returned = 0
			m = re.match(r"(for (?P<yards>\d+) (?:yards|yard|yds|yd)\s*\W*\s*)", play_desc)
			if m:
				returned = 1
				ret_yards = int(m.group("yards"))
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				ret_yards = 0
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for touchback
			m = re.match(r"(for a touchback)", play_desc)
			if m:
				touchback = 1
				field_pos = 25
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				touchback = 0
			# check for out of bounds
			m = re.match(r"(out\-of\-bounds)", play_desc)
			if m:
				out_of_bounds = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				out_of_bounds = 0
			# check for fumble
			m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
			if m:
				fumble = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble = 0
			# chech for fumble lost
			m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
			if m and fumble == 1:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
				if number != offense:
					fumble_lost = 1
				else:
					fumble_lost = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble_lost = 0
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			if td:	# check extra point
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)
			else:
				extra_point = 0

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Kickoff_Stats(ret_yards, td, fumble, fumble_lost, extra_point, returned)
				visitor_team_game_stats.Add_Def_Kickoff_Stats(yards, touchback, out_of_bounds, td, fumble, fumble_lost, extra_point)
			else:
				visitor_team_game_stats.Add_Off_Kickoff_Stats(ret_yards, td, fumble, fumble_lost, extra_point, returned)
				home_team_game_stats.Add_Def_Kickoff_Stats(yards, touchback, out_of_bounds, td, fumble, fumble_lost, extra_point)

		# =============================================================================================================
		# Check for punt
		# =============================================================================================================
		m = re.match("((?P<punter>\D+) punt\s+)", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get kicker
			punter = m.group("punter")
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# get yardage
			m = re.match(r"(for (?P<yards>\d+) (?:yards|yard|yds|yd)\s*\W*\s*)", play_desc)
			if m:
				yards = int(m.group("yards"))
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				yards = 0
			# get returner
			returner = ""
			m = re.match(r"((?P<returner>\D+) returns\s*)", play_desc)
			if m:
				returner = m.group("returner")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# fair catch
			m = re.match(r"(fair catch by (?P<returner>\D+) at the\s*)", play_desc)
			if m:
				returner = m.group("returner")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				m = re.match(r"((?P<field_half>\D+) (?:(?P<yard_line>\d+))|((?P<fifty>50)\D*))", play_desc)
				if m:
					if m.group("field_half"):
						(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
						if number == offense:
							field_pos = int(m.group("yard_line"))
						else:
							field_pos = 100 - int(m.group("yard_line"))
					elif m.group("fifty"):
						field_pos = 50
					play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for loss of yards
			m = re.match(r"(for a (?P<loss>loss) of\W+)", play_desc)
			if m:
				loss = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				loss = 0
			# get return yards
			returned = 0
			m = re.match(r"((?:for)?\s*((?P<yards>\d+) (?:(?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain))\W*)", play_desc)
			if m:
				returned = 1
				if m.group("yards"):
					ret_yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					ret_yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				ret_yards = 0
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+),?\s*)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for touchback
			m = re.match(r"(for a touchback)", play_desc)
			if m:
				field_pos = 25
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for downed punt
			m = re.match(r"(downed at the)", play_desc)
			if m:
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				m = re.match(r"((?P<field_half>\D+) (?:(?P<yard_line>\d+))|((?P<fifty>50) (?:yard|yd) line\s*))", play_desc)
				if m:
					if m.group("field_half"):
						(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
						if number == offense:
							field_pos = int(m.group("yard_line"))
						else:
							field_pos = 100 - int(m.group("yard_line"))
					elif m.group("fifty"):
						field_pos = 50
					play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for out of bounds
			m = re.match(r"(punt out\-of\-bounds at the (?:(?P<field_half>\D+) (?P<yard_line>\d+)|(?P<fifty>50))\s*(?:(?:yard|yd) line)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for fumble
			m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
			if m:
				fumble = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble = 0
			# chech for fumble lost
			m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
			if m and fumble == 1:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
				if number != offense:
					fumble_lost = 1
				else:
					fumble_lost = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble_lost = 0
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			if td:	# check extra point
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Def_Punt_Stats(yards, td, fumble, fumble_lost, extra_point)
				visitor_team_game_stats.Add_Off_Punt_Stats(ret_yards, td, fumble, fumble_lost, extra_point, returned)
			else:
				visitor_team_game_stats.Add_Def_Punt_Stats(yards, td, fumble, fumble_lost, extra_point)
				home_team_game_stats.Add_Off_Punt_Stats(ret_yards, td, fumble, fumble_lost, extra_point, returned)

		# =============================================================================================================
		# Check for punt (alt)
		# =============================================================================================================
		m = re.match(r"((?P<receiver>\D+) (?P<ret_yards>\d+) (?:yard|yd) Punt Return \((?P<punter>\D+) Kick\))", play_desc, re.IGNORECASE)
		if m:
			# inc play number
			play_num += 1
			# get info
			receiver = m.group("receiver")
			ret_yards = int(m.group("ret_yards"))
			punter = m.group("punter")
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Def_Punt_Stats("NA", 0, 0, 0, 0)
				visitor_team_game_stats.Add_Off_Punt_Stats(ret_yards, 0, 0, 0, 0, 1)
			else:
				visitor_team_game_stats.Add_Def_Punt_Stats("NA", 0, 0, 0, 0)
				home_team_game_stats.Add_Off_Punt_Stats(ret_yards, 0, 0, 0, 0, 1)

		# =============================================================================================================
		# Check for field goal
		# =============================================================================================================
		m = re.match(r"((?P<kicker>\D+) (?:(?P<yardage>\d+) (?:yard|yd)) FG (?P<make>BLOCKED|MISSED|GOOD)\s*)", play_desc, re.IGNORECASE)
		if m:
			kicker = m.group("kicker")
			distance = int(m.group("yardage"))
			result = m.group("make")
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			if result == "BLOCKED":
				print "BLOCKED"

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Field_Goal_Off_Stats(kicker, distance, result, red_zone)
			elif offense == visitor:
				visitor_team_game_stats.Add_Field_Goal_Off_Stats(kicker, distance, result, red_zone)

		m = re.match(r"((?P<kicker>\D+) (?:(?P<yardage>\d+) (?:yard|yd)) Field Goal)", play_desc, re.IGNORECASE)
		if m:
			kicker = m.group("kicker")
			distance = int(m.group("yardage"))
			result = "GOOD"
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			if result == "BLOCKED":
				print "BLOCKED"

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Field_Goal_Off_Stats(kicker, distance, result, red_zone)
			elif offense == visitor:
				visitor_team_game_stats.Add_Field_Goal_Off_Stats(kicker, distance, result, red_zone)

		# =============================================================================================================
		# Check for a run play
		# =============================================================================================================
		m = re.match(r"((?P<rusher>\D+) (?:run|rush) for\W+)", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get rusher
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			rusher = m.group("rusher")
			# init rushing class
			rush_play = Rushing_Play(0, play_num, offense, rusher)
			# check for loss of yards
			m = re.match(r"(a (?P<loss>loss) of\W+)", play_desc)
			if m:
				loss = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				loss = 0
			# get yards gained
			m = re.match(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)", play_desc)
			if m:
				if m.group("yards"):
					yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			rush_play.Yards = yards
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for first down
			m = re.match(r"(for a (?P<fd>1ST down))", play_desc, re.IGNORECASE)
			if m:
				fd = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fd = 0
			rush_play.First_down = fd
			# check for safety
			m = re.match(r"(for a (?P<safety>SAFETY)\s+)", play_desc)
			if m:
				safety = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				safety = 0
			rush_play.Safety = safety
			# check for fumble
			m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
			if m:
				fumble = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble = 0
			rush_play.Fumble = fumble
			# chech for fumble lost
			m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
			if m and fumble == 1:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
				if number != offense:
					fl = 1
				else:
					fl = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				rush_play.Fumble_Lost = fl
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			rush_play.Touchdown = td
			if td:	# check extra point
				if rush_play.Yards > dist:	# check for would be first down
					rush_play.First_down = 1
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)
			else:
				extra_point = 0

			if offense == home:
				home_rushing_plays.append(rush_play)
				home_rushing_plays_print.append(rush_play.Compile_Play())
				#print home_rushing_plays[len(home_rushing_plays) - 1].Compile_Play()
			else:
				visitor_rushing_plays.append(rush_play)
				visitor_rushing_plays_print.append(rush_play.Compile_Play())
				#print visitor_rushing_plays[len(visitor_rushing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				visitor_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)
			elif offense == visitor:
				visitor_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				home_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)

		# =============================================================================================================
		# Check for a run play
		# =============================================================================================================
		m = re.match(r"((?P<rusher>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:run|rush)\s*)", play_desc, re.IGNORECASE)
		if m:
			# inc play number
			play_num += 1
			# get rusher
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			rusher = m.group("rusher")
			# init rushing class
			rush_play = Rushing_Play(0, play_num, offense, rusher)
			# get yards gained
			rush_play.Yards = int(m.group("yards"))
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			rush_play.Touchdown = td
			if td:	# check extra point
				if rush_play.Yards > dist:	# check for would be first down
					rush_play.First_down = 1
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)
			else:
				extra_point = 0

			if offense == home:
				home_rushing_plays.append(rush_play)
				home_rushing_plays_print.append(rush_play.Compile_Play())
				#print home_rushing_plays[len(home_rushing_plays) - 1].Compile_Play()
			else:
				visitor_rushing_plays.append(rush_play)
				visitor_rushing_plays_print.append(rush_play.Compile_Play())
				#print visitor_rushing_plays[len(visitor_rushing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				visitor_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)
			elif offense == visitor:
				visitor_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				home_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)

		# =============================================================================================================
		# check for a pass play
		# =============================================================================================================
		m = re.match(r"((?P<passer>\D+) pass (?P<completion>incomplete|complete)\W*)", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get passer
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			passer = m.group("passer")
			# init passing class
			completion = 1 if m.group("completion") == "complete" else 0
			pass_play = Passing_Play(0, play_num, offense, passer, completion)
			# get receiver (at end of string)
			m = re.match(r"(to (?P<receiver>\D+)\Z)", play_desc)
			if m:
				pass_play.Receiver = m.group("receiver")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# get receiver (with yards gained)
			m = re.match(r"(to (?P<receiver>\D+) for\W+)", play_desc)
			if m:
				pass_play.Receiver = m.group("receiver")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for loss of yards
			m = re.match(r"(a (?P<loss>loss) of\W+)", play_desc)
			if m:
				loss = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				loss = 0
			# get yards gained
			yards = 0
			m = re.match(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)", play_desc)
			if m:
				if m.group("yards"):
					yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			pass_play.Yards = yards
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for first down
			m = re.search(r"(for a (?P<fd>1ST down)\s*)", play_desc, re.IGNORECASE)
			if m:
				fd = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fd = 0
			pass_play.First_down = fd
			# check for safety
			m = re.match(r"(for a (?P<safety>SAFETY)\s*)", play_desc)
			if m:
				safety = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				safety = 0
			pass_play.Safety = safety
			# check for fumble
			m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
			if m:
				fumble = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble = 0
			pass_play.Fumble = fumble
			# chech for fumble lost
			m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
			if m and fumble == 1:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
				if number != offense:
					fl = 1
				else:
					fl = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				pass_play.Fumble_Lost = fl
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			pass_play.Touchdown = td
			if td:	# check extra point
				if pass_play.Yards > dist:	# check for would be first down
					pass_play.First_down = 1
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)
			else:
				extra_point = 0

			if offense == home:
				home_passing_plays.append(pass_play)
				home_passing_plays_print.append(pass_play.Compile_Play())
				#print home_passing_plays[len(home_passing_plays) - 1].Compile_Play()
			else:
				visitor_passing_plays.append(pass_play)
				visitor_passing_plays_print.append(pass_play.Compile_Play())
				#print visitor_passing_plays[len(visitor_passing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Pass_Stats(pass_play, extra_point, play[0], red_zone)
				visitor_team_game_stats.Add_Def_Pass_Stats(pass_play, td, extra_point)
			elif offense == visitor:
				visitor_team_game_stats.Add_Off_Pass_Stats(pass_play, extra_point, play[0], red_zone)
				home_team_game_stats.Add_Def_Pass_Stats(pass_play, td, extra_point)

		# =============================================================================================================
		# Check for pass play interception
		# =============================================================================================================
		m = re.match(r"((?P<passer>\D+) pass intercepted\W*)", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get passer
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			passer = m.group("passer")
			# init passing class
			pass_play = Passing_Play(0, play_num, offense, passer, 0)
			pass_play.Interception = 1
			# get interceptor
			m = re.match(r"((?P<interceptor>\D+) return )", play_desc)
			if m:
				interceptor = m.group("interceptor")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for loss of yards
			m = re.match(r"(a (?P<loss>loss) of\W+)", play_desc)
			if m:
				loss = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				loss = 0
			# get yards gained
			yards = 0
			m = re.match(r"(for (?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(for (?P<no_gain>no gain)\W*)", play_desc)
			if m:
				if m.group("yards"):
					yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			#pass_play.Yards = yards
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for first down
			m = re.match(r"(for a (?P<fd>1ST down))", play_desc, re.IGNORECASE)
			if m:
				fd = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fd = 0
			pass_play.First_down = fd
			# check for safety
			m = re.match(r"(for a (?P<safety>SAFETY)\s+)", play_desc)
			if m:
				safety = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				safety = 0
			pass_play.Safety = safety
			# check for fumble
		#	m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
		#	if m:
		#		fumble = 1
		#		play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
		#	else:
		#		fumble = 0
		#	pass_play.Fumble = fumble
		#	# chech for fumble lost
		#	m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
		#	if m and fumble == 1:
		#		(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
		#		if number != offense:
		#			fl = 1
		#		else:
		#			fl = 0
		#		play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
		#		pass_play.Fumble_Lost = fl
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			#pass_play.Touchdown = td
			if td:	# check extra point
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)

			if offense == home:
				home_passing_plays.append(pass_play)
				home_passing_plays_print.append(pass_play.Compile_Play())
				#print home_passing_plays[len(home_passing_plays) - 1].Compile_Play()
			else:
				visitor_passing_plays.append(pass_play)
				visitor_passing_plays_print.append(pass_play.Compile_Play())
				#print visitor_passing_plays[len(visitor_passing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Pass_Stats(pass_play, extra_point, play[0], red_zone)
				visitor_team_game_stats.Add_Def_Pass_Stats(pass_play, td, extra_point)
			elif offense == visitor:
				visitor_team_game_stats.Add_Off_Pass_Stats(pass_play, extra_point, play[0], red_zone)
				home_team_game_stats.Add_Def_Pass_Stats(pass_play, td, extra_point)

		# =============================================================================================================
		# Check for sack
		# =============================================================================================================
		m = re.match(r"((?P<passer>\D+) sacked by )", play_desc)
		if m:
			# inc play number
			play_num += 1
			# get passer
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			passer = m.group("passer")
			# init passing class
			rush_play = Rushing_Play(0, play_num, offense, passer)
			rush_play.Sack = 1
			# get sacker
			m = re.match(r"((?:(?P<sacker>\D+)|(?P<sacker_group>\D+ and \D+)) for )", play_desc)
			if m:
				if m.group("sacker"):
					sacker = m.group("sacker")
				else:
					sacker = m.group("sacker_group")
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for loss of yards
			m = re.match(r"(a (?P<loss>loss) of\W+)", play_desc)
			if m:
				loss = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				loss = 0
			# get yards gained
			yards = 0
			m = re.match(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)", play_desc)
			if m:
				if m.group("yards"):
					yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			rush_play.Yards = yards
			# get new position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for first down
			m = re.match(r"(for a (?P<fd>1ST down))", play_desc, re.IGNORECASE)
			if m:
				fd = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fd = 0
			#rush_play.First_down = fd
			# check for safety
			m = re.match(r"(for a (?P<safety>SAFETY)\s+)", play_desc)
			if m:
				safety = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				safety = 0
			rush_play.Safety = safety
			# check for fumble
			m = re.match(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)", play_desc)
			if m:
				fumble = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fumble = 0
			rush_play.Fumble = fumble
			# chech for fumble lost
			m = re.match(r"(recovered by (?P<team>\w+)(?: (?P<player>\D+))?)", play_desc)
			if m and fumble == 1:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team"), team_arr, abbv_arr, approved_abbv)
				if number != offense:
					fl = 1
				else:
					fl = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				rush_play.Fumble_Lost = fl
			# check for touchdown
			(td, play_desc) = Check_Touchdown(play_desc, play, home_score, visitor_score)
			#rush_play.Touchdown = td
			if td:	# check extra point
				(play_desc, extra_point) = Check_Extra_Point(play_desc, td)

			if offense == home:
				home_rushing_plays.append(rush_play)
				home_rushing_plays_print.append(rush_play.Compile_Play())
				#print home_rushing_plays[len(home_passing_plays) - 1].Compile_Play()
			else:
				visitor_rushing_plays.append(rush_play)
				visitor_rushing_plays_print.append(rush_play.Compile_Play())
				#print visitor_rushing_plays[len(visitor_passing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if offense == home:
				home_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				visitor_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)
			elif offense == visitor:
				visitor_team_game_stats.Add_Off_Rush_Stats(rush_play, extra_point, play[0], red_zone)
				home_team_game_stats.Add_Def_Rush_Stats(rush_play, td, extra_point)

		# =============================================================================================================
		# Check for a penalty
		# =============================================================================================================
		m = re.match(r"((?P<team1>\D+) Penalty\W+)|(Penalty (?P<team2>\w+)\W+)", play_desc, re.IGNORECASE)
		if m:
			# inc play number
			play_num += 1
			play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# set penalty class
			if m.group("team1"):
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team1"), team_arr, abbv_arr, approved_abbv)
			else:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("team2"), team_arr, abbv_arr, approved_abbv)
			penalty = Penalty(0, number, play_num)
			# get type and yards/player
			m = re.match(r"((?P<penalty_type>\D+) \(((?P<player>\D+)|(?P<loss>\-)?(?P<yards>\d+) Yards)\)\W*)", play_desc)
			if m:
				penalty.Type = m.group("penalty_type")
				penalty.Player = m.group("player") if m.group("player") != None else ""
				if m.group("yards"):
					penalty.Yards = int(m.group("yards")) if m.group("loss") == None else -1 * int(m.group("yards"))
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			m = re.match(r"((?P<penalty_type>\D+) (?P<yards>\d+) Yards\W*)", play_desc, re.IGNORECASE)
			if m:
				penalty.Type = m.group("penalty_type")
				penalty.Yards = int(m.group("yards"))
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# get yards
			m = re.match(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)", play_desc)
			if m:
				if m.group("yards"):
					yards = -1*int(m.group("yards")) if loss == 1 else int(m.group("yards"))
				elif m.group("no_gain"):
					yards = 0
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
				penalty.Yards = yards
			# get field position
			m = re.match(r"(to the (?P<field_half>\D+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?(?:\s+)?)", play_desc)
			if m:
				if m.group("field_half"):
					(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
					if number == offense:
						field_pos = int(m.group("yard_line"))
					else:
						field_pos = 100 - int(m.group("yard_line"))
				elif m.group("fifty"):
					field_pos = 50
				penalty.Field_Pos = field_pos
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			m = re.match(r"(to the (?P<field_half>\D+)(?P<yard_line>\d+))", play_desc)
			if m:
				(number, name, abbv_arr) = Find_Abbv_Team(data, m.group("field_half"), team_arr, abbv_arr, approved_abbv)
				if number == offense:
					field_pos = int(m.group("yard_line"))
				else:
					field_pos = 100 - int(m.group("yard_line"))
				penalty.Field_Pos = field_pos
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# check for first down
			m = re.search(r"(for a (?P<fd>1ST down))", play_desc, re.IGNORECASE)
			if m:
				fd = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			else:
				fd = 0
			penalty.First_down = fd
			# get declined
			m = re.match(r"declined", play_desc, re.IGNORECASE)
			if m:
				penalty.Declined = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
			# get no play
			m = re.match(r"(\D+NO PLAY\D+)", play_desc, re.IGNORECASE)
			if m:
				penalty.No_Play = 1
				play_desc = re.sub(re.escape(m.group(0)), "", play_desc)

			if penalty.Team_Code == home:
				home_penalties.append(penalty)
				home_penalties_print.append(penalty.Compile_Play())
				#print home_rushing_plays[len(home_rushing_plays) - 1].Compile_Play()
			else:
				visitor_penalties.append(penalty)
				visitor_penalties_print.append(penalty.Compile_Play())
				#print visitor_rushing_plays[len(visitor_rushing_plays) - 1].Compile_Play()

			# Add to team-game-stats
			if penalty.Team_Code == home:
				home_team_game_stats.Add_Def_Penalty_Stats(penalty)
				visitor_team_game_stats.Add_Off_Penalty_Stats(penalty)
			else:
				visitor_team_game_stats.Add_Def_Penalty_Stats(penalty)
				home_team_game_stats.Add_Off_Penalty_Stats(penalty)

		# check the score
		try:
			visitor_score = int(play[2])
			visitor_team_game_stats.Points = visitor_score
		except:
			pass
		try:
			home_score = int(play[3])
			home_team_game_stats.Points = home_score
		except:
			pass

		# check for full parsing
		if len(play_desc):
			print "\nWARNING: I couldn't parse this play!" 
			print "---------------------------------------------------------------------"
			print play_desc + "\n"
			print play[1]
			print "---------------------------------------------------------------------"
			#raw_input()

	# Return outputs
	vtgs = visitor_team_game_stats.Compile_Stats()
	htgs = home_team_game_stats.Compile_Stats()
	vrush = visitor_rushing_plays_print
	hrush = home_rushing_plays_print
	vpass = visitor_passing_plays_print
	hpass = home_passing_plays_print
	vpenl = visitor_penalties_print
	hpenl = home_penalties_print
	return (vtgs, htgs, vrush, hrush, vpass, hpass, vpenl, hpenl)


# Checks for a touchdown
def Check_Touchdown(play_desc, play, home_score, visitor_score):
	try:
		visitor_new_score = int(play[2])
	except:
		visitor_new_score = visitor_score
	try:
		home_new_score = int(play[3])
	except:
		home_new_score = home_score
	m = re.match(r"(for a (?P<td>TD))", play_desc)
	if m:
		td = 1
		play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
	if visitor_new_score >= 6 + visitor_score or home_new_score >= 6 + home_score:
		td = 1
	else:
		td = 0
	return (td, play_desc)


# Checks for extra point
def Check_Extra_Point(play_desc, td):
	m = re.match(r"(, \((?P<kicker>\D+) KICK\))", play_desc, re.IGNORECASE)
	m2 = re.match(r"(\((?P<kicker>\D+) Kick\))", play_desc, re.IGNORECASE)
	if m:
		extra_point = 1
		play_desc = re.sub(re.escape(m.group(0)), "", play_desc)
		return (play_desc, extra_point)
	elif m2:
		extra_point = 1
		play_desc = re.sub(re.escape(m2.group(0)), "", play_desc)
		return (play_desc, extra_point)
	else:
		return (play_desc, -1)


# Sets the quarter if a new one occurs
def Set_Quarter(play):
	m = re.match(r"(?P<qrt>\d)(?:st|nd|rd|th) Quarter Play-by-Play", play[0])
	if m:
		return int(m.group("qrt"))


# Finds the time in input string and sets the clock
def Set_Clock(minutes, sec):
	return 60*int(minutes) + int(sec)


def Get_Play_Info(play_info, offense):
    m = re.match(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?:(?P<team>\D+) (?P<pos>\d+)|(?P<fifty>50)))", play_info)
    if m == None:
        return (-1, -1, -1, -1)
    down = int(m.group("down"))
    dist = m.group("dist")
    if None == m.group("fifty"):
        team = m.group("team")
        pos = int(m.group("pos"))
    else:
        pos = 50
    if m.group("dist") == "Goal":
        dist = pos
    return (down, int(dist), m.group("team"), pos)

def Get_Field_Pos(team, offense, pos):
	if team != offense:
		return pos
	else:
		return 100 - pos


# ==================================================================
# ===== MAIN FUNCTION ==============================================
# ==================================================================

# Read in all play-by-play files
path = "../pbp/"
allPlays = []
allDrives = []
allTGS = []
game_files = [f for f in listdir(path) if isfile(join(path, f))]

for game_file in game_files:
	print "Analyzing " + str(game_file)

	# Read raw play-by-play
	pbp_file = path + game_file
	pbp_data = Convert_PBP_Data(pbp_file)

	# Create game and collect drive data
	game = Game(pbp_data)
	drives = Compile_Drives(pbp_data, game)

	# Parse data into play form
	plays = []
	game.Current_Qrt = 1
	for drive in drives:	# loop through all drives in the game
		for play in drive.Raw_Pbp_Data:		# loop through all plays in the drive
			game.Check_Points(play)
			game.Set_Quarter(play)
			# Set offense and defense points
			if drive.Offense == game.Home:
				off_pnts = game.Home_Pts
				def_pnts = game.Visitor_Pts
			elif drive.Offense == game.Visitor:
				off_pnts = game.Visitor_Pts	
				def_pnts = game.Home_Pts
			# Create play	
			cur_play = Play_Stats(game.Code, len(plays) + 1, game.Current_Qrt, drive.Start_Time, drive.Offense, drive.Defense, off_pnts, def_pnts, drive.Drive_Num)
			try:
				prev_play = plays[len(plays) - 1]
			except:
				prev_play = Play_Stats(0, 0, 0, 0, 0, 0, 0, 0, 0)
			if cur_play.Extract_Play_Data(play, prev_play):
				try:
					if cur_play.Drive_Number == plays[len(plays) - 1].Drive_Number + 1:
						cur_play.Drive_Play = 1
					else:
						cur_play.Drive_Play = plays[len(plays) - 1].Drive_Play + 1
				except:
					cur_play.Drive_Play = 1
				plays.append(cur_play)
				allPlays.append(cur_play)
				drive.Play_List.append(cur_play)

	# Go back and fill in remaining drive data
	for drive in drives:
		for i in range(0, len(drive.Play_List)):
			play = drive.Play_List[i]
			# get start spot
			if i == 0:
				drive.Start_Spot = play.Spot
			# check red zone attempt
			if play.Spot <= 20 and drive.Red_Zone_Att == 0:
				drive.Red_Zone_Att = 1
			# check for end of drive
			if i + 1 == len(drive.Play_List):
				drive.Stop_Spot = play.Spot
				# Partial stop reason
				if play.Off_Touchdown == 1:
					drive.Stop_Reason = "OFF_TOUCHDOWN"
				elif play.Def_Touchdown == 1:
					drive.Stop_Reason = "DEF_TOUCHDOWN"
				elif play.Fumble_Lost == 1:
					drive.Stop_Reason = "FUMBLE"
				elif play.Interception == 1:
					drive.Stop_Reason = "INTERCEPTION"
				elif play.Safety == 1:
					drive.Stop_Reason = "SAFETY"

	# Add drives to all drives
	for drive in drives:
		allDrives.append(drive)


# Write drives to file
drive_data = []
drive_data.append(drives[0].Header())
for drive in allDrives:
	drive_data.append(drive.Compile_Stats())
Write_CSV(drive_data, "2014 Stats temp/drive.csv")

# Write plays to file
play_data = []
play_data.append(plays[0].Header())
for play in allPlays:
	play_data.append(play.Compile_Stats())
Write_CSV(play_data, "2014 Stats temp/play.csv")

# # Build team-game-statistics
# home_tgs = Team_Game_Statistics(game.Code, game.Home)
# visitor_tgs = Team_Game_Statistics(game.Code, game.Visitor)
# for play in plays:
# 	if play.Offense == home_tgs.Team_Code:
# 		home_tgs.Extract_Play_Offense(play)
# 	elif play.Offense == visitor_tgs.Team_Code:
# 		visitor_tgs.Extract_Play_Offense(play)

# # Write team-game-statistics to file
# tgs_data = []
# tgs_data.append(home_tgs.Header())
# tgs_data.append(home_tgs.Compile_Stats())
# tgs_data.append(visitor_tgs.Compile_Stats())
# Write_CSV(tgs_data, "2014 Stats/team_game_statistics.csv")

# file_name = "2014 Stats/team.csv"
# team_arr = Read_CSV(file_name)
# team_arr = team_arr[1:]
# abbv_arr = Read_CSV("2014 Stats/abbrevations.csv")
# approved_abbv = []

# # Parse all data files
# week = 1
# path = "Week " + str(week)
# days = [f for f in listdir(path) if isdir(join(path, f))]
# team_game_stats = []
# tgs_header = Team_Game_Stat(0,0)
# team_game_stats.append(tgs_header.Team_Game_Stats_Header())
# for day in days:
# 	# get each game
# 	tmp_path = path + "/" + day
# 	games = [f for f in listdir(tmp_path) if isfile(join(tmp_path, f))]
# 	for game in games:
# 		print "Reading data from " + str(game)
# 		pbp_data = Read_CSV(tmp_path + "/" + game)
# 		(visitor_num, visitor, home_num, home) = Find_Teams(pbp_data, abbv_arr)
# 		print "\nVisitor: " + visitor
# 		print "Home: " + home
# 		raw_input("Game Number: " + str(visitor_num.zfill(4)) + str(home_num.zfill(4)) + str(day))
# 		game_num = str(visitor_num.zfill(4)) + str(home_num.zfill(4)) + str(day)
# 		# Parse play-by-play
# 		(vtgs, htgs, vrush, hrush, vpass, hpass, vpenl, hpenl) = Parse_Plays(game_num, pbp_data, team_arr, abbv_arr, visitor_num, home_num, approved_abbv)
# 		team_game_stats.append(vtgs)
# 		team_game_stats.append(htgs)

# Write_CSV(team_game_stats, "2014 Stats/team-game-stats.csv")


# END
raw_input("Press ENTER to finish...")