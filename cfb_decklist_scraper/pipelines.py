# -*- coding: utf-8 -*-

import json

from .items import Deck, Standing


class CfbDecklistScraperPipeline(object):
    def __init__(self):
        self.standing = open('standing.json', 'w')
        self.archetype = open('archetype.json', 'w')
        self.decklist = open('decklist.json', 'w')
        self.match_result = open('match_result.json', 'w')

    def process_item(self, item, spider):
        if isinstance(item, Standing):
            return self._process_standing(item)
        elif isinstance(item, Deck):
            return self._process_deck(item)
        else:
            return self._process_result(item)

    def _process_standing(self, item):
        row = {
            'player': item['player'], 'rank': item['rank'], 'point': item['point']
        }
        self.standing.write(json.dumps(row) + '\n')
        return item

    def _process_deck(self, item):
        self.archetype.write(
            json.dumps({'player': item['player'], 'archetype': item['archetype']}) + '\n'
        )

        for c, n in item['maindeck'].items():
            self._append_deck(item, c, n, False)
        for c, n in item['sideboard'].items():
            self._append_deck(item, c, n, True)

        return item

    def _process_result(self, item):
        row = {
            'win_player': item['win_player'], 'lose_player': item['lose_player']
        }
        self.match_result.write(json.dumps(row) + '\n')
        return item

    def _append_deck(self, deck: Deck, card_name, num, is_sideboard):
        row = {
            'player': deck['player'],
            'card_name': card_name,
            'num': num,
            'is_sideboard': is_sideboard,
        }
        self.decklist.write(json.dumps(row) + '\n')

    def __del__(self):
        self.standing.close()
        self.archetype.close()
        self.decklist.close()
        self.match_result.close()
