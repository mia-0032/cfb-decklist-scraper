# -*- coding: utf-8 -*-

import scrapy
import re

from bs4 import BeautifulSoup

from cfb_decklist_scraper.items import Deck, MatchResult, Standing


class GroundPrixLosAngels2019Spider(scrapy.Spider):
    name = 'ground_prix_los_angels_2019'

    PLAYER_NAME_MAPPING = {
        # cfb decklist => standings
        'Jay Trojan': 'Joseph Trojan',
        'Franky Rodriguez': 'Francisco Rodriguez',
        'Dan Besterman': 'Daniel Besterman',
    }

    def start_requests(self):
        urls = {
            # standings
            'https://magic.wizards.com/en/events/coverage/gplosangeles19/final-standings',
            # deck lists
            'https://www.channelfireball.com/grand-prix-los-angeles-top-8-decklists/',
            'https://www.channelfireball.com/grand-prix-los-angeles-top-32-deck-lists/',
            'https://www.channelfireball.com/grand-prix-los-angeles-day-2-deck-lists/',
            # match results
            'http://coverage.channelfireball.com/assets/prs/5c7c8ec5d43a8840156160.html',  # 15
            'http://coverage.channelfireball.com/assets/prs/5c7c571e0bd76663093203.html',  # 14
            'http://coverage.channelfireball.com/assets/prs/5c7c56f9d445b623225843.html',  # 13
            'http://coverage.channelfireball.com/assets/prs/5c7c4e190afa8194782742.html',  # 12
            'http://coverage.channelfireball.com/assets/prs/5c7c4466d1459405328500.html',  # 11
            'http://coverage.channelfireball.com/assets/prs/5c7c44314a321691346322.html',  # 10
            'http://coverage.channelfireball.com/assets/prs/5c7b65de5fe9a186897650.html',  # 9
            'http://coverage.channelfireball.com/assets/prs/5c7b439c47764663093956.html',  # 8
            'http://coverage.channelfireball.com/assets/prs/5c7b30e3033fc196233044.html',  # 7
            'http://coverage.channelfireball.com/assets/prs/5c7b30bea7276502347142.html',  # 6
            'http://coverage.channelfireball.com/assets/prs/5c7b0fa2422ae155047156.html',  # 5
            'http://coverage.channelfireball.com/assets/prs/5c7b01f5f1170139562696.html',  # 4
            'http://coverage.channelfireball.com/assets/prs/5c7b01d53c588150769879.html',  # 3
            'http://coverage.channelfireball.com/assets/prs/5c7b01b4575c5654160931.html',  # 2
            'http://coverage.channelfireball.com/assets/prs/5c7ac94edf2af749364639.html',  # 1
        }

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        domain = response.url.split("/")[2]
        soup = BeautifulSoup(response.text, 'lxml')

        if domain == 'magic.wizards.com':
            return self._parse_standings(soup)
        elif domain == 'www.channelfireball.com':
            return self._parse_decklist(soup)
        else:
            return self._parse_results(soup)

    def _parse_standings(self, soup):
        table = soup.find('div', id='content-detail-page-of-an-article')

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

            yield Standing(player=name, rank=rank, point=point)

    def _parse_decklist(self, soup):
        post_content = soup.find('div', class_='postContent')

        builders = post_content.find_all('h3')

        for builder in builders:
            player = builder.get_text().title()

            if player in ['', 'Discussion']:
                continue

            if player in self.PLAYER_NAME_MAPPING:
                player = self.PLAYER_NAME_MAPPING[player]

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

            yield Deck(
                player=player, archetype=archetype, maindeck=maindeck, sideboard=sideboard
            )

    def _parse_results(self, soup):
        table = soup.find('table')

        def _format_name(name: str):
            name = name.strip().split(', ')
            name.reverse()
            name = ' '.join(name).title()
            return name

        for tr in table.find_all('tr'):
            tds = tr.find_all('td')

            if len(tds) == 0:
                continue

            result = tds[3].get_text()

            if 'Draw' in result:
                continue

            player = _format_name(tds[1].get_text())
            opponent = _format_name(tds[5].get_text())

            if 'Won' in result:
                yield MatchResult(win_player=player, lose_player=opponent)
            else:
                yield MatchResult(win_player=opponent, lose_player=player)
