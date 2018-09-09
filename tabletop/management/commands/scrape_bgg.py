import json
import os
from time import sleep

from django.core.management.base import BaseCommand

from tabletop.utils.bgg import CACHE_ROOT, cache_game_details

META_PATH = os.path.join(CACHE_ROOT, "meta.json")


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
