# ==================================================================
# ===== IMPORTS ====================================================
# ==================================================================
import re
import csv
import math
from os import listdir
from os.path import isdir, isfile, join

from Game import *
from Drive import *
from Play_Stats import *
from Team_Game_Statistics import *


# ==================================================================
# ===== FUNCTIONS ==================================================
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

	for play in pbp_data:
		start = re.match(r"(?P<offense>\D+) at (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		if start:
			print play[0]
			(code, name, abbv_arr) = New_Find_Abbv_Team(start.group("offense"), team_arr, abbv_arr)
			pbp_data = Replace_All_Names(pbp_data, str(start.group("offense")), "t" + code)

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
	# flag = 0
	# if int(team1_code) == 30 and int(team2_code) == 27:
	# 	print "1: " + str(team1_code)
	# 	print "2: " + str(team2_code)
	# 	print "Home: " + str(home_code)
	# 	print "Visitor: " + str(visitor_code)
	# 	flag = raw_input()
	# elif int(team1_code) == 27 and int(team2_code) == 30:
	# 	print "1: " + str(team1_code)
	# 	print "2: " + str(team2_code)
	# 	print "Home: " + str(home_code)
	# 	print "Visitor: " + str(visitor_code)
	# 	flag = raw_input()
	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		if len(play) > 3 and play[2] != "" and not is_number(play[2]):
			if play[2] != play[3]:
				pbp_data = Replace_All_Names(pbp_data, str(play[2]), "t" + visitor_code)
				pbp_data = Replace_All_Names(pbp_data, str(play[3]), "t" + home_code)
			pbp_data[i][2] = "t" + visitor_code
			pbp_data[i][3] = "t" + home_code

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

	# if int(flag) == 1:
	# 	for play in pbp_data:
	# 		print play
	# 	raw_input()

	return pbp_data


# Locates the names of the two teams in this game (uses team name in drive switching)
def Define_Team_Names(pbp_data, team_arr, abbv_arr):

	# Try game code first
	team1_name = ""
	team2_name = ""
	try:
		team1_code = str(Extract_Team_Code(pbp_data[0][0],"v"))
		team2_code = str(Extract_Team_Code(pbp_data[0][0],"h"))
		for team in team_arr:
			if int(team[0]) == int(team1_code):
				team1_name = team[1]
			if int(team[0]) == int(team2_code):
				team2_name = team[1]
	except:
		pass
	if team1_name != "" and team2_name != "":
		return (team1_code, team1_name, team2_code, team2_name, abbv_arr)
	
	# Find the two teams
	team1_code = pbp_data[0][2]
	team2_code = pbp_data[0][3]
	for team in team_arr:
		if int(team[0]) == int(team1_code):
			team1_name = team[1]
		if int(team[0]) == int(team2_code):
			team2_name = team[1]
	if team1_name != "" and team2_name != "":
		return (team1_code, team1_name, team2_code, team2_name, abbv_arr)
	else:
		print pbp_data[0]
		raw_input()

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
	for team in team_arr:
		if abbv == team[1]:
			return (team[0], team[1], abbv_arr)
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
	new_Quarter = False
	for play in pbp_data:

		game.Set_Quarter(play)
		start = re.match(r"t(?P<offense>\d+) at (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		stop = re.match(r"t(?P<team>\d+) DRIVE TOTALS\: (?P<plays>\d+) play(?:s)?\, (?:\-)?(?P<yards>\d+) (?:yards|yard|yds|yd)\, (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		quarter_start = re.search("Quarter Play-by-Play",play[0],re.IGNORECASE)
		if quarter_start:
			new_Quarter = True

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
			if new_Quarter:
				new_Quarter = False
			else:
				if cur_drive.Finished != 1 and cur_drive.Game_Code != 0:
					# print "WARNING: Drive summary never produced"
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


def Extract_Team_Code(game_code, team):
	if team == "v":
		return int(int(math.floor(float(game_code)/1e12)))
	elif team == "h":
		return int(int(math.floor(float(game_code)/1e8)) % 1e4)
	else:
		flag = raw_input("h or v?")
		return Extract_Team_Code(game_code, flag)



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
	Write_CSV(pbp_data, "../tmpfiles/" + str(game_file))

	# Create game and collect drive data
	game = Game(pbp_data)
	if game.Date == 0:
		print "Bad game code"
		print pbp_data[0][0]
		raw_input()
	try:
		game.Visitor = int(Extract_Team_Code(game.Code, "v"))
		game.Home = int(Extract_Team_Code(game.Code, "h"))
	except:
		game.Set_Home_Visitor(pbp_data)
		print pbp_data[0][0]
		for play in pbp_data:
			print play
			raw_input()
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

		play_count = 0
		for play in drive.Play_List:
			if play.Play_Type in ['PASS','RUSH','SACK']:
				play_count += 1
		if drive.Plays != play_count and drive.Plays > 0:
			print "Play number mismatch"

	# Go back and fill in remaining drive data
	for drive in drives:
		new_Play_List = list(set(drive.Play_List))
		if len(new_Play_List) != len (drive.Play_List):
			print "Duplicate items in drive possible error"

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

# Build team-game-statistics
prev_game_code = 0
allTGS = []
for play in allPlays:
	# found a new game
	if float(play.Game_Code) != prev_game_code:
		# save old data
		if prev_game_code != 0:
			allTGS.append(home_tgs)
			allTGS.append(visitor_tgs)
		visitor_code = int(math.floor(float(play.Game_Code)/1e12))
		home_code = int(math.floor(float(play.Game_Code)/1e8)) % 1e4
		home_tgs = Team_Game_Statistics(play.Game_Code, home_code)
		visitor_tgs = Team_Game_Statistics(play.Game_Code, visitor_code)
		prev_game_code = float(play.Game_Code)
	# increment data
	if play.Offense == home_tgs.Team_Code:
		home_tgs.Extract_Play_Offense(play)
	elif play.Offense == visitor_tgs.Team_Code:
		visitor_tgs.Extract_Play_Offense(play)

# Write team-game-statistics to file
tgs_data = []
tgs_data.append(allTGS[0].Header())
for tgs in allTGS:
	tgs_data.append(tgs.Compile_Stats())
Write_CSV(tgs_data, "2014 Stats temp/team_game_statistics.csv")

# END
raw_input("Press ENTER to finish...")