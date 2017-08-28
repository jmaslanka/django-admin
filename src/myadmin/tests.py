from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase

from myadmin.models import AdminPanel


class CustomAdminPanelModelTestCase(TestCase):
    def setUp(self):
        self.panel1 = AdminPanel.objects.create(models_text='Short text')
        self.panel2 = AdminPanel.objects.create(
            models_text="""
                Very Long Text. Very Long Text.
                Very Long Text. Very Long Text.
                Very Long Text. Very Long Text.
                Very Long Text. Very Long Text.
                Very Long Text. Very Long Text.
                Very Long Text. Very Long Text.
            """
        )

    def test_methods(self):
        self.assertEqual(self.panel1.__str__(), 'Models:Short text')
        self.assertEqual(
            self.panel2.__str__(),
            """Models:
                Very Long Text. Very Long Text.
                Very Long Text."""
        )


class CustomAdminPanelTestView(TestCase):
    def setUp(self):
        self.access_perm = Permission.objects.get(codename='access_panel')
        self.user_add_perm = Permission.objects.get(codename='add_user')
        self.user_edit_perm = Permission.objects.get(codename='change_user')
        self.user_delete_perm = Permission.objects.get(codename='delete_user')

        self.access_user = User.objects.create_user('log1', 'a@a.a', 'qw12')
        self.no_access_user = User.objects.create_user(
            'log2', 'bbb@bbb.com', 'qw12', first_name='Max'
        )
        self.access_user.user_permissions.add(
            self.access_perm, self.user_add_perm
        )

    def test_access(self):
        # No access to all pages within panel
        self.client.force_login(self.no_access_user)
        response = self.client.get(reverse('myadmin:panel'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse('myadmin:objects', kwargs={'model_name': 'auth.User'})
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse('myadmin:create', kwargs={'model_name': 'auth.User'})
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse('myadmin:delete', kwargs={
                'model_name': 'auth.User', 'obj_pk': 1
            })
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse('myadmin:edit', kwargs={
                'model_name': 'auth.User', 'obj_pk': 1
            })
        )
        self.assertEqual(response.status_code, 403)

        # Access to panel, adding user and unsuccessful to others
        self.client.force_login(self.access_user)
        response = self.client.get(reverse('myadmin:panel'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('myadmin:create', kwargs={'model_name': 'auth.User'})
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('myadmin:delete', kwargs={
                'model_name': 'auth.User', 'obj_pk': 2
            })
        )
        self.assertEqual(response.status_code, 403)

    def test_selecting_model(self):
        self.client.force_login(self.access_user)
        # adding models to panel
        response = self.client.post(reverse('myadmin:panel'), data={
            'add': ['Add'], 'select_models': ['1', '3']
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['models_view']), 2)
        model_name = response.context['models_view'][1][0]
        # deleting models from panel
        response = self.client.post(reverse('myadmin:panel'), data={
            'remove': ['Remove'], 'remove_models': ['0']
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['models_view']), 1)
        self.assertEqual(response.context['models_view'][0][0], model_name)

    def test_objects_list(self):
        self.client.force_login(self.access_user)
        response = self.client.get(reverse(
            'myadmin:objects', kwargs={'model_name': 'auth.User'}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['object_list']),
            [self.access_user, self.no_access_user]
        )

    def test_adding_object(self):
        self.client.force_login(self.access_user)
        self.assertFalse(User.objects.filter(username='login651').exists())
        response = self.client.post(
            reverse('myadmin:create', kwargs={'model_name': 'auth.User'}),
            data={
                'username': 'login651', 'password': 'Passw0rd123',
                'date_joined': '2017-08-20 18:00:00'
            }
        )
        self.assertRedirects(response, reverse(
            'myadmin:objects', kwargs={'model_name': 'auth.User'}
        ))
        self.assertTrue(User.objects.filter(username='login651').exists())

    def test_editing_object(self):
        self.client.force_login(self.access_user)
        self.access_user.user_permissions.add(self.user_edit_perm)
        self.assertEqual(self.no_access_user.first_name, 'Max')
        response = self.client.get(
            reverse('myadmin:edit', kwargs={
                'model_name': 'auth.User', 'obj_pk': self.no_access_user.pk
            })
        )
        data = response.context['form'].initial
        data['first_name'] = 'Jack'  # updated value
        data['date_joined'] = str(data['date_joined'])[:19]  # validation
        data['last_login'] = data['date_joined']  # validation
        response = self.client.post(
            reverse('myadmin:edit', kwargs={
                'model_name': 'auth.User', 'obj_pk': self.no_access_user.pk
            }),
            data=data
        )
        self.assertRedirects(response, reverse(
            'myadmin:objects', kwargs={'model_name': 'auth.User'}
        ))
        self.assertEqual(
            User.objects.get(pk=self.no_access_user.pk).first_name, 'Jack'
        )

    def test_deleting_object(self):
        self.client.force_login(self.access_user)
        self.access_user.user_permissions.add(self.user_delete_perm)
        user_to_delete = User.objects.create_user('qwe', 'c@c.c', 'pass1')
        response = self.client.get(
            reverse('myadmin:delete', kwargs={
                'model_name': 'auth.User', 'obj_pk': user_to_delete.pk
            })
        )
        self.assertRedirects(response, reverse(
            'myadmin:objects', kwargs={'model_name': 'auth.User'}
        ))
        self.assertFalse(User.objects.filter(username='qwe').exists())


class ApiTestCase(TestCase):
    def setUp(self):
        self.access_perm = Permission.objects.get(codename='access_panel')
        self.user_add_perm = Permission.objects.get(codename='add_user')
        self.user_edit_perm = Permission.objects.get(codename='change_user')
        self.user_delete_perm = Permission.objects.get(codename='delete_user')

        self.access_user = User.objects.create_user('log1', 'a@a.a', 'qw12')
        self.no_access_user = User.objects.create_user(
            'log2', 'bbb@bbb.com', 'qw12', first_name='Max'
        )
        self.access_user.user_permissions.add(self.access_perm)

    def test_access(self):
        # no global access to panel
        self.client.force_login(self.no_access_user)
        response = self.client.get(reverse('myadmin:model-list', kwargs={
            'model_name': 'auth.User'
        }))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.access_user)
        response = self.client.get(reverse('myadmin:model-list', kwargs={
            'model_name': 'auth.User'
        }))
        self.assertEqual(response.status_code, 200)

        # add permission
        response = self.client.post(reverse('myadmin:model-list', kwargs={
            'model_name': 'auth.User'
        }))
        self.assertEqual(response.status_code, 403)

        self.access_user.user_permissions.add(self.user_add_perm)
        response = self.client.post(reverse(
            'myadmin:model-list', kwargs={'model_name': 'auth.User'}
        ))
        self.assertEqual(response.status_code, 400)  # no data - 400 Error

        # change permission
        response = self.client.put(reverse('myadmin:model-detail', kwargs={
            'model_name': 'auth.User', 'pk': self.no_access_user.pk
        }))
        self.assertEqual(response.status_code, 403)

        self.access_user.user_permissions.add(self.user_edit_perm)
        response = self.client.put(reverse(
            'myadmin:model-detail', kwargs={
                'model_name': 'auth.User', 'pk': self.no_access_user.pk
            }
        ))
        self.assertEqual(response.status_code, 400)  # no data - 400 Error

        # delete permission
        response = self.client.delete(reverse('myadmin:model-detail', kwargs={
            'model_name': 'auth.User', 'pk': self.no_access_user.pk
        }))
        self.assertEqual(response.status_code, 403)

        self.access_user.user_permissions.add(self.user_delete_perm)
        self.assertTrue(User.objects.filter(username='log2').exists())
        response = self.client.delete(reverse(
            'myadmin:model-detail', kwargs={
                'model_name': 'auth.User', 'pk': self.no_access_user.pk
            }
        ))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(username='log2').exists())
