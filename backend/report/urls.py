from django.urls import path
from .views import PostReportViewSet, CommentReportViewSet

# post_report_list = PostReportViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# post_report_detail = PostReportViewSet.as_view({
#     'get': 'retrieve',
#     'delete': 'destroy'
# })

# comment_report_list = CommentReportViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# comment_report_detail = CommentReportViewSet.as_view({
#     'get': 'retrieve',
#     'delete': 'destroy'
# })

urlpatterns = [
    path('post-reports/', PostReportViewSet.as_view({
    'get': 'list',
    'post': 'create'}), name='post-report-list'),
    path('post-reports/<int:pk>/', PostReportViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'}), name='post-report-detail'),
    path('comment-reports/', CommentReportViewSet.as_view({
    'get': 'list',
    'post': 'create'}), name='comment-report-list'),
    path('comment-reports/<int:pk>/', CommentReportViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
}), name='comment-report-detail'),
]
