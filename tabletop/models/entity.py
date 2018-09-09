from uuid import uuid4

from django.conf import settings
from django.db import models
from enumfields import Enum, EnumField


class EntityType(Enum):
    publisher = "publisher"
    designer = "designer"
    artist = "artist"


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    type = EnumField(EntityType, max_length=32)
    name = models.CharField(max_length=128, unique=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("type", "name")
