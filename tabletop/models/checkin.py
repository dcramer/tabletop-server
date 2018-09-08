from uuid import uuid4

from django.conf import settings
from django.db import models


class Checkin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.ForeignKey("tabletop.Game", on_delete=models.CASCADE)
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="tabletop.Player", related_name="checkins"
    )
    duration = models.PositiveIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        app_label = "tabletop"

    def __str__(self):
        return self.bottle.name
