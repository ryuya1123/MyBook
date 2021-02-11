from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Book, Tag

from book.serializers import BookSerializer, BookDetailSerializer


BOOKS_URL = reverse('book:book-list')


def sample_tag(user, name='Main book'):
    """サンプルタグを作成し返す"""
    return Tag.objects.create(user=user, name=name)


def detail_url(book_id):
    """本の詳細のURLを返す"""
    return reverse('book:book-detail', args=[book_id])


def sample_book(user, **params):
    """サンプルBookを作り返す"""
    defaults = {
        'title': 'Sample book',
        'price': 5.00,
    }
    defaults.update(params)

    return Book.objects.create(user=user, **defaults)


class PublicBookApiTests(TestCase):
    """認証されていない本のAPIアクセスのテスト"""

    def setUp(self):
        self.client = APIClient()

    def book_required_auth(self):
        """認証が必要であることのテスト"""
        res = self.client.get(BOOKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBOOKApiTests(TestCase):
    """認証されたBOOKAPIのアクセスをテスト"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_books(self):
        """Test retrieving list of recipes"""
        sample_book(user=self.user)
        sample_book(user=self.user)

        res = self.client.get(BOOKS_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_books_limited_to_user(self):
        """ユーザーの本を取得するテスト"""
        user2 = get_user_model().objects.create_user(
            'other@example.com',
            'pass'
        )
        sample_book(user=user2)
        sample_book(user=self.user)

        res = self.client.get(BOOKS_URL)

        books = Book.objects.filter(user=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_book_detail(self):
        """本の詳細を表示する"""
        book = sample_book(user=self.user)
        book.tags.add(sample_tag(user=self.user))

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.data, serializer.data)
