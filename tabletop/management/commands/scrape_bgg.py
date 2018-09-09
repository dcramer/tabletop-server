import json
import os
from time import sleep

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

CACHE_ROOT = os.path.join(settings.CACHE_PATH, "bgg")
GAME_DETAILS_PATH = os.path.join(CACHE_ROOT, "game-details")
META_PATH = os.path.join(CACHE_ROOT, "meta.json")

FILE_HEADER = b'<boardgames termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">'


def cache_game_details(game_id):
    if not os.path.exists(GAME_DETAILS_PATH):
        os.makedirs(GAME_DETAILS_PATH)

    req = requests.get(
        "https://www.boardgamegeek.com/xmlapi/boardgame/{}".format(game_id)
    )
    content = req.content

    assert content.startswith(FILE_HEADER)

    cache_path = os.path.join(GAME_DETAILS_PATH, "{}.xml".format(game_id))
    with open(cache_path, "wb") as fp:
        fp.write(content)
    return content


class Command(BaseCommand):
    help = "Scrape BoardGameGeek for new games"

    def save_meta(self, meta):
        with open(META_PATH, "w") as fp:
            json.dump(meta, fp)

    def read_meta(self):
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as fp:
                try:
                    return json.load(fp)
                except json.JSONDecodeError:
                    pass
        return {}

    def handle(self, *args, **options):
        if not os.path.exists(CACHE_ROOT):
            os.makedirs(CACHE_ROOT)

        meta = self.read_meta()

        last_game_id = meta.get("last_game_id") or 0
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Beginning search at game_id={}".format(last_game_id)
            )
        )

        while True:
            last_game_id += 1
            self.stdout.write(
                self.style.SQL_FIELD("Retrieving game_id={}".format(last_game_id))
            )

            cache_game_details(last_game_id)
            meta["last_game_id"] = last_game_id
            self.save_meta(meta)
            sleep(1)
