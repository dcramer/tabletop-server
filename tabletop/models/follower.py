from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property


class Follower(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "tabletop"
        unique_together = (("from_user", "to_user"),)

    @cached_property
    def is_mutual(self):
        return (
            type(self)
            .objects.filter(to_user_id=self.from_user_id, from_user_id=self.to_user_id)
            .exists()
        )
