from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Article, Comment
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import ArticleSerializer, CommentSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related("author").prefetch_related(
        "comments__author"
    )
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "content"]
    filterset_fields = ["category", "author"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("article", "author")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ["article", "author"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
