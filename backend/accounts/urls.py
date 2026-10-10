from django.urls import path, include
from .views import (
    AuthViewSet, UserViewSet, FindIDViewSet,
    FindPasswordViewSet, SignupVerificationViewSet, BlockViewSet, SignupVerificationViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)


# auth_login = AuthViewSet.as_view({'post': 'login'})
# auth_logout = AuthViewSet.as_view({'post': 'logout'})
# auth_signup = AuthViewSet.as_view({'post': 'signup'})

# find_id_send_code = FindIDViewSet.as_view({'post': 'send_code'})
# find_id_verify = FindIDViewSet.as_view({'post': 'verify_code'})

# find_pw_send_code = FindPasswordViewSet.as_view({'post': 'send_code'})
# find_pw_verify = FindPasswordViewSet.as_view({'post': 'verify_code'})
# find_pw_reset = FindPasswordViewSet.as_view({'post': 'reset_password'})

# signup_send_code = SignupVerificationViewSet.as_view({'post': 'send_code'})
# signup_verify = SignupVerificationViewSet.as_view({'post': 'verify_code'})

# user_viewset = UserViewSet.as_view({'get': 'get_user_by_nickname'})
# user_list = UserViewSet.as_view({'get': 'list'})
# user_detail = UserViewSet.as_view({'get': 'retrieve'})
# mypage = UserViewSet.as_view({'get': 'me'})
# update_info = UserViewSet.as_view({'patch': 'update_info'})
# delete_account = UserViewSet.as_view({'delete': 'delete_account'})
# change_password = UserViewSet.as_view({'post': 'change_password'})
# update_profile = UserViewSet.as_view({'patch': 'profile'})
# my_posts = UserViewSet.as_view({'get': 'my_posts'})
# my_comments = UserViewSet.as_view({'get': 'my_comments'})
# liked_posts = UserViewSet.as_view({'get': 'liked_posts'})
# update_nickname = UserViewSet.as_view({'patch': 'update_nickname'})
# nickname_posts = UserViewSet.as_view({'get': 'user_posts_by_nickname'})
# nickname_comments = UserViewSet.as_view({'get': 'user_comments_by_nickname'})
# nickname_profile = UserViewSet.as_view({'get': 'get_user_by_nickname'})

# block_list = BlockViewSet.as_view({'get': 'list', 'post': 'create'})
# block_detail = BlockViewSet.as_view({'delete': 'destroy'})


# 경로 등록
urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Auth
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/signup/', AuthViewSet.as_view({'post': 'signup'}), name='auth-signup'),

    # 아이디 찾기
    path('find-id/send-code/', FindIDViewSet.as_view({'post': 'send_code'}), name='find-id-send'),
    path('find-id/verify/',  FindIDViewSet.as_view({'post': 'verify_code'}), name='find-id-verify'),

    # 비밀번호 찾기
    path('find-password/send-code/', FindPasswordViewSet.as_view({'post': 'send_code'}), name='find-pw-send'),
    path('find-password/verify/', FindPasswordViewSet.as_view({'post': 'verify_code'}), name='find-pw-verify'),
    path('find-password/reset-password/', FindPasswordViewSet.as_view({'post': 'reset_password'}), name='find-pw-reset'),

    # 회원가입 인증
    path('signup/send-code/', SignupVerificationViewSet.as_view({'post': 'send_code'})),
    path('signup/verify/', SignupVerificationViewSet.as_view({'post': 'verify_code'})),

    # 유저 관련 (예: 마이페이지)
    path('mypage/me/', UserViewSet.as_view({'get': 'me'}), name='mypage'),
    path('accounts/', UserViewSet.as_view({'get': 'list'}), name='accounts-list'),
    path('accounts/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='accounts-detail'),
    path('mypage/update-info/', UserViewSet.as_view({'patch': 'update_info'}), name='update-info'),
    path('mypage/delete-account/', UserViewSet.as_view({'delete': 'delete_account'}), name='delete-account'),
    path('mypage/change-password/', UserViewSet.as_view({'post': 'change_password'}), name='change-password'),
    path('mypage/update-profile/', UserViewSet.as_view({'patch': 'profile'}), name='update-profile'),
    path('mypage/my-posts/', UserViewSet.as_view({'get': 'my_posts'}), name='my-posts'),
    path('mypage/my-comments/', UserViewSet.as_view({'get': 'my_comments'}), name='my-comments'),
    path('mypage/liked-posts/', UserViewSet.as_view({'get': 'liked_posts'}), name='liked-posts'),
    path('mypage/update-nickname/', UserViewSet.as_view({'patch': 'update_nickname'}), name='update-nickname'),

    path('accounts/nickname/<str:nickname>/posts/', UserViewSet.as_view({'get': 'user_posts_by_nickname'}), name='nickname-posts'),
    path('accounts/nickname/<str:nickname>/comments/', UserViewSet.as_view({'get': 'user_comments_by_nickname'}), name='nickname-comments'),
    path('accounts/nickname/<str:nickname>/', UserViewSet.as_view({'get': 'get_user_by_nickname'}), name='nickname-profile'),
    
    path('accounts/blocks/', BlockViewSet.as_view({'get': 'list', 'post': 'create'}), name='block-list'),
    path('accounts/blocks/<int:pk>/', BlockViewSet.as_view({'delete': 'destroy'}), name='block-detail'),
]
