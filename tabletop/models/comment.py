from uuid import uuid4

from django.conf import settings
from django.db import models


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    checkin = models.ForeignKey(
        "tabletop.Checkin", on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        app_label = "tabletop"
