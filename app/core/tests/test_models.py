from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from core import models


def sample_user(email='test@example.com', password='testpass'):
    """サンプルユーザーの作成"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """新しいemailとUserを作るテスト"""
        email = 'test@example.com'
        password = 'Testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """新しいユーザーの電子メールが正規化されているかのテスト"""
        email = 'test@EXAMPLE.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """メールなしでユーザを作成するテストでエラーが発生する"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """スーパーユーザーを作成するテスト"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """タグ文字列の列表現のテスト"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='book'
        )

        self.assertEqual(str(tag), tag.name)

    def test_book_str(self):
        """本の文字列表現のテスト"""
        book = models.Book.objects.create(
            user=sample_user(),
            title='test book title',
            price=5.00,
        )

        self.assertEqual(str(book), book.title)

    @patch('uuid.uuid4')
    def test_book_file_name_uuid(self, mock_uuid):
        """画像が正しい場所に保存されているかのテスト"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.book_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/book/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
