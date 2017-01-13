from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'^storage/new_file$', views.storage.FileUploadView.as_view(), name='create_file'),
]