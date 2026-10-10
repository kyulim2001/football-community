from django.urls import path
from .views import ChatMessageViewSet

chat_message_list = ChatMessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

chat_message_detail = ChatMessageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('messages/', chat_message_list, name='chat-message-list'),
    path('messages/<int:pk>/', chat_message_detail, name='chat-message-detail'),
]