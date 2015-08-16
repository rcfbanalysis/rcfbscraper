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

year = 2014

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
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=1",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=2",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=3",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=4",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=5",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=6",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=7",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=8",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=9",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=10",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=11",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=12",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=13",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=14",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=15",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=2&weekNumber=16",
		"http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=" + str(year) + "&seasonType=3&weekNumber=17"
	]

	def parse(self, response):
		# Read team abbv data
		team_names = Read_CSV(str(year) + " Stats/team.csv")
		team_names = team_names[1:]
		team_abbvs = Read_CSV(str(year) + " Stats/abbrevations.csv")
		# Parse the days of the week
		raw_days = response.xpath('//h4[contains(@class, "games-date")]/text()').extract()
		days = []
		for day in raw_days:
			day_split = day.split(',')
			days.append(day_split[0])
		# Get game containers
		gameDays = response.xpath('//div[contains(@class, "gameDay-Container")]')
		gameDates = response.xpath('//h4[contains(@class, "games-date")]/text()').extract()
		# Begin to set game items
		games = []
		for i in range(0, len(gameDays)):
			day = gameDays[i]
			date = gameDates[i].split()
			date = str(date[3]) + str(months[date[1]]).zfill(2) + str(date[2]).zfill(2)
			for game in day.xpath('.//div[contains(@id, "gameContainer")]'):
				new_game = GameItem()
				tmpID = game.re(r'\d+-gameContainer')	# must remove letters from ID
				table = string.maketrans('','')
				digits = table.translate(table, string.digits)
				new_game['gameID'] = str(tmpID).translate(table, digits)
				new_game['date'] = date
				new_game['home'] = str(game.xpath('.//div[@class="team home"]/div[@class="team-capsule"]/p[@class="team-name"]/span/a/text()').extract())
				new_game['visitor'] = str(game.xpath('.//div[@class="team visitor"]/div[@class="team-capsule"]/p[@class="team-name"]/span/a/text()').extract())
				new_game['play_link'] = str(game.xpath('.//li/a[contains(@href, "playbyplay")]/@href').extract())
				new_game['drive_link'] = str(game.xpath('.//li/a[contains(@href, "drivechart")]/@href').extract())
				new_game['box_link'] = str(game.xpath('.//li/a[contains(@href, "boxscore")]/@href').extract())
				games.append(new_game)
		# Write page to file
		weekNum = response.url.split("=")[-1]
		newPath = os.getcwd() + "/" + str(year) + "/week_" + weekNum
		make_sure_path_exists(newPath)
		for game in games:
			home = game['home'][3:len(game['home'])-2]				# strip home name
			(home_code, home_off, team_abbvs) = Find_Abbv(home, team_names, team_abbvs)				# find home code
			visitor = game['visitor'][3:len(game['visitor'])-2]		# strip visitor name
			(visitor_code, visitor_off, team_abbvs) = Find_Abbv(visitor, team_names, team_abbvs)	# find visitor code
			filename = newPath + "/" + str(visitor_code).zfill(4) + str(home_code).zfill(4) + str(game['date']) + ".txt"
			with open(filename, 'w') as f:
				f.write("Date: " + game['date'] + "\n")
				f.write("Home: " + home + " (" + str(home_code) + ")" + "\n")
				f.write("Visitor: " + visitor + " (" + str(visitor_code) + ")" + "\n")
				f.write("Plays: " + "http://scores.espn.go.com" + game['play_link'][3:len(game['play_link'])-2] + "\n")
				f.write("Drives: " + "http://scores.espn.go.com" + game['drive_link'][3:len(game['drive_link'])-2] + "\n")
				f.write("Box: " + "http://scores.espn.go.com" + game['box_link'][3:len(game['box_link'])-2] + "\n")
				f.close()