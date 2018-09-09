import os
import sys

import pytest
from lxml import etree

from tabletop.models import EntityType

from .bgg import parse_game_details


@pytest.fixture
def sample_bgg_game_details():
    with open(
        os.path.join(
            os.path.dirname(sys.modules["tabletop"].__file__),
            "fixtures",
            "bgg-game-details.xml",
        ),
        "r",
    ) as fp:
        return etree.fromstring(fp.read())


def test_parse_game_details(sample_bgg_game_details):
    result = parse_game_details(sample_bgg_game_details)
    assert result["name"] == "Hexpack"
    assert result["year_published"] == 2008
    assert len(result["entities"]) == 6
    assert {"name": "Blue Panther", "type": EntityType.publisher} in result["entities"]
    assert {"name": "(Public Domain)", "type": EntityType.publisher} in result[
        "entities"
    ]
    assert {"name": "Nathan Morse", "type": EntityType.designer} in result["entities"]
    assert {"name": "Nathan Morse", "type": EntityType.artist} in result["entities"]
    assert {"name": "Daniel Wilcox", "type": EntityType.designer} in result["entities"]
    assert {"name": "Daniel Wilcox", "type": EntityType.artist} in result["entities"]
