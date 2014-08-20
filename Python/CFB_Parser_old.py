# IMPORTS
import re


# ===== GAME CLASS ==================================================
class Game:
	HomeName = "NULL"
	HomeCode = 0
	VisitorName = "NULL"
	VisitorCode = 0
	HomeScore = 0
	VisitorScore = 0
	Plays = []


	# Constructor
	def __init__(self, hName, hCode, vName, vCode):
		self.HomeName = hName
		self.HomeCode = hCode
		self.VisitorName = vName
		self.VisitorCode = vCode


	# Adds a score to the appropriate team
	def SetGameScore(self, teamCode, add, play):
		if teamCode == self.HomeCode:		# home team score
			self.HomeScore += add
		elif teamCode == self.VisitorCode:	# visitor team score
			self.VisitorScore += add
		else:
			play.PlayWarning("Score is not assigned to either team")


# ===== PLAY CLASS ==================================================
class Play:
	# Initalized in constructor
	PlayNum = 0
	Down = 0
	Distance = 0
	OffCode = 0
	DefCode = 0
	DriveNum = 0
	# Initialized later
	Spot = 0
	DrivePlay = 1
	Type = "NULL"
	OffScore = 0
	DefScore = 0
	Clock = 0
	QuarNum = 0


	# Constructor
	def __init__(self, playNum, down, distance, offense, defense, drive):
		self.PlayNum = playNum
		self.Down = down
		self.Distance = distance
		self.OffCode = offense
		self.DefCode = defense
		self.DriveNum = drive
		self.OutputArray = []


	# Finds the time in input string and sets the clock
	def SetClock(self, input):
		if None == re.search(r"\d{1,2}:\d{1,2}", input):
			self.PlayWarning("Clock not set")
		else:
			time = re.findall(r"\d{1,2}:\d{1,2}", input)
			time = time[0].split(":")
			self.Clock = 60*int(time[0]) + int(time[1])


	# Uses game data to set the offensive and defensive score
	def SetPlayScore(self, game):
		if self.OffCode == game.HomeCode:		# home team on offense
			self.OffScore = game.HomeScore
			self.DefScore = game.VisitorScore
		elif self.OffCode == game.VisitorCode:	# visitor team on offense
			self.OffScore = game.VisitorScore
			self.DefScore = game.HomeScore
		else:
			self.PlayWarning("Offense code does not match either home or visitor team")


	# Get the type of play
	def SetPlayType(self, result, info):
		typeIDs = ["rush", "lost", "pass", "intercepted", "punt", "field goal", "extra point", "kicked"]
		typeVals = ["RUSH", "RUSH", "PASS", "PASS", "PUNT", "FIELD_GOAL", "ATTEMPT", "KICKOFF"]
		typesFound = 0
		for i in range(0, len(typeIDs)):	# look for type identifier
			if None != re.search(typeIDs[i], result, re.IGNORECASE):	# found a match in play result
				self.Type = typeVals[i]
				typesFound += 1
			if None != re.search(typeIDs[i], info, re.IGNORECASE):		# found a match in play info
				self.Type = typeVals[i]
				typesFound += 1
			
		# Drive stuff is NULL or 0 for all, down and distance NULL for kickoff / attempt
		nullDriveStuff = ["KICKOFF", "ATTEMPT", "PUNT"]
		for type in nullDriveStuff:
			if type == self.Type:
				self.DrivePlay = "NULL"
				self.DriveNum = "NULL"
				if type == "KICKOFF" or type == "ATTEMPT":
					self.Distance = "NULL"
					self.Down = "NULL"
		
		if self.Type == "NULL":
			self.PlayWarning("No play type detected")


	# Gets the real spot, using the input string
	def SetRealSpot(self, spot):
		if None != re.search(str(self.OffCode), spot):		# on own half
			realSpot = int(spot[len(str(self.OffCode)):])
			return 100 - realSpot
		elif None != re.search(str(self.DefCode), spot):	# on opponent's half
			return int(spot[len(str(self.DefCode)):])
		else:
			self.PlayWarning("No field position found")


	# Determines if a team scored on a play and increments their score accordingly
	def ScoringPlay(self, result, info, game):
		scoringTeam = "NULL"
		scoringAmount = 0
		
		# Touchdown (+6)
		if None != re.search("Touchdown", result, re.IGNORECASE):
			self.OffScore += 6
			scoringAmount = 6
			scoringTeam = self.OffCode
		
		# Extra point
		if self.Type == "ATTEMPT":
			if None != re.search("made", info, re.IGNORECASE):		# made (+1)
				self.OffScore += 1
				scoringAmount = 1
				scoringTeam = self.OffCode
			elif None != re.search("miss", info, re.IGNORECASE):	# missed (place holder)
				self.OffScore += 0
				scoringAmount = 0
				scoringTeam = self.OffCode
			else:
				self.PlayWarning("ATTEMPT not set to 'make' or 'miss'")
		
		# Extra point
		if self.Type == "FIELD_GOAL":
			if None != re.search("made", result, re.IGNORECASE):		# made (+3)
				self.OffScore += 3
				scoringAmount = 3
				scoringTeam = self.OffCode
			elif None != re.search("miss", result, re.IGNORECASE):	# missed (place holder)
				self.OffScore += 0
				scoringAmount = 0
				scoringTeam = self.OffCode
			else:
				self.PlayWarning("FIELD_GOAL not set to 'make' or 'miss'")
			
		return (scoringTeam, scoringAmount)


	# Puts all the data for this play into an array to write out
	def CompileAndSend(self):
		self.OutputArray.append(str(self.PlayNum) + ",")
		self.OutputArray.append(str(self.QuarNum) + ",")
		self.OutputArray.append(str(self.Clock) + ",")
		self.OutputArray.append(str(self.OffCode) + ",")
		self.OutputArray.append(str(self.DefCode) + ",")
		self.OutputArray.append(str(self.OffScore) + ",")
		self.OutputArray.append(str(self.DefScore) + ",")
		self.OutputArray.append(str(self.Down) + ",")
		self.OutputArray.append(str(self.Distance) + ",")
		self.OutputArray.append(str(self.Spot) + ",")
		self.OutputArray.append(str(self.Type) + ",")
		self.OutputArray.append(str(self.DriveNum) + ",")
		self.OutputArray.append(str(self.DrivePlay) + "\n")
		return self.OutputArray


	# Displays a warning for bad inputs
	def PlayWarning(self, message):
		print "WARNING: " + str(message)
		print "  Play Number: " + str(self.PlayNum)
		print "       Result: " + str(result)
		print "         Info: " + str(info) + "\n"


