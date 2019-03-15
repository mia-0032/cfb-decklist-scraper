# -*- coding: utf-8 -*-

import scrapy
import re

from bs4 import BeautifulSoup

from cfb_decklist_scraper.items import Deck


class GroundPrixLosAngels2019Spider(scrapy.Spider):
    name = 'ground_prix_los_angels_2019'

    PLAYER_NAME_MAPPING = {
        # cfb decklist => standings
        'Jay Trojan': 'Joseph Trojan',
        'Franky Rodriguez': 'Francisco Rodriguez',
        'Dan Besterman': 'Daniel Besterman',
    }

    def start_requests(self):
        urls = [
            'https://magic.wizards.com/en/events/coverage/gplosangeles19/final-standings',
            'https://www.channelfireball.com/grand-prix-los-angeles-top-8-decklists/',
            'https://www.channelfireball.com/grand-prix-los-angeles-top-32-deck-lists/',
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
            name = ' '.join(name).title()

            self._standings[name] = {'rank': rank, 'point': point}

    def _parse_decklist(self, soup):
        post_content = soup.find('div', class_='postContent')

        builders = post_content.find_all('h3')

        self._not_found_players = []

        for builder in builders:
            player_name = builder.get_text().title()

            if player_name in ['', 'Discussion']:
                continue

            if player_name in self.PLAYER_NAME_MAPPING:
                player_name = self.PLAYER_NAME_MAPPING[player_name]

            deck_content = builder.find_next('div').find('div', class_='plain-text-decklist').find('pre').get_text()

            deck_contents = deck_content.split('Sideboard', 1)
            maindeck = deck_contents[0]
            sideboard = deck_contents[1] if len(deck_contents) == 2 else ''

            maindeck = [l.split(' ', 1) for l in maindeck.strip().split('\r\n')]
            maindeck = {l[1]: int(l[0]) for l in maindeck}

            # sideboard may be empty
            sideboard = [l.split(' ', 1) for l in [x for x in sideboard.strip().split('\r\n') if x]]
            sideboard = {l[1]: int(l[0]) for l in sideboard}

            archetype = None
            standing = self._standings.get(player_name, {'rank': None, 'point': None})

            if player_name not in self._standings:
                self._not_found_players.append(player_name)

            yield Deck(
                player_name=player_name, rank=standing['rank'], point=standing['point'],
                archetype=archetype, maindeck=maindeck, sideboard=sideboard
            )

        print(f'NotFoundPlayers:{self._not_found_players}')
