from uuid import uuid4

from django.conf import settings
from django.db import models


class GameRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.ForeignKey(
        "tabletop.Game", on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rated_games"
    )
    rating = models.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        app_label = "tabletop"
        unique_together = (("game", "user"),)
