from uuid import uuid4

from django.conf import settings
from django.db import models
from enumfields import Enum, EnumField


class DurationType(Enum):
    total = "total"
    per_player = "per_player"


class EntityType(Enum):
    publisher = "publisher"
    designer = "designer"
    artist = "artist"


class GameEntity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    entity = models.ForeignKey("tabletop.Entity", on_delete=models.CASCADE)
    game = models.ForeignKey("tabletop.Game", on_delete=models.CASCADE)
    type = EnumField(EntityType, max_length=32)

    class Meta:
        app_label = "tabletop"
        unique_together = (("game", "type"),)


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True)
    confirmed = models.BooleanField(default=False)
    min_players = models.PositiveIntegerField(null=True)
    max_players = models.PositiveIntegerField(null=True)
    # suggested duration in minutes
    duration = models.PositiveIntegerField(null=True)
    duration_type = EnumField(DurationType, max_length=32, null=True)
    year_published = models.PositiveSmallIntegerField(null=True)
    entities = models.ManyToManyField("tabletop.Entity", through=GameEntity)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        app_label = "tabletop"

    def __str__(self):
        return self.name
