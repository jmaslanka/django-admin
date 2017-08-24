from django.contrib import admin

from myadmin.models import AdminPanel
from testapp.models import TestModel1, TestModel2

# Register your models here.

admin.site.register(AdminPanel)
admin.site.register(TestModel1)
admin.site.register(TestModel2)
