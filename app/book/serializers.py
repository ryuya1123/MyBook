from rest_framework import serializers

from core.models import Tag, Book


class TagSerializer(serializers.ModelSerializer):
    """タグオブジェクトのためのシリアライザー"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class BookSerializer(serializers.ModelSerializer):
    """Bookシリアライザー"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'tags', 'price',
            'link',
        )
        read_only_fields = ('id',)


class BookDetailSerializer(BookSerializer):
    tags = TagSerializer(many=True, read_only=True)
