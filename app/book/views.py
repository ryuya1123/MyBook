from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Book

from book import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 ):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """現在認証されているユーザーのオブジェクトを返す"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)


class BookViewSet(viewsets.ModelViewSet):
    """データベース内の本を管理する"""
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """認証されたユーザーの本を取得する"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """適切なシリアライザークラスを返す"""
        if self.action == 'retrieve':
            return serializers.BookDetailSerializer

        return self.serializer_class
