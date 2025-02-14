from django.urls import path
from .views import FileChatView

urlpatterns = [
    path('json-coverter/', FileChatView.as_view(), name='chat_with_file'),
]
