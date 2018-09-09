from uuid import uuid4

from django.db import models


class GameImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.OneToOneField(
        "tabletop.Game", on_delete=models.CASCADE, related_name="image"
    )
    file = models.ImageField(
        upload_to="game-images/%Y/%m/%d/",
        null=True,
        width_field="width",
        height_field="height",
    )
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
