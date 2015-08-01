# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

# Top level game item
class GameItem(scrapy.Item):
	gameID = scrapy.Field()
	date = scrapy.Field()
	home = scrapy.Field()
	visitor = scrapy.Field()
	play_link = scrapy.Field()
	drive_link = scrapy.Field()
	box_link = scrapy.Field()

# Top level game item
class PBP_GameItem(scrapy.Item):
	code = scrapy.Field()
	date = scrapy.Field()
	home_code = scrapy.Field()
	visitor_code = scrapy.Field()
	link = scrapy.Field()

# Top level game item
class BOX_GameItem(scrapy.Item):
	code = scrapy.Field()
	date = scrapy.Field()
	home_code = scrapy.Field()
	visitor_code = scrapy.Field()
	link = scrapy.Field()