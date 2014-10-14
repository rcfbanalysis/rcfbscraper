
import re
import csv
import C
from Team_Game_Stat import *


#=============================================================================================================
# FUNCTION DEFINITIONS
#=============================================================================================================

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
def Find_Abbv_Team(data, abbv, team_arr, abbv_arr):

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
		print "\nGuess: " + str(abbv) + " = " + str(team_sort[i][2])
		user_in = raw_input("Enter 0 for incorrect match, 1 for correct match, or 2 for unknown: ")
		for name in team_arr:
			if user_in == name[1]:
				if abbv_arr != 0:
					abbv_arr.append([abbv, name[0], name[1]])
					Write_CSV(abbv_arr, "2014 Stats/abbrevations.csv")
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
		Write_CSV(abbv_arr, "2014 Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)


# Return game date (MM/DD/YYYY) in YYYYMMDD format
def Get_Date(date):
	m1 = re.match(r"(?P<month>\d{1,2})\/(?P<day>\d{1,2})\/(?P<year>\d{4})", date)
	m2 = re.match(r"(?P<year>\d{4})\-(?P<month>\d{1,2})\-(?P<day>\d{1,2})", date)
	if None == m1 and None == m2:
		print date
		raw_input()
	if None != m1:
		return str(m1.group("year")).zfill(2) + str(m1.group("month")).zfill(2) + str(m1.group("day")).zfill(2)
	elif None != m2:
		return str(m2.group("year")).zfill(2) + str(m2.group("month")).zfill(2) + str(m2.group("day")).zfill(2)


# Converts pbp date from NCAAsavant to my format
def Convert_PBP_Data(pbp_file):

	# Read in play-by-play data
	print "Reading raw play-by-play data..."
	pbp_data = Read_CSV(pbp_file)
	pbp_data = pbp_data[1:]
	print "Done"

	# Read in team and abbreviation data
	team_data = Read_CSV("2014 Stats/team.csv")
	team_data = team_data[1:]
	try:
		abbv_arr = Read_CSV("2014 Stats/abbrevations.csv")
	except:
		print "WARNING: abbrevations.csv not found\n"
		abbv_arr = []

	# Replace team names with numbers
	for line in pbp_data:
		teams = []
		# find home team
		(number, name, abbv_arr) = Find_Abbv_Team(pbp_data, line[C.HOME], team_data, abbv_arr)
		line[C.HOME] = number
		teams.append([number,name])
		# find away team
		(number, name, abbv_arr) = Find_Abbv_Team(pbp_data, line[C.VSTR], team_data, abbv_arr)
		line[C.VSTR] = number
		teams.append([number,name])
		# find team dir
		if len(line[C.DIR]) > 0 and line[C.DIR] != "ERROR":
			(number, name, abbv_arr) = Find_Abbv_Team(pbp_data, line[C.DIR], teams, abbv_arr)
			line[C.DIR] = number
		# find defense
		(number, name, abbv_arr) = Find_Abbv_Team(pbp_data, line[C.DEF], team_data, abbv_arr)
		line[C.DEF] = number
		# find offense
		(number, name, abbv_arr) = Find_Abbv_Team(pbp_data, line[C.OFF], team_data, abbv_arr)
		line[C.OFF] = number
		# parse game date
		line[C.GCODE] = str(line[C.VSTR]).zfill(4) + str(line[C.HOME]).zfill(4) + Get_Date(line[C.DATE])

	Write_CSV(pbp_data, "2014 Stats/play-by-play.csv")


#=============================================================================================================
# MAIN FUNCTION
#=============================================================================================================

# Convert PBP
pbp_file = "Raw PBP/Week 7/pbp-2014.csv"
Convert_PBP_Data(pbp_file)
raw_input("Done converting file...\n")

# Read in statistics
print "Reading play-by-play data..."
file_name = "2014 Stats/play-by-play.csv"
pbp_data = Read_CSV(file_name)
print "Done.\n"

# Compile stats
print "Compiling stats from play-by-play data..."
prev_game = 0
tgs_home = Team_Game_Stat(0, 0, 0)
tgs_visit = Team_Game_Stat(0, 0, 0)
tgs_array = []
tgs_array.append(tgs_home.Team_Game_Stats_Header())
use_game = True	# game is valid for use
home_bad_plays = 0
visit_bad_plays = 0
max_bad_plays = 3	# if a number of bad plays occur in a row, discard game

for i in range(0, len(pbp_data)):
	play = pbp_data[i]
	if i + 1 < len(pbp_data):
		next_play = pbp_data[i + 1]

	# Check for a new game
	if prev_game != play[C.GCODE]:
		if tgs_home.Game_Code != 0 and use_game:	# add data to array
			tgs_array.append(tgs_home.Compile_Stats())
			tgs_array.append(tgs_visit.Compile_Stats())
		tgs_home = Team_Game_Stat(play[C.GCODE], play[C.HOME], play)
		tgs_visit = Team_Game_Stat(play[C.GCODE], play[C.VSTR], play)
		home_bad_plays = 0
		visit_bad_plays = 0
		use_game = True

	# Add this play to T-G-Stats
	try:
		offense = int(play[C.OFF])
	except:
		print "WARNING: Couldn't get offense, ignoring play"
		print "  		Game Code: " + str(play[C.GCODE])
		continue

	if tgs_home.Team_Code == offense:		# home
		# Check for a bad game
		if home_bad_plays >= max_bad_plays and use_game:
			use_game = False
			if home_bad_plays == max_bad_plays:
				print "WARNING: Not using game " + str(tgs_home.Game_Code)
			continue
		# Extract play
		elif use_game:
			error = tgs_home.Extract_Play_Data(play, next_play)
			if error == 1:
				home_bad_plays += 1
			else:
				home_bad_plays = 0
	elif tgs_visit.Team_Code == offense:	# visitor
		# Check for a bad game
		if visit_bad_plays >= max_bad_plays and use_game:
			use_game = False
			if visit_bad_plays == max_bad_plays:
				print "WARNING: Not using game " + str(tgs_visit.Game_Code)
			continue
		# Extract play
		elif use_game:
			error = tgs_visit.Extract_Play_Data(play, next_play)
			if error == 1:
				visit_bad_plays += 1
			else:
				visit_bad_plays = 0

	prev_game = play[C.GCODE]
print "Done.\n"

print "Writing team-game-stats data..."
Write_CSV(tgs_array, "2014 Stats/team-game-stats.csv")
print "Done.\n"


# END
raw_input("Press ENTER to finish...")