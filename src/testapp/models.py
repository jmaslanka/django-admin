from django.db import models

# Create your models here.


class TestModel1(models.Model):
    text = models.TextField(null=True)
    integer = models.IntegerField(null=True)

    def __str__(self):
        return self.text[:50]


class TestModel2(models.Model):
    text = models.TextField(null=True)
    integer = models.IntegerField(null=True)

    def __str__(self):
        return self.text[:50]
