from django.db import models


class AdminPanel(models.Model):
    models_text = models.TextField(default='', blank=True)

    def __str__(self):
        return 'AdminPanel: {:.80}'.format(str(self.models_text))

    class Meta:
        permissions = (
            ('access_panel', 'Can access myadmin panel'),
        )
