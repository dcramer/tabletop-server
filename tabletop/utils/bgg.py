import os

import requests
from django.conf import settings
from lxml import etree

from tabletop.models import EntityType

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


def get_game_details(game_id):
    cache_path = os.path.join(GAME_DETAILS_PATH, "{}.xml".format(game_id))
    with open(cache_path, "rb") as fp:
        root = etree.fromstring(fp.read())

    return parse_game_details(root)


def parse_game_details(tree):
    assert tree.tag == "boardgames"

    game = list(tree.iter("boardgame"))[0]

    entities = []
    for node in game.xpath("boardgamepublisher"):
        entities.append({"name": node.text, "type": EntityType.publisher})
    for node in game.xpath("boardgameartist"):
        entities.append({"name": node.text, "type": EntityType.artist})
    for node in game.xpath("boardgamedesigner"):
        entities.append({"name": node.text, "type": EntityType.designer})

    return {
        "name": game.xpath("name")[0].text,
        "year_published": int(game.xpath("yearpublished")[0].text),
        "entities": entities,
    }
