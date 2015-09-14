# TO RUN: ENTER "scrapy crawl espn" IN THE COMMAND LINE

import scrapy
import re
import string
import os
import errno
import csv
from ESPN_Scraper.items import GameItem

months = {"January": 1, "Febuary": 2, "March": 3, 
			"April": 4, "May": 5, "June": 6, "July": 7, 
			"August": 8, "September": 9, "October": 10, 
			"November": 11, "December": 12}

year = 2015

# Returns the contents of a .csv file in an array
def Read_CSV(file_name):
	print "Reading " + str(file_name) + "..."
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

def Find_Abbv(team_name, team_arr, team_abbvs):
	team_name = team_name.lower()
	team_name = team_name.replace(" ", "")
	team_name = team_name.replace("-", "")
	code = 0
	for team in team_arr:
		if team[1].lower().replace("-", "") == team_name or team[1].lower().replace(" ", "") == team_name:
			code = team[0]
			return (code, team[1], team_abbvs)
	if code == 0:
		for abbv in team_abbvs:
			if abbv[0].lower().replace("-", "") == team_name or abbv[0].lower().replace(" ", "") == team_name:
				code = abbv[1]
				return (code, abbv[0], team_abbvs)
	return Find_Abbv_Team(team_name, team_arr, team_abbvs)

# Changes an abbreviated team name to its team number
def Find_Abbv_Team(abbv, team_arr, abbv_arr):
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
					Write_CSV(abbv_arr, str(year) + " Stats/abbrevations.csv")
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
		Write_CSV(abbv_arr, str(year) + " Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)

# Make sure os path exists, create it if not
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# SPIDER
class espnSpider(scrapy.Spider):
	name = "espn"
	allowed_domains = ["espn.go.com"]
	start_urls = [
		"http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/1",
		"http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/2"#,
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/3",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/4",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/5",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/6",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/7",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/8",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/9",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/10",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/11",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/12",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/13",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/14",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/15",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/2/week/16",
		# "http://espn.go.com/college-football/scoreboard/_/group/80/year/" + str(year) + "/seasontype/3/week/1"
	]

	def parse(self, response):
		# Read team abbv data
		team_names = Read_CSV(str(year) + " Stats/team.csv")
		team_names = team_names[1:]
		team_abbvs = Read_CSV(str(year) + " Stats/abbrevations.csv")
		# Get boxscore links
		name_re = '\"location\"\:\"(\D+?(?:\\u00e9)?\D+?)\"'
		box_re = '\"href\"\:\"(http\:\/\/espn\.go\.com\/college\-football\/boxscore\?.*?)\"'
		date_re = '\"date\"\:\"(\d+\-\d+\-\d+)'
		regex_str = name_re + '.*?' + name_re + '.*?' + box_re + '.*?' + date_re
		script_blocks = response.xpath('//script[not(@*)]')
		# game info storage
		boxscore_links = []
		home = []
		away = []
		dates = []
		# find games and links
		for block in script_blocks:
			block_links = block.re(regex_str)
			counter = 0
			for link in block_links:
				if counter == 0:
					home.append(re.sub('\\\u00e9','e',link))
				elif counter == 1:
					away.append(re.sub('\\\u00e9','e',link))
				elif counter == 2:
					boxscore_links.append(link)
				elif counter == 3:
					dates.append(re.sub('-','',link))
				# count to track what data type (uuugly)
				counter += 1
				if counter == 4:
					counter = 0
		# Get week number
		if response.url.split("/")[-3] == "3":
			weekNum = "17" # bowl season
		else:
			weekNum = response.url.split("/")[-1]

		# Write page to file
		newPath = os.getcwd() + "/" + str(year) + "/week_" + weekNum
		make_sure_path_exists(newPath)
		for idx, box in enumerate(boxscore_links):
			# find codes
			(home_code, home_off, team_abbvs) = Find_Abbv(home[idx], team_names, team_abbvs)
			(away_code, away_off, team_abbvs) = Find_Abbv(away[idx], team_names, team_abbvs)
			filename = newPath + "/" + str(away_code).zfill(4) + str(home_code).zfill(4) + str(dates[idx]) + ".txt"
			with open(filename, 'w') as f:
				f.write("Date: " + dates[idx] + "\n")
				f.write("Home: " + home[idx] + " (" + str(home_code) + ")" + "\n")
				f.write("Away: " + away[idx] + " (" + str(away_code) + ")" + "\n")
				f.write("Box: " + box + "\n")
				f.write("Matchup: " + re.sub('boxscore','matchup',box) + "\n")
				f.write("PBP: " + re.sub('boxscore','playbyplay',box) + "\n")
				f.close()