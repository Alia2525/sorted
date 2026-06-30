
import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from .models import Article, Comment

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"

class ArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = "__all__"

class Query(graphene.ObjectType):
    articles = graphene.List(ArticleType, category=graphene.String(), title=graphene.String(), order_by=graphene.String())
    article = graphene.Field(ArticleType, id=graphene.Int(required=True))
    comments = graphene.List(CommentType)

    def resolve_articles(self, info, category=None, title=None, order_by=None):
        qs=Article.objects.all()
        if category:
            qs=qs.filter(category__iexact=category)
        if title:
            qs=qs.filter(title__icontains=title)
        allowed=["title","-title","created_at","-created_at","category","-category","id","-id"]
        if order_by in allowed:
            qs=qs.order_by(order_by)
        return qs

    def resolve_article(self, info, id):
        return Article.objects.get(pk=id)

    def resolve_comments(self, info):
        return Comment.objects.all()

class CreateArticle(graphene.Mutation):
    class Arguments:
        title=graphene.String(required=True)
        content=graphene.String(required=True)
        category=graphene.String(required=True)
    article=graphene.Field(ArticleType)
    @classmethod
    def mutate(cls, root, info, title, content, category):
        article=Article.objects.create(title=title,content=content,category=category,author=info.context.user)
        return cls(article=article)

class UpdateArticle(graphene.Mutation):
    class Arguments:
        id=graphene.Int(required=True)
        title=graphene.String()
        content=graphene.String()
        category=graphene.String()
    article=graphene.Field(ArticleType)
    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        a=Article.objects.get(pk=id)
        for k,v in kwargs.items(): setattr(a,k,v)
        a.save()
        return cls(article=a)

class DeleteArticle(graphene.Mutation):
    class Arguments: id=graphene.Int(required=True)
    success=graphene.Boolean()
    @classmethod
    def mutate(cls, root, info, id):
        Article.objects.filter(pk=id).delete()
        return cls(success=True)

class CreateComment(graphene.Mutation):
    class Arguments:
        article_id=graphene.Int(required=True)
        text=graphene.String(required=True)
    comment=graphene.Field(CommentType)
    @classmethod
    def mutate(cls, root, info, article_id, text):
        c=Comment.objects.create(article_id=article_id, text=text, author=info.context.user)
        return cls(comment=c)

class Mutation(graphene.ObjectType):
    create_article=CreateArticle.Field()
    update_article=UpdateArticle.Field()
    delete_article=DeleteArticle.Field()
    create_comment=CreateComment.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema=graphene.Schema(query=Query, mutation=Mutation)
