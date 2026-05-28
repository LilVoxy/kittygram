from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Achievement, Cat

User = get_user_model()


class CatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )

    def test_unauthorized_request_returns_401(self):
        response = self.client.get('/api/cats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_can_list_cats(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_cat(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Мурзик', 'color': 'Gray', 'birth_year': 2020}
        response = self.client.post('/api/cats/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cat.objects.count(), 1)
        self.assertEqual(Cat.objects.first().name, 'Мурзик')

    def test_cat_owner_set_automatically(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Барсик', 'color': 'Black', 'birth_year': 2019}
        self.client.post('/api/cats/', data, format='json')
        cat = Cat.objects.first()
        self.assertEqual(cat.owner, self.user)

    def test_user_sees_only_own_cats(self):
        Cat.objects.create(name='Мой кот', color='Gray', birth_year=2020, owner=self.user)
        Cat.objects.create(name='Чужой кот', color='White', birth_year=2019, owner=self.other_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Мой кот')

    def test_invalid_birth_year_returns_400(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Дед', 'color': 'Gray', 'birth_year': 1900}
        response = self.client.post('/api/cats/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_cat(self):
        cat = Cat.objects.create(name='Барсик', color='Black', birth_year=2019, owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/cats/{cat.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cat.objects.count(), 0)


class AchievementAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_achievement(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Лучший кот'}
        response = self.client.post('/api/achievements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Achievement.objects.count(), 1)

    def test_list_achievements(self):
        Achievement.objects.create(name='Прыжок')
        Achievement.objects.create(name='Мурлыканье')
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
