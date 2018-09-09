import os

import requests
from django.conf import settings

from tabletop.models import DurationType, EntityType

CACHE_ROOT = os.path.join(settings.CACHE_PATH, "bgg")

GAME_DETAILS_PATH = os.path.join(CACHE_ROOT, "game-details")

META_PATH = os.path.join(CACHE_ROOT, "meta.json")

FILE_HEADER = b'<boardgames termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">'

ERROR_MESSAGE = b'<error message="Item not found"/>'


class UnknownGame(Exception):
    pass


def coerce_posint(value):
    if not value:
        return None
    value = int(value)
    if value <= 0:
        return None
    return value


def cache_game_details(game_id):
    if not os.path.exists(GAME_DETAILS_PATH):
        os.makedirs(GAME_DETAILS_PATH)

    req = requests.get(
        "https://www.boardgamegeek.com/xmlapi/boardgame/{}".format(game_id)
    )
    content = req.content

    assert content.startswith(FILE_HEADER)
    if ERROR_MESSAGE in content:
        raise UnknownGame

    cache_path = os.path.join(GAME_DETAILS_PATH, "{}.xml".format(game_id))
    with open(cache_path, "wb") as fp:
        fp.write(content)
    return content


def parse_game_details(tree):
    assert tree.tag == "boardgames"

    game = list(tree.iter("boardgame"))[0]

    entities = []
    for node in game.iter("boardgamepublisher"):
        entities.append({"name": node.text, "type": EntityType.publisher})
    for node in game.iter("boardgameartist"):
        entities.append({"name": node.text, "type": EntityType.artist})
    for node in game.iter("boardgamedesigner"):
        entities.append({"name": node.text, "type": EntityType.designer})

    year_published = game.xpath("yearpublished")[0].text
    if year_published:
        year_published = int(year_published)
        if (
            year_published <= 1900 or year_published > 2025
        ):  # we ignore things like "3000 bc" because lol
            year_published = None

    return {
        "bgg_id": int(game.get("objectid")),
        "name": game.xpath("name[@primary='true']")[0].text,
        "year_published": year_published,
        "min_players": coerce_posint(game.xpath("minplayers")[0].text),
        "max_players": coerce_posint(game.xpath("maxplayers")[0].text),
        "entities": entities,
        # bgg doesn't understand "per player" duration estimates
        "duration": coerce_posint(game.xpath("playingtime")[0].text),
        "duration_type": DurationType.total,
    }
