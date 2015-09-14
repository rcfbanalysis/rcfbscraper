import scrapy
import re
import string
import os
import errno
import csv
import pdb
from ESPN_Scraper.items import BOX_GameItem
from Team_Game_Statistics import *
import ESPNSpiderFunctions

year = 2015
num_weeks = 2

# Make sure os path exists, create it if not
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

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
		csvfile.close()

# Extracts passing stats from boxscore
def Extract_Passing(TGS, div):
	pass_totals = div.xpath('.//tr[@class="highlight"]')
	try:
		catt = pass_totals.xpath('.//td[@class="c-att"]/text()').extract()[0]
		m = re.search(r'(?P<c>\d+)/(?P<a>\d+)', catt)
		TGS.Pass_Att = m.group('a')
		TGS.Pass_Comp = m.group('c')
	except:
		TGS.Pass_Att = 0
		TGS.Pass_Comp = 0
	TGS.Pass_Yard = pass_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
	TGS.Pass_TD = pass_totals.xpath('.//td[@class="td"]/text()').extract()[0]
	TGS.Pass_Int = pass_totals.xpath('.//td[@class="int"]/text()').extract()[0]
	return TGS

# Extracts rushing stats from boxscore
def Extract_Rushing(TGS, div):
	rush_totals = div.xpath('.//tr[@class="highlight"]')
	TGS.Rush_Att = rush_totals.xpath('.//td[@class="car"]/text()').extract()[0]
	TGS.Rush_Yard = rush_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
	TGS.Rush_TD = rush_totals.xpath('.//td[@class="td"]/text()').extract()[0]
	return TGS

# Extracts kick return stats from boxscore
def Extract_KickReturns(TGS, div):
	kr_totals = div.xpath('.//tr[@class="highlight"]')
	try:
		TGS.Kickoff_Ret = kr_totals.xpath('.//td[@class="no"]/text()').extract()[0]
		TGS.Kickoff_Ret_Yard = kr_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
		TGS.Kickoff_Ret_TD = kr_totals.xpath('.//td[@class="td"]/text()').extract()[0]
	except:
		TGS.Kickoff_Ret = "0"
		TGS.Kickoff_Ret_Yard = "0"
		TGS.Kickoff_Ret_TD = "0"
	return TGS

# Extracts punt return stats from boxscore
def Extract_PuntReturns(TGS, div):
	pr_totals = div.xpath('.//tr[@class="highlight"]')
	try:
		TGS.Punt_Ret = pr_totals.xpath('.//td[@class="no"]/text()').extract()[0]
		TGS.Punt_Ret_Yard = pr_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
		TGS.Punt_Ret_TD = pr_totals.xpath('.//td[@class="td"]/text()').extract()[0]
	except:
		TGS.Punt_Ret = "0"
		TGS.Punt_Ret_Yard = "0"
		TGS.Punt_Ret_TD = "0"
	return TGS

# Extracts points from boxscore
def Extract_Points(TGS, div):
	score_box = div.xpath('.//div[@class="score-container"]')
	TGS.Points = score_box.xpath('.//div[contains(@class,"score")]/text()').extract()[0]
	return TGS

# Extracts interception stats from boxscore
def Extract_Interceptions(TGS, div):
	int_totals = div.xpath('.//tr[@class="highlight"]')
	try:
		TGS.Int_Ret = int_totals.xpath('.//td[@class="int"]/text()').extract()[0]
		TGS.Int_Ret_Yard = int_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
		TGS.Int_Ret_TD = int_totals.xpath('.//td[@class="td"]/text()').extract()[0]
	except:
		TGS.Int_Ret = "0"
		TGS.Int_Ret_Yard = "0"
		TGS.Int_Ret_TD = "0"
	return TGS

# Extracts kicking stats from boxscore
def Extract_Kicking(TGS, div):
	kick_totals = div.xpath('.//tr[@class="highlight"]')
	# field goals
	try:
		fatt = kick_totals.xpath('.//td[@class="fg"]/text()').extract()[0]
		m = re.search(r'(?P<f>\d+)/(?P<a>\d+)', fatt)
		TGS.Field_Goal_Made = m.group('f')
		TGS.Field_Goal_Att = m.group('a')
	except:
		TGS.Field_Goal_Made = "0"
		TGS.Field_Goal_Att = "0"
	# extra points
	try:
		xatt = kick_totals.xpath('.//td[@class="xp"]/text()').extract()[0]
		m = re.search(r'(?P<x>\d+)/(?P<a>\d+)', xatt)
		TGS.Off_XP_Kick_Made = m.group('x')
		TGS.Off_XP_Kick_Att = m.group('a')
	except:
		TGS.Off_XP_Kick_Made = "0"
		TGS.Off_XP_Kick_Att = "0"
	return TGS

# Extracts kicking stats from boxscore
def Extract_Punting(TGS, div):
	punt_totals = div.xpath('.//tr[@class="highlight"]')
	try:
		TGS.Punt = punt_totals.xpath('.//td[@class="no"]/text()').extract()[0]
		TGS.Punt_Yard = punt_totals.xpath('.//td[@class="yds"]/text()').extract()[0]
	except:
		TGS.Punt = "0"
		TGS.Punt_Yard = "0"
	return TGS


