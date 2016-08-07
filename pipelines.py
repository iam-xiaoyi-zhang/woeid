# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import csv
import tweepy
import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from .api import *

def check_spider(func):
    def checker(self, item, spider):

        if self.__class__.__name__ not in spider.pipelines:
            print('-----skip '+self.__class__.__name__+'-----'),
            return item
        else:
            print('-----in '+self.__class__.__name__+'-----'),
            return func(self, item, spider)

    return checker

class WoeidCsvSavePipeline(object):

    def __init__(self):
        print('init WoeidCsvSavePipeline')
        self.csv_id = open('woeid/data/country_id.csv', 'a')
        self.csv_noid = open('woeid/data/country_noid.csv', 'a')
        self.id_writer = csv.writer(self.csv_id, delimiter=',', lineterminator='\n')
        self.noid_writer = csv.writer(self.csv_noid, delimiter=',', lineterminator='\n')

    def open_spider(self, spider):
        print('open spider')
        if os.stat("woeid/data/country_id.csv").st_size == 0:
            self.id_writer.writerow(["original name", "county", "state", "country", "woeid"])
        if os.stat("woeid/data/country_noid.csv").st_size == 0:
            self.noid_writer.writerow(["original name"])

    @check_spider
    def process_item(self, item, spider):
        print('process_item', item['origin'], item['district_county'],
              item['province_state'], item['country'], item['woeid'])

        if item['woeid'] != '':
            self.id_writer.writerow([item['origin'], item['district_county'],
                                     item['province_state'], item['country'], item['woeid']])
        else:
            self.noid_writer.writerow([item['origin']])
        return item

# DOING
class WoeidMongoSavePipeline(object):

    def __init__(self):
        # 1. set connection
        print('init WoeidMongoSavePipeline')
        print('-----CONNECTING TO MONGODB-----')
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        # 2. check if db.collection exists.
        db = connection[settings['MONGODB_DB_WOEID']]
        self.collection = db[settings['MONGODB_COLLECTION_WOEID']]

    @check_spider
    def process_item(self, item, spider):
        # insert
        # note: There is no need to update any records because woeid for every city is constant.
        #       And for now, there is no need to check the data, because I want to do it in the app
        #       level.  Possibly records will be checked here in the future.

        # 1. check the existance of data (possible) (using indexing or check a pre-defined key)
        print('producing')

        # 2. insert data
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))

        if valid:
            self.collection.insert(dict(item))
            log.msg("Item added to MongoDB database!",
                    level=log.DEBUG, spider=spider)

        return item


class GeoplanetPipeline(object):

    @check_spider
    def process_item(self, item, spider):
        # print(item)
        print('in GeoplanetPipeline')


class TwitterGeoTrendsAPIPipeline(object):

    def __init__(self):
        print("-----CONNECTING TO TWITTER API-----")
        self.auth = tweepy.OAuthHandler(twitter_consumer_key,
                                        twitter_consumer_secret)
        self.auth.set_access_token(twitter_access_token,
                                   twitter_access_secret)
        self.api = tweepy.API(self.auth)

    @check_spider
    def process_item(self, item, spider):
        print("-----GET Trends-----")
        trend = self.api.trends_place(item['woeid'])[0]
        item['twitterTrends'] = trend.pop('trends')
        item['twitterTrendsInfo'] = trend
        return item



class TwitterTrendsMongoSavePipeline(object):

    def __init__(self):
        print("-----CONNECTING TO MONGODB-----")
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    @check_spider
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))

        if valid:
            self.collection.insert(dict(item))
            log.msg("Item added to MongoDB database!",
                    level=log.DEBUG, spider=spider)

        return item


