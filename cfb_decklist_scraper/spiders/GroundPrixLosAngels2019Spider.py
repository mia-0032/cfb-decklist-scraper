# -*- coding: utf-8 -*-

import scrapy
import re

from bs4 import BeautifulSoup

from cfb_decklist_scraper.items import Deck


class GroundPrixLosAngels2019Spider(scrapy.Spider):
    name = 'ground_prix_los_angels_2019'

    def start_requests(self):
        urls = [
            'https://magic.wizards.com/en/events/coverage/gplosangeles19/final-standings',
            'https://www.channelfireball.com/grand-prix-los-angeles-day-2-deck-lists/',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        domain = response.url.split("/")[2]
        soup = BeautifulSoup(response.text, 'lxml')

        if domain == 'magic.wizards.com':
            self._parse_standings(soup)
        else:
            return self._parse_decklist(soup)

    def _parse_standings(self, soup):
        table = soup.find('div', id='content-detail-page-of-an-article')

        self._standings = {}
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')

            name = tds[1].get_text()

            if name == 'Player':
                continue

            rank = int(tds[0].get_text())
            point = int(tds[2].get_text())

            name = re.sub(r'\s+\[[A-Z]+\]$', '', name).split(', ')
            name.reverse()
            name = ' '.join(name)

            self._standings[name] = {'rank': rank, 'point': point}

    def _parse_decklist(self, soup):
        post_content = soup.find('div', class_='postContent')

        builders = post_content.find_all('h3')

        self._not_found_players = []

        for builder in builders:
            builder_name = builder.get_text()

            if builder_name in ['', 'Discussion']:
                continue

            deck_content = builder.find_next('div').find('div', class_='plain-text-decklist').find('pre').get_text()
            maindeck, sideboard = deck_content.split('Sideboard', 1)

            maindeck = [l.split(' ', 1) for l in maindeck.strip().split('\r\n')]
            maindeck = {l[1]: int(l[0]) for l in maindeck}

            sideboard = [l.split(' ', 1) for l in sideboard.strip().split('\r\n')]
            sideboard = {l[1]: int(l[0]) for l in sideboard}

            archetype = None
            standing = self._standings.get(builder_name, {'rank': None, 'point': None})

            if builder_name not in self._standings:
                self._not_found_players.append(builder_name)

            yield Deck(
                builder_name=builder_name, rank=standing['rank'], point=standing['point'],
                archetype=archetype, maindeck=maindeck, sideboard=sideboard
            )

        print(f'NotFoundPlayers:{self._not_found_players}')
