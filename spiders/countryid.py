# -*- coding: utf-8 -*-
import re
import scrapy
from ..items import WoeidItem

class CountryidSpider(scrapy.Spider):
    name = "countryid"
    pipelines = {'WoeidCsvSavePipeline'}
                 #'WoeidMongoSavePipeline'}  #'TwitterGeoTrendsAPIPipeline', 'TwitterTrendsMongoSavePipeline'}
    # allowed_domains = ["woeid.rosselliot.co.nz/lookup"]
    start_urls = (
        'http://woeid.rosselliot.co.nz/lookup/',
    )
    start_url = 'http://woeid.rosselliot.co.nz/lookup/'

    def parse(self, response):
        # load countries we want
        countries = open('countriesoftheworld.txt', 'r')
        _ = countries.readline()  # get rid of column name
        for country in countries:
            country = re.sub('[^\w|\s|\\-]|\\n', '', country)  # obay the input form
            yield scrapy.Request(
                url=self.start_url+country,
                callback=self.after_request
            )

    def after_request(self, response):
        item = WoeidItem()
        # get the input name of country
        try:
            item['origin'] = response.xpath('(//form/div)[2]/input/@value').extract()[0]
        except IndexError:
            item['origin'] = response.url[37:]

        # get the woeid
        if response.xpath('//table').extract():
            item['woeid'] = response.xpath('(//table/tr)[1]/@data-woeid').extract()[0]
            print(response.url[37:], item['woeid'])
        else:
            item['woeid'] = ''
            print('something wrong with getting the woeid for: '+item['origin'])

        # get the District-County name
        # get the Province-State name
        # get the country name in the website
        if item['woeid'] != '':
            # should I use .encode('utf-8') down here?????
            item['district_county'] = response.xpath('(//table/tr)[1]/@data-district_county').extract()[0]
            item['province_state'] = response.xpath('(//table/tr)[1]/@data-province_state').extract()[0]
            item['country'] = response.xpath('(//table/tr)[1]/@data-country').extract()[0]
        else:
            item['city'] = ''
            item['district_county'] = ''
            item['province_state'] = ''
            item['country'] = ''

        yield item

        # How to detect things like "C?te d'Ivoire" ?

