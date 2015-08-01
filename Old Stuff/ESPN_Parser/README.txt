TO SCRAPE DATA FROM ESPN:
   1. Put the correct start urls in "espnSpider.py" in this folder. Put each weekly scoreboard for the week that you want to scrape.
	ex: (2014, Week 1) "http://scores.espn.go.com/ncf/scoreboard?confId=80&seasonYear=2014&seasonType=2&weekNumber=1"
   2. Run "scrapy crawl espn" to populate each week's url info for plays, box scores, and drive data
   3. Run "scrapy crawl (drive|playbyplay|boxscore)" in this folder consecutively to get box score data drive data and play-by-play data
	Make sure folders "box", "drive", and "pbp" exist in this folder
   4. The files are named in the format:
	"visitor code" + "home code" + "yyyymmdd" .csv