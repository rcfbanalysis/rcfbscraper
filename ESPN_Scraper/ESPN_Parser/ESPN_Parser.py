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

year = 2013


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


# Determines whether to add a team to the replacement array
def Add_To_Replacement(to_be_replaced, abbv):
	for prev_abbv in to_be_replaced:
		if prev_abbv[0] == abbv:
			return False
	return True


# Sorts array by length of string in first column
def Sort_Replacement(to_be_replaced):
	# init sort array
	sort_TBR = []
	for TBR in to_be_replaced:
		sort_TBR.append("NULL_NULL")
	# loop through all unsorted
	for TBR in to_be_replaced:
		i = 0
		# find correct spot
		while i < len(sort_TBR) - 1:
			if len(TBR[0]) > len(sort_TBR[i][0]) or sort_TBR[i][0] == "NULL_NULL":
				break
			else:
				i += 1
		# shift down
		j = len(sort_TBR) - 1
		while j > i:
			sort_TBR[j] = sort_TBR[j-1]
			j -= 1
		sort_TBR[i] = TBR
	# for TBR in sort_TBR:
	# 	print TBR
	return sort_TBR


# Converts pbp date from ESPN to my format
def Convert_PBP_Data(pbp_file):

	# Read in play-by-play data
	print "\nReading raw play-by-play data..."
	pbp_data = Read_CSV(pbp_file)
	print "Done"

	# Read in team and abbreviation data
	team_arr = Read_CSV("../" + str(year) + " Stats/team.csv")
	team_arr = team_arr[1:]
	try:
		abbv_arr = Read_CSV("../" + str(year) + " Stats/abbrevations.csv")
	except:
		print "WARNING: abbrevations.csv not found\n"
		abbv_arr = []

	# Find and replace team names
	teams = []
	(team1_code, team1_name, team2_code, team2_name, abbv_arr) = Define_Team_Names(pbp_data, team_arr, abbv_arr)
	to_be_replaced = []

	# pbp_data = Replace_All_Names(pbp_data, team1_name, "t" + team1_code)
	# pbp_data = Replace_All_Names(pbp_data, team2_name, "t" + team2_code)
	to_be_replaced.append([team1_name, "t" + team1_code])
	to_be_replaced.append([team2_name, "t" + team2_code])
	teams.append([team1_code, team1_name])
	teams.append([team2_code, team2_name])

	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		start = re.match(r"(?P<offense>\D+) at (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0], re.IGNORECASE)
		if start:
			if Add_To_Replacement(to_be_replaced, str(start.group("offense"))):
				(code, name, abbv_arr) = New_Find_Abbv_Team(start.group("offense"), teams, abbv_arr, pbp_data, i)
				# pbp_data = Replace_All_Names(pbp_data, str(start.group("offense")), "t" + code)
				to_be_replaced.append([str(start.group("offense")), "t" + code])

	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		stop = re.match(r"(?P<offense>\D+) DRIVE TOTALS\: (?P<plays>\d+) play(?:s)?\, (?:\-)?(?P<yards>\d+) (?:yards|yard|yds|yd)(\, (?P<min>\d{1,2})\:(?P<sec>\d{2}))?", play[0], re.IGNORECASE)
		if stop:
			if Add_To_Replacement(to_be_replaced, str(stop.group("offense"))):
				(code, name, abbv_arr) = New_Find_Abbv_Team(stop.group("offense"), teams, abbv_arr, pbp_data, i)
				# pbp_data = Replace_All_Names(pbp_data, str(stop.group("offense")), "t" + code)
				to_be_replaced.append([str(stop.group("offense")), "t" + code])

	# Find and replace home/visitor score abbreviations
	visitor_code = team1_code
	visitor_name = team1_name
	home_code = team2_code
	home_name = team2_name
	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		if len(play) > 3 and play[2] != "" and not is_number(play[2]):
			if play[2] != play[3]:
				# pbp_data = Replace_All_Names(pbp_data, str(play[2]), "t" + visitor_code)
				# pbp_data = Replace_All_Names(pbp_data, str(play[3]), "t" + home_code)
				if Add_To_Replacement(to_be_replaced, str(play[2])):
					to_be_replaced.append([str(play[2]), "t" + visitor_code])
				if Add_To_Replacement(to_be_replaced, str(play[3])):
					to_be_replaced.append([str(play[3]), "t" + home_code])
			pbp_data[i][2] = "t" + visitor_code
			pbp_data[i][3] = "t" + home_code

	# Find and replace home/visitor spot abbreviations
	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		m = re.match(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?P<team>\D+) (?P<pos>\d+))", play[0])
		if m:
			if Add_To_Replacement(to_be_replaced, str(m.group("team"))):
				(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("team"), teams, abbv_arr, pbp_data, i)
				# pbp_data = Replace_All_Names(pbp_data, str(m.group("team")), "t" + code)
				to_be_replaced.append([str(m.group("team")), "t" + code])

	# Find and replace field position abbreviations
	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		if len(play) > 1:
			m = re.search(r"to the (?P<team>\D+) \d{1,2}", play[1])
			if m:
				if Add_To_Replacement(to_be_replaced, str(m.group("team"))):
					(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("team"), teams, abbv_arr, pbp_data, i)
					# pbp_data = Replace_All_Names(pbp_data, str(m.group("team")), "t" + code)
					to_be_replaced.append([str(m.group("team")), "t" + code])

	# Replace all abbreviations (in order of abbreviation length to prevent misclassifications)
	to_be_replaced = Sort_Replacement(to_be_replaced)
	for abbv in to_be_replaced:
		pbp_data = Replace_All_Names(pbp_data, abbv[0], abbv[1])

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

	for i in range(0,len(pbp_data)):
		play = pbp_data[i]
		m = re.match(r"(?P<offense>\D+) at \d+\:\d+", play[0])
		if m:
			(code, name, abbv_arr) = New_Find_Abbv_Team(m.group("offense"), team_arr, abbv_arr, pbp_data, i)
			if team1_code == 0:
				team1_code = code
				team1_name = name
			elif team2_code == 0:
				team2_code = code
				team2_name = name
		if team1_code != 0 and team2_code != 0:
			return (team1_code, team1_name, team2_code, team2_name, abbv_arr)


