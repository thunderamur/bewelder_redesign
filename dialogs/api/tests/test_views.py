from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from dialogs.models import Dialog, Membership, Message

User = get_user_model()


class DialogViewAPITestCase(APITestCase):
    url = reverse('dialogs_api:dialog_list')

    def setUp(self):
        self.dialog = mixer.blend(Dialog)
        self.creator, self.opponent = mixer.cycle(2).blend(User)
        mixer.blend(Membership, dialog=self.dialog, user=self.creator, is_creator=True)
        mixer.blend(Membership, dialog=self.dialog, user=self.opponent)

    def test_dialogs_list_url_exists(self):
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_dialog_list(self):
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.opponent)
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['id'], self.dialog.pk)

    def test_post_dialog_list(self):
        creator, opponent = mixer.cycle(2).blend(User)

        data = {
            'opponent': opponent.pk,
            'vacancy': None,
            'theme': 'Предложение',
            'text': 'Xотим вас нанять',
        }

        self.client.force_login(creator)
        resp = self.client.post(self.url, data=data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('theme'), data['theme'])
        created_msg = Message.objects.first()
        self.assertEqual(created_msg.user, creator)
        self.assertEqual(created_msg.text, data['text'])

    def test_post_message(self):

        url = reverse('dialogs_api:dialog_detail', kwargs={'pk': self.dialog.pk})
        msg = {'text': 'Hello world'}

        resp = self.client.post(url, data=msg, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.creator)
        resp = self.client.post(url, data=msg, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
