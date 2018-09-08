from uuid import uuid4

from django.conf import settings
from django.db import models


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    checkin = models.ForeignKey("tabletop.Checkin", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    winner = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)
    tags = models.ManyToManyField("tabletop.Tag")
    rating = models.DecimalField(decimal_places=2, max_digits=5, null=True)
    confirmed = models.BooleanField(default=False)

    class Meta:
        app_label = "tabletop"
        unique_together = (("checkin", "user"),)
