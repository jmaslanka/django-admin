from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from myadmin import views

urlpatterns = [
    url(r'^$', views.AdminPanelView.as_view(), name='panel'),
    url(
        r'^objects/'
        r'(?P<model_name>[0-9A-Za-z_]+[.][0-9A-Za-z_]+)$',
        login_required(views.ModelListView.as_view()),
        name='objects'
    ),
    url(
        r'^create/'
        r'(?P<model_name>[0-9A-Za-z_]+[.][0-9A-Za-z_]+)$',
        login_required(views.ObjectCreateView.as_view()),
        name='create'
    ),
    url(
        r'^objects/'
        r'(?P<model_name>[0-9A-Za-z_]+[.][0-9A-Za-z_]+)/'
        r'(?P<obj_pk>[0-9]+)'
        r'delete$',
        login_required(views.ObjectDeleteView.as_view()),
        name='delete'
    ),
    url(
        r'^objects/'
        r'(?P<model_name>[0-9A-Za-z_]+[.][0-9A-Za-z_]+)/'
        r'(?P<obj_pk>[0-9]+)/'
        r'edit$',
        login_required(views.ObjectEditView.as_view()),
        name='edit'
    ),

]
