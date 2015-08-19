import scrapy
import re
import string
import os
import errno
import csv
from ESPN_Scraper.items import PBP_GameItem

year = 2013

# Make sure os path exists, create it if not
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Writes the contents of data to a .csv file
def Write_CSV(data, file_name):
	with open(file_name, "w") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)
		csvfile.close()

# SPIDER
class playbyplaySpider(scrapy.Spider):
	name = "playbyplay"
	allowed_domains = ["espn.go.com"]

	# Build URLs from scraped data
	start_urls = []
	for i in range(1, 18):
		make_sure_path_exists(str(year) + "/week_" + str(i))
		folder = str(year) + "/week_" + str(i)
		os.chdir(folder)
		for filename in os.listdir(os.getcwd()):
			new_game = PBP_GameItem()
			with open (filename, "r") as f:
				data = f.read()
				# Get start URL
				m = re.search(r"Plays: (?P<url>\S+)", data)
				if ''.join(e for e in m.group("url") if e.isalnum()) == "httpscoresespngocom":
					continue
				start_urls.append(m.group("url") + "&period=0")
				new_game['link'] = m.group("url") + "&period=0"
				# Get date
				m = re.search(r"Date: (?P<date>\d+)", data)
				new_game['date'] = m.group("date")
				# Get home
				m = re.search(r"Home: \D+ \((?P<code>\d+)\)", data)
				new_game['home_code'] = m.group("code")
				# Get visitor
				m = re.search(r"Visitor: \D+ \((?P<code>\d+)\)", data)
				new_game['visitor_code'] = m.group("code")
			infofile = ''.join(e for e in new_game['link'] if e.isalnum())
			make_sure_path_exists(os.getcwd() + "/../../tmpfiles/")
			with open(os.getcwd() + "/../../tmpfiles/" + infofile + ".txt", 'w') as f:
				f.write(new_game['link'] + "\n")
				f.write("Code: " + str(new_game['visitor_code']).zfill(4))
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
		# Scrape play by play
		table = response.xpath('//table[contains(@class, "mod-pbp")]')
		rows = []
		visitor = int(code) / 1000000000000
		home = (int(code) / 100000000) % 1000
		date = int(code) % 100000000
		rows.append([code, "", visitor, home])
		for row in table.xpath('.//tr'):
			new_rows1 = [x.xpath('.//text()').extract() for x in row.xpath('.//td')]
			if len(new_rows1) > 0:
				rows.append(new_rows1)
			new_rows2 = [x.xpath('.//text()').extract() for x in row.xpath('.//th')]
			if len(new_rows2) > 0:
				if len(new_rows2) == 3:
					new_rows2 = [new_rows2[0], "", new_rows2[1], new_rows2[2]]
				rows.append(new_rows2)
			for i in range(0, len(rows[len(rows)-1])):
				rows[len(rows)-1][i] = ''.join([re.sub(r"\[u'\\xa0'\]|', |\[u'|u'|'\]|\[|\]", '', str(rows[len(rows)-1][i]))])
		# make_sure_path_exists(os.getcwd() + "pbp")
		Write_CSV(rows, "pbp/" + str(visitor).zfill(4) + str(home).zfill(4) + str(date) + ".csv")

