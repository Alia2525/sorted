from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, Comment


class ArticlePermissionsTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="pass12345",
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass12345",
        )
        self.article = Article.objects.create(
            title="Original title",
            content="Article content",
            category="Django",
            author=self.author,
        )
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.other_user,
            text="Nice article",
        )

    def test_anonymous_user_can_read_articles(self):
        response = self.client.get(reverse("article-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["comments"][0]["text"], "Nice article")

    def test_anonymous_user_cannot_create_article(self):
        response = self.client.post(
            reverse("article-list"),
            {"title": "New", "content": "Text", "category": "API"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_update_own_article(self):
        self.client.force_authenticate(self.author)
        response = self.client.patch(
            reverse("article-detail", args=[self.article.id]),
            {"title": "Updated title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated title")

    def test_other_user_cannot_update_article(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.patch(
            reverse("article-detail", args=[self.article.id]),
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_delete_article(self):
        self.client.force_authenticate(self.author)
        response = self.client.delete(reverse("article-detail", args=[self.article.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_article(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(reverse("article-detail", args=[self.article.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(
            reverse("comment-list"),
            {"article": self.article.id, "text": "Second comment"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.other_user.username)

    def test_other_user_cannot_update_comment(self):
        self.client.force_authenticate(self.author)
        response = self.client.patch(
            reverse("comment-detail", args=[self.comment.id]),
            {"text": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_comment(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(reverse("comment-detail", args=[self.comment.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
