import tempfile
import os

from PIL import Image

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


def image_upload_url(book_id):
    """本の画像をアップロードするためのURLを返す"""
    return reverse('book:book-upload-image', args=[book_id])


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

    def test_create_basic_book(self):
        """本を作成するテスト"""
        payload = {
            'title': 'Test book',
            'price': 10.00,
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_with_tags(self):
        """本とタグを作成する"""
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test book with two tags',
            'tags': [tag1.id, tag2.id],
            'price': 10.00
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        tags = book.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_recipe(self):
        """パッチで本を更新するテスト"""
        book = sample_book(user=self.user)
        book.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='science')

        payload = {'title': 'math book', 'tags': [new_tag.id]}
        url = detail_url(book.id)
        self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        tags = book.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_book(self):
        """PUTで本を全て更新するテスト"""
        book = sample_book(user=self.user)
        book.tags.add(sample_tag(user=self.user))

        payload = {
                'title': 'Spaghetti carbonara',
                'price': 5.00
            }
        url = detail_url(book.id)
        self.client.put(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.price, payload['price'])
        tags = book.tags.all()
        self.assertEqual(len(tags), 0)


class BookImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.book = sample_book(user=self.user)

    def tearDown(self):
        self.book.image.delete()

    def test_upload_image_to_book(self):
        """Bookへの画像のアップロードのテスト"""
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_image_bad_request(self):
        """無効なイメージがアップロードされた時のテスト"""
        url = image_upload_url(self.book.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
