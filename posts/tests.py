from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='derek', password='derekg')

    def test_can_list_posts(self):
        derek = User.objects.get(username='derek')
        Post.objects.create(owner=derek, title='a title')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print(len(response.data))

    def test_logged_in_user_can_create_post(self):
        self.client.login(username='derek', password='derekg')
        response = self.client.post('/posts/', {'title': 'a title'})
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_create_post(self):
        response = self.client.post('/posts/', {'title': 'no way Jose'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTests(APITestCase):
    def setUp(self):
        derek = User.objects.create_user(username='derek', password='derekg')
        adam = User.objects.create_user(username='adam', password='adamp')
        Post.objects.create(
            owner=derek, title='Dereks Title', content='Derek\'s content'
        )
        Post.objects.create(
            owner=adam, title='Adams Title', content='Adams Content'
        )

    def test_can_retrieve_post_valid_id(self):
        response = self.client.get('/posts/1/')
        self.assertEqual(response.data['title'], 'Dereks Title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_post_invalid_id(self):
        response = self.client.get('/posts/199/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_post(self):
        self.client.login(username='derek', password='derekg')
        response = self.client.put('/posts/1/', {'title': 'a new title'})
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(post.title, 'a new title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_posts_they_dont_own(self):
        self.client.login(username='adam', password='adamp')
        response = self.client.put('/posts/1/', {'title': 'A brand new title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
