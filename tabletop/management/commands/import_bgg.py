import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from lxml import etree

from tabletop.models import Entity, Game, GameEntity
from tabletop.utils.bgg import GAME_DETAILS_PATH, parse_game_details


class Command(BaseCommand):
    help = "Import any games in the BoardGameGeek cache"

    def handle(self, *args, **options):
        if not os.path.exists(GAME_DETAILS_PATH):
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "No cached data in {}".format(GAME_DETAILS_PATH)
                )
            )
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Beginning import from {}".format(GAME_DETAILS_PATH)
            )
        )

        for root, dirs, files in os.walk(GAME_DETAILS_PATH):
            for fn in files:
                if not fn.endswith(".xml"):
                    self.stdout.write(self.style.ERROR("Unknown file: {}".format(fn)))
                    continue

                self.stdout.write(
                    self.style.SQL_FIELD("Processing file: {}".format(fn))
                )

                with open(os.path.join(root, fn), "rb") as fp:
                    tree = etree.fromstring(fp.read())

                details = parse_game_details(tree)

                game = Game.objects.filter(
                    Q(bgg_id=details["bgg_id"]) | Q(name__iexact=details["name"])
                ).first()
                if not game:
                    with transaction.atomic():
                        game = Game.objects.create(
                            name=details["name"],
                            bgg_id=details["bgg_id"],
                            min_players=details["min_players"],
                            max_players=details["max_players"],
                            duration=details["duration"],
                            duration_type=details["duration_type"],
                            year_published=details["year_published"],
                        )
                        for entity in details["entities"]:
                            GameEntity.objects.create(
                                entity=Entity.objects.get_or_create(
                                    name=entity["name"]
                                )[0],
                                game=game,
                                type=entity["type"],
                            )
                    self.stdout.write(
                        self.style.SQL_FIELD("Created <Game: id={}>".format(game.id))
                    )
                else:
                    if not game.bgg_id:
                        game.bgg_id = details["bgg_id"]
                        game.save(update_fields=["bgg_id"])
