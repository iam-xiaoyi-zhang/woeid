# This is for all branches in under one single place

# -*- coding: utf-8 -*-
import scrapy
from ..items import GeoplanetItem


class GeoplanetSpider(scrapy.Spider):
    name = "geoplanet"
    pipelines = {'GeoplanetPipeline'}
    # allowed_domains = ["http://isithackday.com/geoplanet-explorer/index.php?"]
    # start_urls = (
    #     'http://isithackday.com/geoplanet-explorer/index.php?',
    # )
    start_url = 'http://isithackday.com/geoplanet-explorer/'
    index = 'index.php?'  # be careful about the detail.php and index.php
    detail = 'detail.php?'
    woe_id = '2151330'
    # Boston not working anymore

    def start_requests(self):
        print('in start_request')
        # Basic requests from a list of locations
        locations = [self.woe_id]
        for location in locations:
            yield scrapy.Request(self.start_url+self.index+'woeid='+location,
                                 callback=self.parse)

    def parse(self, response):
        print('in parse')
        item = GeoplanetItem()
        # 1st get basic info
        item['place_info'] = self.get_place_info(response)
        # print(place_info)
        # 2nd check how many see_all are there
        branches = [('Children:', 'children'), ('Neighbours:', 'neighbors'),
                    ('Siblings:', 'siblings'), ('Parent:', 'parent'),
                    ('Ancestors', 'ancestors'), ('Belongs to:', 'belongtos')]
        for branch_xpath, branch_url in branches:
            if response.xpath('//h3[text()="'+branch_xpath+'"]/parent::div//p[@class="seeall"]'):
                print('turn to', response.url.replace(self.index, self.detail))
                yield scrapy.Request(response.url.replace(self.index, self.detail)+'&type='+branch_url,
                                     callback=lambda arg1=response, arg2=branch_xpath: self.get_branch(arg1, arg2))
            else:
                print('not many children')
                yield self.get_branch(response, branch_xpath)

        yield item

    def get_place_info(self, response):
        print('in get_place_info')
        info_selector = response.xpath('//ul[@id="placeinfo"]/li')
        info = self.get_node(info_selector)
        print('basic info:', info)
        return info

    def get_branch(self, response, branch_xpath):
        """
        :param response:
        :param branch_xpath: in ['Children:', 'Neighbours:', 'Siblings:', 'Parent:', 'Ancestors', 'Belongs to:']
        :return:
        """
        print('in get '+branch_xpath)
        print(response)  # testing
        print(response.url)
        children_selector = response.xpath('//h3[text()="'+branch_xpath+'"]/parent::div/ul[@class="collapse"]/li')
        print(len(children_selector))
        nodes = children_selector
        children_list = []
        for node in nodes:
            children_list.append(self.get_node(node))
            print('get_node end'),  # testing

        print('start yielding items')  # testing
        for node in children_list:
            yield node

    def get_node(self, selector):
        print('in get_node'),
        unit = GeoplanetItem()
        name = selector.xpath('a[contains(@href,"index.php")]/text()').extract()[0]
        country = selector.xpath('ul/li[contains(text(),"Country")]/text()').extract()[0].split(': ')[1]
        woeid = selector.xpath('ul/li[contains(text(),"WOEID")]/text()').extract()[0].split(': ')[1]
        latlon = selector.xpath('ul/li[contains(text(),"Location")]/a/text()').extract()[0].split(', ')
        boundne = selector.xpath('ul/li[contains(text(),'
                                 '"Bounding Box")]/p[1]/text()').extract()[0][3:].split(', ')
        boundsw = selector.xpath('ul/li[contains(text(),'
                                 '"Bounding Box")]/p[2]/text()').extract()[0][3:].split(', ')
        unit = {'Name': name, 'Country': country, 'WOEID': woeid, 'latlon': latlon,
                'boundNE': boundne, 'boundSW': boundsw}
        try:
            unit['postalcode'] = selector.xpath('ul/li[contains(text(),"Postal")]/text()').extract()[0].split(' ')[1]
        except:
            unit['postalcode'] = 'None'

        return unit

