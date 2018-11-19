from django.apps import AppConfig
from django.db.models.signals import post_save


class AppConfig(AppConfig):
    name = "tabletop"

    def ready(self):
        Collection = self.get_model("Collection")
        User = self.get_model("User")

        def create_default_collection(instance, created, **kwargs):
            if not created:
                return

            Collection.objects.create(
                name="My Games",
                description="My personal collection of games",
                created_by=instance,
                is_default=True,
            )

        post_save.connect(create_default_collection, sender=User, weak=False)
