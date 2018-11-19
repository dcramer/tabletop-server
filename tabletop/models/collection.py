from uuid import uuid4

from django.conf import settings
from django.db import models


class CollectionGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    collection = models.ForeignKey("tabletop.Collection", on_delete=models.CASCADE)
    game = models.ForeignKey("tabletop.Game", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "tabletop"
        unique_together = (("collection", "game"),)


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    games = models.ManyToManyField(
        "tabletop.Game", through=CollectionGame, related_name="collections"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        app_label = "tabletop"
        unique_together = (("name", "created_by"),)

    def __str__(self):
        return self.name
