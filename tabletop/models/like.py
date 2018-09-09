from uuid import uuid4

from django.conf import settings
from django.db import models


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    checkin = models.ForeignKey("tabletop.Checkin", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        app_label = "tabletop"
        unique_together = (("checkin", "created_by"),)
