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


# SPIDER
class matchSpider(scrapy.Spider):
	name = "matchup"
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
				m = re.search(r"Matchup: (?P<url>\S+)", data)
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

		# Scrape first downs
		first_div = response.xpath('//tr[@data-stat-attr="firstDowns"]')
		away_TGS.First_Down_Total = re.sub(r'[\\\t|\\\n]','',first_div.xpath('.//td/text()').extract()[1])
		home_TGS.First_Down_Total = re.sub(r'[\\\t|\\\n]','',first_div.xpath('.//td/text()').extract()[2])

		# Scrape turnovers
		fumble_div = response.xpath('//tr[@data-stat-attr="fumblesLost"]')
		away_TGS.Fum_Lost = re.sub(r'[\\\t|\\\n]','',fumble_div.xpath('.//td/text()').extract()[1])
		home_TGS.Fum_Lost = re.sub(r'[\\\t|\\\n]','',fumble_div.xpath('.//td/text()').extract()[2])
		away_TGS.Fum_Ret = home_TGS.Fum_Lost
		home_TGS.Fum_Ret = away_TGS.Fum_Lost

		# Scrape first down efficiency on 3rd down
		eff_div = response.xpath('//tr[@data-stat-attr="thirdDownEff"]')
		fatt_away = re.sub(r'[\\\t|\\\n]','',eff_div.xpath('.//td/text()').extract()[1])
		fatt_home = re.sub(r'[\\\t|\\\n]','',eff_div.xpath('.//td/text()').extract()[2])
		# away
		m = re.search(r'(?P<f>\d+)\-(?P<a>\d+)', fatt_away)
		away_TGS.Third_Down_Att = m.group('a')
		away_TGS.Third_Down_Conv = m.group('f')
		# home
		m = re.search(r'(?P<f>\d+)\-(?P<a>\d+)', fatt_home)
		home_TGS.Third_Down_Att = m.group('a')
		home_TGS.Third_Down_Conv = m.group('f')

		# Scrape first down efficiency on 4th down
		eff_div = response.xpath('//tr[@data-stat-attr="fourthDownEff"]')
		fatt_away = re.sub(r'[\\\t|\\\n]','',eff_div.xpath('.//td/text()').extract()[1])
		fatt_home = re.sub(r'[\\\t|\\\n]','',eff_div.xpath('.//td/text()').extract()[2])
		# away
		m = re.search(r'(?P<f>\d+)\-(?P<a>\d+)', fatt_away)
		away_TGS.Fourth_Down_Att = m.group('a')
		away_TGS.Fourth_Down_Conv = m.group('f')
		# home
		m = re.search(r'(?P<f>\d+)\-(?P<a>\d+)', fatt_home)
		home_TGS.Fourth_Down_Att = m.group('a')
		home_TGS.Fourth_Down_Conv = m.group('f')

		# Scrape time of possession
		top_div = response.xpath('//tr[@data-stat-attr="possessionTime"]')
		try:
			top_away = re.sub(r'[\\\t|\\\n]','',top_div.xpath('.//td/text()').extract()[1])
		except:
			top_away =  "30:00"
		try:
			top_home = re.sub(r'[\\\t|\\\n]','',top_div.xpath('.//td/text()').extract()[2])
		except:
			top_home =  "30:00"

		# away
		m_away = re.search(r'(?P<h>\d+)\:(?P<m>\d+)', top_away)
		# home
		m_home = re.search(r'(?P<h>\d+)\:(?P<m>\d+)', top_home)
		try:
			away_TGS.Time_Of_Possession = str(60*int(m_away.group('h')) + int(m_away.group('m')))
			home_TGS.Time_Of_Possession = str(60*int(m_home.group('h')) + int(m_home.group('m')))
		except:
			away_TGS.Time_Of_Possession = 1800
			home_TGS.Time_Of_Possession = 1800
		if int(away_TGS.Time_Of_Possession) == 1800 and int(home_TGS.Time_Of_Possession) != 1800:
			away_TGS.Time_Of_Possession = str(3600 - int(home_TGS.Time_Of_Possession))
		elif int(home_TGS.Time_Of_Possession) == 1800 and int(away_TGS.Time_Of_Possession) != 1800:
			home_TGS.Time_Of_Possession = str(3600 - int(away_TGS.Time_Of_Possession))

		# Scrape penalties
		pen_div = response.xpath('//tr[@data-stat-attr="totalPenaltiesYards"]')
		pen_away = re.sub(r'[\\\t|\\\n]','',pen_div.xpath('.//td/text()').extract()[1])
		pen_home = re.sub(r'[\\\t|\\\n]','',pen_div.xpath('.//td/text()').extract()[2])
		# away
		m = re.search(r'(?P<tot>\d+)\-(?P<yds>\d+)', pen_away)
		away_TGS.Penalty = m.group('tot')
		away_TGS.Penalty_Yard = m.group('yds')
		# home
		m = re.search(r'(?P<tot>\d+)\-(?P<yds>\d+)', pen_home)
		home_TGS.Penalty = m.group('tot')
		home_TGS.Penalty_Yard = m.group('yds')


		# Write stats to file
		if os.path.isfile(str(year) + " Stats/matchup-stats.csv"):
			f = open(str(year) + " Stats/matchup-stats.csv","a")
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
			Write_CSV(new_rows, str(year) + " Stats/matchup-stats.csv")