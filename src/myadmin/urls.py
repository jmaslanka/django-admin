from django.conf.urls import url

from myadmin import views

urlpatterns = [
    url(r'^', views.AdminPanelView.as_view(), name='myadmin')
]