# Changes an abbreviated team name to its team number
def New_Find_Abbv_Team(abbv, team_arr, abbv_arr, data, data_pos):
	# Check if it is already matched
	if abbv_arr != 0:
		for team in abbv_arr:
			if abbv.lower() == team[0].lower():
				return (team[1], team[2], abbv_arr)
	for team in team_arr:
		if abbv.lower() == team[1].lower():
			return (team[0], team[1], abbv_arr)
	# Sort teams
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
		# check in team array
		for name in team_arr:
			if user_in == "t" + name[0] or user_in == name[1]:
				if user_in == name[1]:
					save_abbvs = raw_input("Save abbrevations?")
					if abbv_arr != 0 and save_abbvs == "1":
						abbv_arr.append([abbv, name[0], name[1]])
						Write_CSV(abbv_arr, "../" + str(year) + " Stats/abbrevations.csv")
				return (name[0], name[1], abbv_arr)
		# check in abbv array
		for name in abbv_arr:
			if re.match(re.sub("[\(\)]", "", user_in), re.sub("[\(\)]", "", name[0]), re.IGNORECASE):
				return (name[1], name[2], abbv_arr)
		# other options
		if user_in == "":
			print "Please enter 1 or 0"
			continue
		elif user_in == "1":
			break
		elif user_in == "2":
			print "Previous: " + str(data[data_pos-1])
			print "This:     " + str(data[data_pos])
			print "Current:  " + str(data[data_pos+1])
			print "The next option is " + str(team_sort[i + 1][2])
			continue
		i += 1
		if i == len(team_sort):
			i = 0
	if abbv_arr != 0:
		abbv_arr.append([abbv, team_sort[i][1], team_sort[i][2]])
		Write_CSV(abbv_arr, "../" + str(year) + " Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)


# Replaces all occurrances of a string with another
def Replace_All_Names(pbp_data, name, number):
	# middle of string
	k = re.compile(r" %s " % re.escape(name), re.IGNORECASE)						# replaces whole word abbreviations
	for i in range(0, len(pbp_data)):
		for j in range(0, len(pbp_data[i])):
			pbp_data[i][j] = k.sub(" " + number + " ", pbp_data[i][j])
	# beginning of string
	k = re.compile(r"\A%s " % re.escape(name), re.IGNORECASE)						# replaces whole word abbreviations
	for i in range(0, len(pbp_data)):
		for j in range(0, len(pbp_data[i])):
			pbp_data[i][j] = k.sub(number + " ", pbp_data[i][j])
	# end of string
	k = re.compile(r" %s\Z" % re.escape(name), re.IGNORECASE)						# replaces whole word abbreviations
	for i in range(0, len(pbp_data)):
		for j in range(0, len(pbp_data[i])):
			pbp_data[i][j] = k.sub(" " + number, pbp_data[i][j])
	# replaces spot abbreviations (ex: BAYLOR49)
	k = re.compile(r"%s(?P<spot>\d{1,2})" % re.escape(name), re.IGNORECASE)
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
	ignore_start = False
	new_Half = False
	prev_off = 0
	prev_start = ""
	for play in pbp_data:

		start = re.match(r"t(?P<offense>\d+) at (?P<min>\d{1,2})\:(?P<sec>\d{2})", play[0])
		stop = re.match(r"t(?P<team>\d+) DRIVE TOTALS\: (?P<plays>\d+) play(?:s)?\, (?:\-)?(?P<yards>\d+) (?:yards|yard|yds|yd)(\, (?P<min>\d{1,2})\:(?P<sec>\d{2}))?", play[0], re.IGNORECASE)

		quarter_start1 = game.Set_Quarter(play)
		quarter_start2 = re.match(r"(?P<qrt>\d)(?:st|nd|rd|th) Quarter Play-by-Play", play[0], re.IGNORECASE)
		if quarter_start1 and quarter_start2:
			new_Quarter = True
			if game.Current_Qrt == 1 or game.Current_Qrt == 3:
				new_Half = True
		elif not quarter_start1 and quarter_start2:
			ignore_start = True

		if start:	# Check for the start of a new drive
			if ignore_start:
				ignore_start = False
			elif prev_start == play[0] and cur_drive.Finished == 0 and cur_drive.Game_Code != 0:
				continue
			elif not new_Quarter or (new_Quarter and prev_off != int(start.group("offense"))) or new_Half:
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
					print "Couldn't find who the offense is"
					raw_input()
				start_time = Set_Clock(start.group("min"), start.group("sec"))

				if cur_drive.Finished == 0 and cur_drive.Game_Code != 0:
					print "WARNING: Drive summary never produced"
					print play[0]
					print game.Current_Qrt
					print new_Quarter
					print new_Half
					print prev_off
					print int(start.group("offense"))
					# raw_input()
					drives.append(cur_drive)

				prev_start = play[0]
				prev_off = offense
				new_Quarter = False
				new_Half = False
				cur_drive = Drive(game.Code, offense, defense, start_time, game.Current_Qrt, len(drives) + 1)
		elif stop:	# Check for the end of a drive
			plays = int(stop.group("plays"))
			yards = int(stop.group("yards"))
			try:
				stop_time = Set_Clock(stop.group("min"), stop.group("sec"))
			except:
				stop_time = cur_drive.Start_Time
			cur_drive.Set_Summary(plays, yards, stop_time, game.Current_Qrt)
			if cur_drive.Game_Code != 0:
				# print "Summary produced"
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


# Sets the quarter if a new one occurs
def Set_Quarter(play):
	m = re.match(r"(?P<qrt>\d)(?:st|nd|rd|th) Quarter Play-by-Play", play[0])
	if m:
		return int(m.group("qrt"))


# Finds the time in input string and sets the clock
def Set_Clock(minutes, sec):
	return 60*int(minutes) + int(sec)


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
unparsed_plays = []
game_files = [f for f in listdir(path) if isfile(join(path, f))]

for game_file in game_files:

	# check to make sure it is from this year
	file_year = int(game_file[8:12])
	if file_year != year:
		continue
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
	replica = False
	nReplica = 0
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

				# check to make sure this play isn't a replica
				if replica:
					# if previous was a replica
					cur_play.Play_Number -= nReplica
					cur_play.Drive_Play -= nReplica
					replica = False
					nReplica = 0
				for dr_play in drive.Play_List:
					if dr_play.Distance == cur_play.Distance and dr_play.Down == cur_play.Down and dr_play.Spot == cur_play.Spot and dr_play.Play_Desc == cur_play.Play_Desc:
						replica = True
						nReplica += 1
						break
				if not replica:
					plays.append(cur_play)
					allPlays.append(cur_play)
					drive.Play_List.append(cur_play)
			else:
				unparsed_plays.append(play)

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

print "\nFinishing up..."

# Write drives to file
drive_data = []
drive_data.append(drives[0].Header())
for drive in allDrives:
	drive_data.append(drive.Compile_Stats())
Write_CSV(drive_data, str(year) + " Stats temp/drive.csv")

# Write plays to file
play_data = []
play_data.append(plays[0].Header())
for play in allPlays:
	play_data.append(play.Compile_Stats())
Write_CSV(play_data, str(year) + " Stats temp/play.csv")

# Write plays to file
play_data = []
for play in unparsed_plays:
	play_data.append(play)
Write_CSV(play_data, str(year) + " Stats temp/unparsed_plays.csv")

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
Write_CSV(tgs_data, str(year) + " Stats temp/play_TGS.csv")

# END
raw_input("Press ENTER to finish...")