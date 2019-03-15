# -*- coding: utf-8 -*-

import json

from .items import Deck


class CfbDecklistScraperPipeline(object):
    def __init__(self):
        self.output = open('decklist.json', 'w')

    def process_item(self, item: Deck, spider) -> Deck:
        for c, n in item['maindeck'].items():
            self._append_row(item, c, n, False)
        for c, n in item['sideboard'].items():
            self._append_row(item, c, n, True)

        return item

    def _append_row(self, deck: Deck, card_name, num, is_sideboard):
        row = {
            'player_name': deck['player_name'],
            'archetype': deck['archetype'],
            'rank': deck['rank'],
            'point': deck['point'],
            'card_name': card_name,
            'num': num,
            'is_sideboard': is_sideboard,
        }
        self.output.write(json.dumps(row) + '\n')

    def __del__(self):
        self.output.close()
