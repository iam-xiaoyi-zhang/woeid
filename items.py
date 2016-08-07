# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WoeidItem(scrapy.Item):
    # for spider countryid
    origin = scrapy.Field()
    district_county = scrapy.Field()
    province_state = scrapy.Field()
    country = scrapy.Field()
    woeid = scrapy.Field()
    twitterTrends = scrapy.Field()
    twitterTrendsInfo = scrapy.Field()

class GeoplanetItem(scrapy.Item):
    # for spider geoplanet
    place_info = scrapy.Field()

class PlaceAvailableItem(scrapy.Item):
    country = scrapy.Field()
    countryCode = scrapy.Field()
    name = scrapy.Field()
    parentid = scrapy.Field()
    placeType = scrapy.Field()
    url = scrapy.Field()
    woeid = scrapy.Field()

class TwitterTrendsItem(scrapy.Item):
    trendsInfo = scrapy.Field()
