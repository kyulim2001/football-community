from django.urls import path
from .views import NotificationViewSet

# notification_list = NotificationViewSet.as_view({'get': 'list'})
# notification_detail = NotificationViewSet.as_view({
#     'get': 'retrieve',
#     'delete': 'destroy',
# })
# notification_unread_count = NotificationViewSet.as_view({'get': 'unread_count'})
# notification_mark_read = NotificationViewSet.as_view({'patch': 'mark_as_read'})

urlpatterns = [
    path('', NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
    path('<int:pk>/', NotificationViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy',}), name='notification-detail'),
    path('unread-count/', NotificationViewSet.as_view({'get': 'unread_count'}), name='notification-unread-count'),
    path('<int:pk>/mark-read/', NotificationViewSet.as_view({'patch': 'mark_as_read'}), name='notification-mark-read'),
]
