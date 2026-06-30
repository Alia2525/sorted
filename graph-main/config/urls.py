from django.urls import path
from graphene_django.views import GraphQLView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from articles.views import ArticleViewSet, CommentViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="article")
router.register("comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("authentication.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('graphql/', GraphQLView.as_view(graphiql=True))]