# ===== READ CSV ==================================================
# Reads in the contents of a .csv file and splits data by comma (,)
def ReadCSV(file):
	print "Reading in " + str(file) + " data..."
	datafile = open(file, 'r')
	data = []
	for row in datafile:
		data.append(row.strip("\n").split(","))
	datafile.close()
	return data


# ===== MAIN FUNCTION ==================================================
# Parses file and returns relavent stats
print "\n                      CFB PARSER                       "
print   "=====================================================\n"

# Read file contents into a data array
rdFile = "musiccitydata.csv"
print "Parsing data from: " + str(rdFile)
data = ReadCSV(rdFile)

# Append data to file
wFile = "test_play.csv"
playWriteData = []

# Read header and team info
homeTeam = data[0][0]
visitorTeam = data[0][1]
homeCode = data[0][2]
visitorCode = data[0][3]
game = Game(homeTeam, homeCode, visitorTeam, visitorCode)
header = data[1][:]

# Loop through data, parsing plays
nPlay = 0		# game play number
nDrive = 0		# drive number
offense = homeCode
defense = visitorCode

for i in range(2, len(data[:])):
	playData = data[i]
	playRegex = r"(\d{1,2}\-\d{1,2}\-" + "(" + re.escape(homeCode) + "|" + re.escape(visitorCode) + "))|(extra point)"
	
	# Look for change in possession
	if None != re.search(homeTeam, playData[0], re.IGNORECASE):			# home team got possession
		offense = homeCode
		defense = visitorCode
		nDrive += 1
	elif None != re.search(visitorTeam, playData[0], re.IGNORECASE):	# visitor team got possession
		offense = visitorCode
		defense = homeCode
		nDrive += 1
	elif None != re.search(playRegex, playData[0], re.IGNORECASE):		# regular play occured
		# read all data and increment play number
		nPlay += 1
		info = playData[0]
		result = playData[1]
		down = playData[2]
		distance = playData[3]
		spot = playData[4]
		
		# Create the new play
		newPlay = Play(nPlay, down, distance, offense, defense, nDrive)
		newPlay.SetClock(str(info) + str(result))
		newPlay.SetPlayScore(game)
		
		# Set play type and spot
		newPlay.SetPlayType(result, info)
		if newPlay.Type == "ATTEMPT":
			newPlay.Spot = "NULL"
		else:
			newPlay.Spot = newPlay.SetRealSpot(spot)

		# Fixes bug where kickoff incremented drive number an extra time
		if newPlay.Type == "KICKOFF":
			nDrive -= 1

		# ******************************
		# TO DO: This section checks for a penalty. To get penalty info correctly, the distance of the play
		# 	(ie pass dist, rush dist, ect) needs to be done. Possibly regex for digits after 'for' and before 'yards'.
		# ******************************
		# Checks for a penalty 
		#if newPlay.Type == "NULL" and None != re.search("penal", result, re.IGNORECASE):	# play is a penalty
		#	newPlay.Type = "PENALTY"
		#elif None != re.search("penal", result, re.IGNORECASE):								# play is a play + penalty
		#	penPlay = 
		# 
		
		# Add new score
		scoringTeam, scoringAmount = newPlay.ScoringPlay(result, info, game)
		if scoringAmount > 0:
			game.SetGameScore(scoringTeam, scoringAmount, newPlay)
		
		# Save this play to array
		if newPlay.Type != "NULL":
			playWriteData.append(newPlay.CompileAndSend())
		else:
			nPlay -= 1
			newPlay.PlayWarning("This play is being removed")
		
		# add play to the game
		game.Plays.append(newPlay)

# Append data to file
datafile = open(wFile, "w")
for play in playWriteData:
	for data in play:
		datafile.write(data)
datafile.close()

# ===== END PARSING ==================================================
raw_input()