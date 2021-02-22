from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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


class BookViewSet(viewsets.ModelViewSet):
    """データベース内の本を管理する"""
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Bookに画像をアップロードする"""
        book = self.get_object()
        serializer = self.get_serializer(
            book,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        """認証されたユーザーの本を取得する"""
        tags = self.request.query_params.get('tags')
        queryset = self.queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """適切なシリアライザークラスを返す"""
        if self.action == 'retrieve':
            return serializers.BookDetailSerializer
        elif self.action == 'upload_image':
            return serializers.BookImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """新しい本を作成する"""
        serializer.save(user=self.request.user)
