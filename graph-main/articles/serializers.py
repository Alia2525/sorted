from rest_framework import serializers

from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "article", "author", "text", "created_at"]
        read_only_fields = ["id", "author", "created_at"]


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "category",
            "author",
            "created_at",
            "comments",
        ]
        read_only_fields = ["id", "author", "created_at"]
