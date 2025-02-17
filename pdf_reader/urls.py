from django.urls import path
from .views import FileChatView

urlpatterns = [
    path('json-converter/', FileChatView.as_view(), name='chat_with_file'),
]
