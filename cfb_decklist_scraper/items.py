# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Standing(scrapy.Item):
    player = scrapy.Field()
    rank = scrapy.Field()
    point = scrapy.Field()


class Deck(scrapy.Item):
    player = scrapy.Field()
    archetype = scrapy.Field()
    maindeck = scrapy.Field()
    sideboard = scrapy.Field()


class MatchResult(scrapy.Item):
    win_player = scrapy.Field()
    lose_player = scrapy.Field()