# SPIDER
class boxscoreSpider(scrapy.Spider):
	name = "boxscore"
	allowed_domains = ["espn.go.com"]
	# Build URLs from scraped data
	start_urls = []
	for i in range(1, num_weeks+1):
		make_sure_path_exists(str(year) + "/week_" + str(i))
		folder = str(year) + "/week_" + str(i)
		os.chdir(folder)
		for filename in os.listdir(os.getcwd()):
			new_game = BOX_GameItem()
			with open (filename, "r") as f:
				data = f.read()
				# Get start URL
				m = re.search(r"Box: (?P<url>\S+)", data)
				if ''.join(e for e in m.group("url") if e.isalnum()) == "httpespngocomcollegefootball":
					continue
				# Save boxscore link and team stats link
				start_urls.append(m.group("url"))
				new_game['link'] = m.group("url")
				# Get date
				m = re.search(r"Date: (?P<date>\d+)", data)
				new_game['date'] = m.group("date")
				# Get home
				m = re.search(r"Home: \D+ \((?P<code>\d+)\)", data)
				new_game['home_code'] = m.group("code")
				# Get away
				m = re.search(r"Away: \D+ \((?P<code>\d+)\)", data)
				new_game['away_code'] = m.group("code")
			infofile = ''.join(e for e in new_game['link'] if e.isalnum())
			make_sure_path_exists(os.getcwd() + "/../../tmpfiles/")
			with open(os.getcwd() + "/../../tmpfiles/" + infofile + ".txt", 'w') as f:
				f.write(new_game['link'] + "\n")
				f.write("Code: " + str(new_game['away_code']).zfill(4))
				f.write(str(new_game['home_code']).zfill(4))
				f.write(new_game['date'])
				f.close()
		os.chdir("../..")


	def parse(self, response):
		# Get this game code from file
		with open(os.getcwd() + "/tmpfiles/" + ''.join(e for e in response.url if e.isalnum()) + ".txt") as f:
			data = f.read()
			m = re.search(r"Code: (?P<code>\d+)", data)
			code = str(m.group('code')).zfill(16)

		# Scrape box score
		away = int(long(code) / 1e12)
		home = int((long(code) / 1e8) % 1e3)
		date = int(long(code) % 1e8)
		away_TGS = Team_Game_Statistics(code, away)
		home_TGS = Team_Game_Statistics(code, home)

		# MOVE SOME OF THESE TO MATCHUP SCRAPER

		# Scrape passing
		pass_div = response.xpath('//div[@id="gamepackage-passing"]')
		# away
		away_pass_div = pass_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_Passing(away_TGS, away_pass_div)
		# home
		home_pass_div = pass_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_Passing(home_TGS, home_pass_div)

		# Scrape rushing
		rush_div = response.xpath('//div[@id="gamepackage-rushing"]')
		# away
		away_rush_div = rush_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_Rushing(away_TGS, away_rush_div)
		# home
		home_rush_div = rush_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_Rushing(home_TGS, home_rush_div)

		# Scrape kick returns
		kr_div = response.xpath('//div[@id="gamepackage-kickReturns"]')
		# away
		away_kr_div = kr_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_KickReturns(away_TGS, away_kr_div)
		# home
		home_kr_div = kr_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_KickReturns(home_TGS, home_kr_div)

		# Scrape punt returns
		pr_div = response.xpath('//div[@id="gamepackage-puntReturns"]')
		# away
		away_pr_div = pr_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_PuntReturns(away_TGS, away_pr_div)
		# home
		home_pr_div = pr_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_PuntReturns(home_TGS, home_pr_div)

		# Scrape interception returns
		int_div = response.xpath('//div[@id="gamepackage-interceptions"]')
		# away
		away_int_div = int_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_Interceptions(away_TGS, away_int_div)
		# home
		home_int_div = int_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_Interceptions(home_TGS, home_int_div)

		# Scrape kicking
		kick_div = response.xpath('//div[@id="gamepackage-kicking"]')
		# away
		away_kick_div = kick_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_Kicking(away_TGS, away_kick_div)
		# home
		home_kick_div = kick_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_Kicking(home_TGS, home_kick_div)

		# Scrape punting
		punt_div = response.xpath('//div[@id="gamepackage-punting"]')
		# away
		away_punt_div = punt_div.xpath('.//div[contains(@class,"gamepackage-away-wrap")]')
		away_TGS = Extract_Punting(away_TGS, away_punt_div)
		# home
		home_punt_div = punt_div.xpath('.//div[contains(@class,"gamepackage-home-wrap")]')
		home_TGS = Extract_Punting(home_TGS, home_punt_div)

		# Get points
		points_div = response.xpath('//div[@class="competitors"]')
		away_points = points_div.xpath('.//div[contains(@class,"away")]')
		away_TGS = Extract_Points(away_TGS, away_points)
		home_points = points_div.xpath('.//div[contains(@class,"home")]')
		home_TGS = Extract_Points(home_TGS, home_points)

		# Write stats to file
		if os.path.isfile(str(year) + " Stats/boxscore-stats.csv"):
			f = open(str(year) + " Stats/boxscore-stats.csv","a")
			data_writer = csv.writer(f, lineterminator = '\n')
			new_rows = []
			new_rows.append(away_TGS.Compile())
			new_rows.append(home_TGS.Compile())
			data_writer.writerows(new_rows)
			f.close()
		else:
			new_rows = []
			new_rows.append(away_TGS.Header())
			new_rows.append(away_TGS.Compile())
			new_rows.append(home_TGS.Compile())
			Write_CSV(new_rows, str(year) + " Stats/boxscore-stats.csv")