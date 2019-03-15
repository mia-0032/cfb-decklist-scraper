# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Deck(scrapy.Item):
    builder_name = scrapy.Field()
    rank = scrapy.Field()
    point = scrapy.Field()
    archetype = scrapy.Field()
    maindeck = scrapy.Field()
    sideboard = scrapy.Field()
