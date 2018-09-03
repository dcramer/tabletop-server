from uuid import uuid4

from django.conf import settings
from django.db import models


class CheckIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="activity.Player", related_name="checkins"
    )
    duration = models.PositiveIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.bottle.name


class Player(models.Model):
    checkin = models.ForeignKey(CheckIn, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    winner = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)
    tags = models.ManyToManyField("games.Tag")
    rating = models.DecimalField(decimal_places=2, max_digits=5, null=True)
    confirmed = models.BooleanField(default=False)
