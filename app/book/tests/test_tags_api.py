from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from book.serializers import TagSerializer


TAGS_URL = reverse('book:tag-list')


class PublicTagApiTests(TestCase):
    """公開されているタグAPIのテスト"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """タグを取得するにはログインが必要であることをテスト"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """許可されたユーザータグAPIのテスト"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """タグの取得をテスト"""
        Tag.objects.create(user=self.user, name='test book')
        Tag.objects.create(user=self.user, name='test book1')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """返されたタグが認証されたユーザーのものであることを確認するテスト"""
        user2 = get_user_model().objects.create_user(
            'other@example.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='book2')
        tag = Tag.objects.create(user=self.user, name='book3')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
