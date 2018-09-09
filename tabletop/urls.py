from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from tabletop.views import EnhancedGraphQLView

urlpatterns = [
    path("graphql/", csrf_exempt(EnhancedGraphQLView.as_view(graphiql=settings.DEBUG)))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
