import os
import tempfile

import requests
from django.core import files
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from lxml import etree

from tabletop.models import Entity, Game, GameEntity, GameImage
from tabletop.utils.bgg import GAME_DETAILS_PATH, parse_game_details


def save_game(details):
    game = (
        Game.objects.filter(
            Q(bgg_id=details["bgg_id"]) | Q(name__iexact=details["name"])
        )
        .select_related("image")
        .first()
    )
    if not game:
        created = True
        with transaction.atomic():
            game = Game.objects.create(
                name=details["name"],
                bgg_id=details["bgg_id"],
                min_players=details["min_players"],
                max_players=details["max_players"],
                duration=details["duration"],
                duration_type=details["duration_type"],
                year_published=details["year_published"],
                parent=details["parent"],
            )
            for entity in details["entities"]:
                GameEntity.objects.create(
                    entity=Entity.objects.get_or_create(name=entity["name"])[0],
                    game=game,
                    type=entity["type"],
                )
    else:
        created = False
        if not game.bgg_id:
            game.bgg_id = details["bgg_id"]
            game.save(update_fields=["bgg_id"])
        if details["parent"] and not game.parent:
            game.parent = details["parent"]
            game.save(update_fields=["parent"])

    if details["image_url"]:
        try:
            game.image
        except Game.image.RelatedObjectDoesNotExist:
            req = requests.get(details["image_url"])
            tmp = tempfile.NamedTemporaryFile()
            for chunk in req.iter_content(1024 * 8):
                if not chunk:
                    break
                tmp.write(chunk)
            image = GameImage(game=game)
            image.file.save(
                "{}.{}".format(str(game.id), details["image_url"].rsplit(".", 1)[-1]),
                files.File(tmp),
            )

    return game, created


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

        for root, _, file_list in os.walk(GAME_DETAILS_PATH):
            for fn in file_list:
                if not fn.endswith(".xml"):
                    self.stdout.write(self.style.ERROR("Unknown file: {}".format(fn)))
                    continue

                self.stdout.write(
                    self.style.SQL_FIELD("Processing file: {}".format(fn))
                )

                with open(os.path.join(root, fn), "rb") as fp:
                    tree = etree.fromstring(fp.read())

                details = parse_game_details(tree)

                game, created = save_game(details)
                if created:
                    self.stdout.write(
                        self.style.SQL_FIELD("Created <Game: id={}>".format(game.id))
                    )
