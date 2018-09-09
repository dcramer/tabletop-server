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


def test_parse_game_details(db, sample_bgg_game_details):
    result = parse_game_details(sample_bgg_game_details)
    assert result["bgg_id"] == 167791
    assert result["name"] == "Terraforming Mars"
    assert result["year_published"] == 2016
    assert len(result["entities"]) == 18
    assert {"name": "FryxGames", "type": EntityType.publisher} in result["entities"]
