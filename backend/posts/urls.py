from django.urls import path
from .views import PostViewSet, CommentViewSet


# post_list = PostViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
# })

# post_detail = PostViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })

# post_like = PostViewSet.as_view({ 'post': 'like_post'})
# post_dislike = PostViewSet.as_view({'post': 'dislike_post'})
# post_report = PostViewSet.as_view({'post': 'report'})
# post_popular = PostViewSet.as_view({'get': 'popular_posts'})
# post_by_board = PostViewSet.as_view({'get': 'posts_by_board'})

# comment_list = CommentViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
# })

# comment_detail = CommentViewSet.as_view({
#     'get': 'retrieve',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })

urlpatterns = [
    path('', PostViewSet.as_view({'get': 'list','post': 'create',}), name='post-list'),
    path('popular/', PostViewSet.as_view({'get': 'popular_posts'}), name = 'post-popular'),
    path('boards/<str:name>/', PostViewSet.as_view({'get': 'posts_by_board'}), name='post-by-board'),
    # path('<int:pk>/', post_detail, name='post-detail'),
    path('<int:pk>/', PostViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'delete_post',}), name='post-detail'), # 왼쪽에 http method 뭐 쓸지 적고 오른쪽에 views에서 함수 이름 마음대로 정하고 데코레이터로 매핑
    path('<int:pk>/like/', PostViewSet.as_view({ 'post': 'like_post'}), name='post-like'),
    path('<int:pk>/dislike/', PostViewSet.as_view({'post': 'dislike_post'}), name='post-dislike'),
    path('<int:pk>/report/', PostViewSet.as_view({'post': 'report'}), name='post-report'),
    path('<int:post_pk>/comments/', CommentViewSet.as_view({
    'get': 'list',
    'post': 'create',}), name='comment-list'),
    path('<int:post_pk>/comments/<int:pk>/', CommentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',}), name='comment-detail'),
]
