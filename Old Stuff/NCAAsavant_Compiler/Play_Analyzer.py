import re
import csv
import C
import math
from Play_Attributes import *


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

def Add_Yards(ptype, play):
    if (ptype == "PASS" and play[C.COMP] == "1") or ptype == "RUSH" or ptype == "SACKED":
        try:
            yards = int(play[C.GAIN])
            return yards
        except:
            # try to manually parse yardage
            m1 = re.search(r"for (?P<yards>-?\d{1,3}) (?:yards|yard)", play[C.DESC])
            m2 = re.search(r"runs (?P<yards>\d{1,3}) (?:yards|yard) for a touchdown", play[C.DESC])
            m3 = re.search(r"for no gain", play[C.DESC])
            m4 = re.search(r"(?P<fum>FUMBLE)|(?P<oob>out of bounds)", play[C.DESC])
            if m1:
                #print "WARNING: Manually parsed yardage, returning " + str(m1.group("yards"))
                #print "         " + play[C.DESC]
                #raw_input()
                return int(m1.group("yards"))
            elif m2:
                #print "WARNING: Manually parsed yardage, returning " + str(m2.group("yards"))
                #print "         " + play[C.DESC]
                #raw_input()
                return int(m2.group("yards"))
            elif m3:
                #print "WARNING: Manually parsed yardage, returning 0"
                #print "         " + play[C.DESC]
                #raw_input()
                return 0
            elif m4:
                if self.Next_Yard_Line > -1000 and self.Yard_Line > -1000:
                    gained = self.Yard_Line - self.Next_Yard_Line
                else:
                    gained = 0
                #print "WARNING: Manually parsed yardage, returning " + str(gained)
                #print "         " + play[C.DESC]
                #raw_input()
                return gained
            else:
                print "WARNING: No yards added to play"
                print "    " + play[C.DESC]
                #raw_input()
                return 0
    else:
        return 0


#=============================================================================================================
# MAIN FUNCTION
#=============================================================================================================

# Read in play by play data
print "Reading play-by-play data... "
file_name = "2014 Stats/play-by-play.csv"
pbp_data = Read_CSV(file_name)
print "Done.\n"

# Set up the play attributes array
print "Analyzing play data... "
plays = []
for i in range(0,400):
	pos = int(math.floor(i/(4*5)))
	down = int(math.floor((i - 4*5*pos)/5))
	dist = int(i - 4*5*pos - 5*down)
	plays.append(Play_Attributes(pos, down, dist))

# Look through all plays
drive_points = 0
end_drive = 0
for i in range(1, len(pbp_data)):
	play = pbp_data[i]
	try:
		# Don't use no play
		if play[C.NOPLY] == "1" or play[C.DIR] == "ERROR":
			continue
		# Look for the result of the drive
		if i > end_drive:
			for j in range(i, len(pbp_data)):
				new_play = pbp_data[j]
				if new_play[C.GCODE] != play[C.GCODE]:	# Check for end of game
					drive_points = 0
					end_drive = j
					break
				if new_play[C.QRT] == "3" and play[C.QRT] == "2":	# Check for half time
					drive_points = 0
					end_drive = j
					break
				if new_play[C.OFF] == play[C.DEF]:	# Check for change of possession
					drive_points = 0
					end_drive = j
					break
				# Check for punt
				if new_play[C.TYPE] == "PUNT":
					drive_points = 0
					end_drive = j
					break
				# Check for safety
				m = re.search(r", safety", new_play[C.DESC])
				if m:
					drive_points = -2;
					end_drive = j
					break
				# Check for FG
				m = re.search(r"Field Goal is Good", new_play[C.DESC])
				if m:
					drive_points = 3;
					end_drive = j
					break
				# Check for TD
				if new_play[C.ISTD] == "1":
					drive_points = 7
					end_drive = j
					break
		# Convert play info to int
		play[C.YARD] = int(play[C.YARD])
		play[C.DIST] = int(play[C.DIST])
		play[C.DOWN] = int(play[C.DOWN])
		# Get play index
		pos = math.floor(play[C.YARD]/5)
		down = play[C.DOWN] - 1
		if play[C.DIST] <= 3:
			dist = 0
		elif play[C.DIST] <= 6:
			dist = 1
		elif play[C.DIST] <= 10:
			dist = 2
		elif play[C.DIST] <= 20:
			dist = 3
		else:
			dist = 4
		index = int(4*5*pos + 5*down + dist)
		plays[index].Plays += 1
		# Get play info
		if play[C.TYPE] == "RUSH":
			plays[index].Runs += 1
			plays[index].Rush_Yards.append(Add_Yards("RUSH", play))
			plays[index].Rush_Pts.append(drive_points)
		elif play[C.TYPE] == "PASS":
			plays[index].Passes += 1
			plays[index].Pass_Yards.append(Add_Yards("PASS", play))
			plays[index].Pass_Pts.append(drive_points)
		elif play[C.TYPE] == "SACKED":
			plays[index].Sacks += 1
			plays[index].Sack_Yards.append(Add_Yards("SACKED", play))
			plays[index].Sack_Pts.append(drive_points)
		elif play[C.TYPE] == "PUNT":
			plays[index].Punts += 1
		elif play[C.TYPE] == "FIELD GOAL":
			plays[index].FGs += 1
	except:
		error = 1
		#print "WARNING: Could not play info (" + str(play[C.YARD]) + ", " + str(play[C.DOWN]) + ", " + str(play[C.DIST]) + ")\n"
print "Done.\n"

# Convert data to file format
plays_output = []
plays_output.append(plays[0].Header())
for i in range(1, len(plays)+1):
	plays_output.append(plays[i-1].Compile_Data())

print "Writing play data... "
Write_CSV(plays_output, "2014 Stats/play-stats.csv")
print "Done.\n"