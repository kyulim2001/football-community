from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Profile, Block, EmailVerification, User
from .forms import ProfileForm
from .forms import SignupForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.middleware.csrf import get_token
import traceback
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.response import Response
from .import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, UserProfileSerializer, UserUpdateSerializer, PasswordChangeSerializer, UserDeleteSerializer, BlockSerializer
from rest_framework.decorators import action
from rest_framework import viewsets
from posts.models import Post, Comment
from posts.serializers import PostSerializer, CommentSerializer
import random
from django.core.mail import send_mail
from rest_framework.decorators import action
from django.conf import settings
from rest_framework.exceptions import ValidationError

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    '''
    로그인, 로그아웃, 회원가입 등 인증 관련 기능을 담당하는 viewset
    viewset을 사용해 /auth/login, logout, signup 등 엔드포인트 제공
    '''
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        '''
        사용자 로그인 처리
        처리 절차:
          1. 사용자명(username), 비밀번호(password) 추출
          2. 해당 사용자 존재 여부 확인
          3. 비활성화 계정인지 체크
          4. 비밀번호 일치 여부 확인
          5. JWT 토큰(access, refresh) 발급
          6. 세션 로그인 처리 (auth_login)
        '''
        data = request.data
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': '존재하지 않는 아이디입니다.'}, status=401)

        if not user.is_active:
            return Response({'error': '탈퇴한 사용자입니다.'}, status=401)

        if not user.check_password(password):
            return Response({'error': '비밀번호가 틀렸습니다.'}, status=401)

        auth_login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': '로그인 성공',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'nickname': user.nickname,
            'id': user.id
        }, status=200)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        '''
        사용자 로그아웃 처리
        
        처리 절차:
          - Django 세션 기반 로그아웃 수행
          - 클라이언트 측 토큰 삭제는 프론트에서 담당해야 함
        '''
        auth_logout(request)
        return Response({'message': '로그아웃 성공'}, status=200)


    def signup(self, request):
        '''
        사용자 회원가입 처리
        처리 절차:
          1. 필수 입력값 확인 (username, password, email, nickname)
          2. 중복 여부 확인
             - username, email, nickname
          3. 이메일 인증 완료 여부 확인
             - EmailVerification 레코드에서 is_verified == True 여부 체크
          4. 사용자 생성 및 이메일 인증 기록 삭제
          5. 세션 로그인(auth_login) 처리
        '''
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        nickname = data.get('nickname')

        if not all([username, password, email, nickname]):
            return Response({'error': '모든 항목을 입력해주세요.'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'username': '이미 존재하는 아이디입니다.'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'email': '이미 사용된 이메일입니다.'}, status=400)
        if User.objects.filter(nickname=nickname).exists():
            return Response({'nickname': '이미 사용된 닉네임입니다.'}, status=400)

        try:
            record = EmailVerification.objects.filter(email=email).latest('created_at')
            if not record.is_verified:
                return Response({'email': '이메일 인증이 완료되지 않았습니다.'}, status=400)
        except EmailVerification.DoesNotExist:
            return Response({'email': '이메일 인증 기록이 없습니다.'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, nickname=nickname)
        record.delete()
        auth_login(request, user)
        return Response({'message': '회원가입 성공'}, status=200)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def check_login(self, request):
        '''
        현재 로그인 상태인지 확인하는 엔드포인트
        JWT 또는 세션 기반 인증을 통과한 경우 "로그인 상태입니다" 반환
        '''
        return Response({'message': '로그인 상태입니다'})

    @action(detail=False, methods=['get'])
    def check_duplicate(self, request):
        '''
        username, email, nickname 중복 확인
        처리 절차:
          1. 쿼리 파라미터로 들어온 필드명 추출 (username/email/nickname)
          2. 해당 필드가 이미 존재하면 400, 아니면 200 응답
        클라이언트 회원가입 시 실시간 중복 확인에 사용됨
        '''
        for field in ['username', 'email', 'nickname']:
            value = request.query_params.get(field)
            if value:
                if User.objects.filter(**{field: value}).exists():
                    return Response({field: f'이미 사용 중인 {field}입니다.'}, status=400)
                else:
                    return Response({field: f'사용 가능한 {field}입니다.'}, status=200)
        return Response({'error': '유효하지 않은 요청'}, status=400)

class UserViewSet(viewsets.ViewSet):
    '''
    사용자 관련 기능(정보 조회, 수정, 비밀번호 변경, 마이페이지 조회 등)을 담당하는 ViewSet.
    대부분 로그인한 사용자만 접근 가능 (IsAuthenticated)
    단, 특정 닉네임으로 유저/글/댓글 조회는 비로그인도 허용
    '''
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        '''
        현재 로그인한 사용자의 정보를 반환하는 API.
        React 앱에서 로그인 상태 유지 및 마이페이지 로딩 시 사용
        반환값: username, nickname, email
        '''
        return Response({
            'isLoggedIn': True,
            'username': request.user.username,
            'nickname': request.user.nickname,
            'email': request.user.email,
        })
    
    def get_permissions(self):
        '''
        ViewSet의 기본 permission을 오버라이드하여
        닉네임 기반 조회 API만 비로그인 사용자(AllowAny)에게 허용하고,
        나머지는 로그인 사용자(IsAuthenticated)만 접근 가능하게 함.
        '''
        if self.action in ['user_posts_by_nickname', 'user_comments_by_nickname', 'get_user_by_nickname']:
            return [AllowAny()]
        return super().get_permissions()


    @action(detail=False, methods=['patch'])
    def update_info(self, request):
        '''
        사용자 정보(이메일, 닉네임 등) 일부 수정 API.
        1. request.user를 기준으로 serializer 호출 (partial=True)
        2. 유효성 검사 통과 시 저장
        '''
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '정보 수정 완료'}, status=200)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        '''
        회원 탈퇴 API: 실제 삭제 대신 비활성화 처리.
        절차:
        1. 클라이언트가 입력한 password를 검증
        2. 일치하면 user의 is_active = False 설정
        3. 유효성 또는 비밀번호 불일치 시 적절한 오류 반환
        '''
        serializer = UserDeleteSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']

            if not request.user.check_password(password):
                return Response({'password': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            request.user.is_active = False
            request.user.save()
            return Response({'message': '회원 탈퇴 완료'}, status=200)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        '''
        비밀번호 변경 API.
        절차:
        1. old_password, new_password1, new_password2 필드를 검증
        2. 패스워드 일치 및 형식 유효성 검사
        3. 비밀번호 변경 및 저장
        성공 시: "비밀번호 변경 완료" 응답
        실패 시: 각각의 필드별 오류 메시지 반환
        '''
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '비밀번호 변경 완료'}, status=200)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['patch'])
    def profile(self, request):
        '''
        사용자 프로필(Profile 모델)의 정보(소개글, 사진 등) 수정 API.
        request.user.profile에 접근하여 부분 업데이트 수행
        '''
        serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '프로필 수정 완료'}, status=200)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        '''
        현재 로그인한 사용자가 작성한 게시글 목록 조회 API.
        최신순 정렬 (created_at DESC)
        프론트 마이페이지 "내 게시글" 탭에서 사용
        '''
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        '''
        현재 로그인한 사용자가 작성한 댓글 목록 조회 API.
        최신순 정렬
        프론트 마이페이지 "내 댓글" 탭에서 사용
        '''
        comments = Comment.objects.filter(user=request.user).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def liked_posts(self, request):
        '''
        현재 로그인한 사용자가 좋아요를 누른 글 목록 조회 API.
        최신순 정렬
        ManyToMany 필드를 써서 역참조
        '''
        posts = Post.objects.filter(like=request.user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='update_nickname')
    def update_nickname(self, request):
        '''
        닉네임 변경 api
        절차: 1. 닉네임 입력 여부 확인 2. 중복 여부 검사(본인 제외) 3. 통과하면 저장 후 새 닉네임 반환
        '''
        new_nickname = request.data.get('nickname')
        if not new_nickname:
            return Response({'error': '닉네임을 입력해주세요.'}, status=400)

        # 닉네임 중복 검사
        if User.objects.filter(nickname=new_nickname).exclude(id=request.user.id).exists():
            return Response({'error': '이미 사용 중인 닉네임입니다.'}, status=400)

        request.user.nickname = new_nickname
        request.user.save()
        return Response({'message': '닉네임이 변경되었습니다.', 'nickname': new_nickname}, status=200)

    @action(detail=False, methods=['get'], url_path=r'nickname/(?P<nickname>[^/.]+)/posts', permission_classes=[AllowAny])
    def user_posts_by_nickname(self, request, nickname=None):
        '''
        특정 닉네임을 가진 사용자의 게시글 조회 API.
        비로그인 사용자도 접근 가능
        게시글은 최신순 정렬
        프로필 페이지나 유저 검색에서 사용됨
        '''
        user = get_object_or_404(User, nickname=nickname)
        posts = Post.objects.filter(user=user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response({'posts': serializer.data})
    
    
    @action(detail=False, methods=['get'], url_path=r'nickname/(?P<nickname>[^/.]+)/comments', permission_classes=[AllowAny])
    def user_comments_by_nickname(self, request, nickname=None):
        '''
        특정 닉네임을 가진 사용자의 댓글 조회 API.
        비로그인 사용자도 접근 가능
        댓글은 최신순 정렬
        '''
        user = get_object_or_404(User, nickname=nickname)
        comments = Comment.objects.filter(user=user).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response({'comments': serializer.data})
    
    @action(detail=False, methods=['get'], url_path=r'nickname/(?P<nickname>[^/.]+)', permission_classes=[AllowAny])
    def get_user_by_nickname(self, request, nickname=None):
        '''
        특정 닉네임으로 사용자 정보를 조회하는 API.
        존재하지 않는 경우 404 반환
        존재할 경우 전체 유저 정보 반환(UserSerializer)
        '''
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return Response({'detail': '유저 없음'}, status = 404)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)


    
class BlockViewSet(viewsets.ModelViewSet):
    '''
    사용자가 다른 사용자를 차단하는 기능을 담당하는 ViewSet.
    로그인한 사용자만 접근 가능
    '''
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        '''
        현재 로그인한 사용자가 차단한 사용자 목록을 조회하는 메서드.
        '''
        return Block.objects.filter(blocker=self.request.user)
    
    def perform_create(self, serializer):
        '''
        차단 요청을 실제로 저장하기 전에 수행되는 메서드.
        
        차단 유효성 검증 포함:
        1. 자기 자신은 차단 불가능
        2. 이미 차단한 사용자면 중복 차단 불가
        3. 위 조건을 모두 통과하면 blocker 필드를 현재 사용자로 지정하여 저장

        이 로직을 serializer 내부가 아니라 ViewSet에서 처리하는 이유:
        - request.user에 접근할 수 있고
        - 비즈니스 로직이 명확히 드러남
        '''
        blocked_user = serializer.validated_data['blocked']

        if blocked_user == self.request.user:
            raise ValidationError("자기 자신을 차단할 수 없습니다.")

        if Block.objects.filter(blocker=self.request.user, blocked=blocked_user).exists():
            raise ValidationError("이미 차단한 사용자입니다.")

        serializer.save(blocker=self.request.user)


class FindIDViewSet(viewsets.ViewSet):
    '''
    이메일을 통해 사용자 아이디(username)를 찾는 기능을 제공하는 ViewSet
    비로그인 사용자도 접근 가능 (AllowAny)
    인증 코드 전송 + 인증 코드 검증 + 아이디 반환 기능을 포함
    '''
    permission_classes = [AllowAny]
    @action(detail=False, methods=['post'], url_path='send-code')
    def send_code(self, request):
        '''
        이메일로 인증 코드를 전송하는 API.(POST /find-id/send-code/)
        처리 순서:
        1. 이메일 필드 유효성 검사 (값이 있는지 확인)
        2. 해당 이메일로 가입된 사용자가 있는지 확인
        3. 4자리 숫자 인증 코드 생성
        4. EmailVerification 객체 생성 및 저장
        5. 이메일 발송 (Django send_mail 사용)
        응답: 코드 발송 성공 여부
        실패: 이메일 누락, 가입 이력 없음
        '''
        email = request.data.get('email')
        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status = 400)
        
        if not User.objects.filter(email=email).exists():
            return Response({'detail': '해당 이메일로 가입된 사용자가 없습니다.'}, status = 404)
        
        code = str(random.randint(1000, 9999))
        EmailVerification.objects.create(email=email, code=code)
        
        send_mail(
            subject = '[사이트 이름]아이디 찾기 인증 코드',
            message = f'인증 코드는 다음과 같습니다: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list = [email],
        )
        return Response({'detail': '인증 코드를 전송했습니다.'}, status = 200)
    
    @action(detail=False, methods = ['post'], url_path = 'verify', permission_classes = [AllowAny])
    def verify_code(self, request):
        '''
            사용자가 입력한 인증 코드가 올바른지 검증하는 API.
            (POST /find-id/verify/)

            처리 순서:
            1. 해당 이메일로 생성된 가장 최근 인증 기록 조회
            2. 인증 코드 일치 여부 확인
            3. 인증 코드 만료 여부 확인
            4. 성공 시 username 반환

            성공: 사용자 아이디 반환
            실패: 기록 없음, 불일치, 만료됨 등
        '''
        email = request.data.get('email')
        code = request.data.get('code')
        
        try:
            record = EmailVerification.objects.filter(email=email).latest('created_at')
        except EmailVerification.DoesNotExist:
            return Response({'detail': '인증 요청 기록이 없습니다.'}, status=404)
        
        if str(record.code) != str(code):
            return Response({'detail': '인증 코드가 일치하지 않습니다.'}, status=400)
        
        if record.is_expired():
            return Response({'detail': '인증 코드가 만료되었습니다.'}, status = 400)
        
        try:
            user = User.objects.get(email=email)
            return Response({'username': user.username})
        
        except User.DoesNotExist:
            return Response({'detail': '해당 이메일로 가입된 사용자가 없습니다.'}, stauts = 404)
        
class FindPasswordViewSet(viewsets.ViewSet):
    '''
    이메일을 통해 비밀번호를 재설정하는 기능을 제공하는 ViewSet.
    로그인하지 않은 사용자도 사용 가능
    주요 기능:
        1. 인증 코드 전송
        2. 인증 코드 검증
        3. 아이디 반환
        4. 비밀번호 재설정
    '''
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='send-code')
    def send_code(self, request):
        '''
        이메일로 인증 코드를 전송하는 API.
        (POST /find-password/send-code/)
        처리 절차:
        1. 이메일 입력 여부 확인
        2. 해당 이메일로 가입된 사용자 존재 여부 확인
        3. 4자리 숫자 랜덤 코드 생성
        4. EmailVerification 객체 생성
        5. 인증 코드를 이메일로 발송
        성공 시: 인증 코드 전송 메시지 반환
        실패 시: 이메일 누락, 사용자 없음 등 에러 반환
        '''
        email = request.data.get('email')
        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status = 400)
        if not User.objects.filter(email=email).exists():
            return Response({'detail': '해당 이메일로 가입된 사용자가 없습니다.'}, status = 404)
        
        code = str(random.randint(1000, 9999))
        EmailVerification.objects.create(email=email, code=code)
        
        send_mail(
            subject='[사이트 이름] 인증 코드',
            message= f'인증 코드는 다음과 같습니다: {code}',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({'detail': '인증 코드를 전송했습니다.'}, status = 200)
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_code(self, request):
        '''
        사용자가 입력한 인증 코드가 올바른지 확인하는 API.
        (POST /find-password/verify/)
        처리 절차:
        1. 이메일로 가장 최근 인증 기록 조회
        2. 입력된 인증 코드와 일치 여부 확인
        3. 인증 코드 만료 여부 확인
        성공 시: '인증 성공' 메시지 반환
        실패 시: 인증 기록 없음, 코드 불일치, 만료됨
        '''
        email = request.data.get('email')
        code = request.data.get('code')
        
        try:
            record = EmailVerification.objects.filter(email=email).latest('created_at')
        except EmailVerification.DoesNotExist:
            return Response({'detail': '인증 요청 기록이 없습니다.'}, status=404)
        
        if str(record.code) != str(code):
            return Response({'detail': '인증 코드가 일치하지 않습니다.'}, status=404)
        
        if record.is_expired():
            return Response({'detail': '인증 코드가 만료되었습니다.'}, status=400)
        
        return Response({'detail': '인증 성공'}, status=200)
    
    @action(detail=False, methods=['post'], url_path = 'find-id')
    def find_id(self, request):
        '''
        이메일로 사용자 아이디(username)를 찾는 API.
        (POST /find-password/find-id/)
        절차:
        1. 이메일에 해당하는 사용자 조회
        2. 존재할 경우 username 반환
        성공: {'username': 사용자아이디}
        실패: 사용자 없음
        '''
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            return Response({'username': user.username})
        except User.DoesNotExist:
            return Response({'detail': '해당 이메일로 가입된 사용자가 없습니다.'}, status = 404)
    
    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        '''
        인증된 사용자의 비밀번호를 재설정하는 API.
        (POST /find-password/reset-password/)

        처리 절차:
        1. 모든 필드(email, code, new_password) 존재 여부 확인
        2. 이메일에 해당하는 사용자 조회
        3. 가장 최근의 인증 코드 조회
        4. 코드 일치 여부 및 만료 여부 검증
        5. 사용자 비밀번호 변경 및 저장

        성공: "비밀번호가 성공적으로 변경되었습니다."
        실패: 사용자 없음, 인증 실패, 만료, 필드 누락 등
        
        '''
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not all([email, code, new_password]):
            return Response({'detail': '모든 필드를 입력해주세요.'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': '존재하지 않는 사용자입니다.'}, status=404)
        
        try:
            record = EmailVerification.objects.filter(email=user.email).latest('created_at')
        except EmailVerification.DoesNotExist:
            return Response({'detail': '인증코드가 만료되었습니다.'}, status = 404)
        if str(record.code) != str(code):
            return Response({'detail': '인증 코드가 일치하지 않습니다.'}, status = 400)
        if record.is_expired():
            return Response({'detail': '인증 코드가 만료되었습니다.'}, status = 400)
        
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': '비밀번호가 성공적으로 변경되었습니다.'}, status = 200)
    
class SignupVerificationViewSet(viewsets.ViewSet):
    '''
    회원가입 과정에서 이메일을 인증하기 위한 인증 코드 전송 및 검증을 담당하는 ViewSet.
    비로그인 사용자도 접근 가능 (AllowAny)
    기능 구성:
        1. 인증 코드 전송
        2. 인증 코드 검증
    '''
    permission_classes = [AllowAny]
    
    def send_code(self, request):
        '''
        회원가입 시 사용자가 입력한 이메일로 인증 코드를 전송하는 API.
        (POST /signup-verification/send-code/)
        처리 절차:
        1. 이메일 필드 존재 여부 확인
        2. 이미 가입된 이메일인지 중복 검사
        3. 이메일 형식 제한 (gmail만 허용)
        4. 4자리 인증 코드 생성 (랜덤 숫자)
        5. EmailVerification 객체 저장
        6. 이메일 발송 (Django send_mail 사용)
        성공: 인증 코드 전송 완료 메시지 반환
        실패:
            - 이메일 없음
            - 이미 사용 중인 이메일
            - gmail 도메인 아님
        '''
        email = request.data.get('email')
        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status = 400)
        
        if User.objects.filter(email=email).exists():
            return Response({'detail': '이미 사용 중인 이메일입니다.'}, status = 400)
        
        if not email.endswith('@gmail.com'):
            return Response({'detail': '이메일은 gmail만 사용 가능합니다.'}, status = 400)
        
        code = str(random.randint(1000, 9999))
        EmailVerification.objects.create(email=email, code=code)
        
        send_mail(
            subject='[사이트 이름] 인증 코드',
            message= f'인증 코드는 다음과 같습니다: {code}',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({'detail': '인증 코드를 전송했습니다.'}, status = 200)
    

    def verify_code(self, request):
        '''
            사용자가 입력한 인증 코드가 올바른지 확인하는 API.
            (POST /signup-verification/verify/)

            처리 절차:
            1. 이메일과 인증 코드를 입력받음
            2. 해당 이메일로 가장 최근 인증 코드 조회
            3. 코드 일치 여부 확인
            4. 만료 여부 확인
            5. 통과하면 해당 기록을 is_verified=True로 설정하고 저장

            성공: '인증 성공' 메시지
            실패:
                - 인증 기록 없음
                - 코드 불일치
                - 코드 만료
        '''
        email = request.data.get('email', '').lower()
        code = str(request.data.get('code'))

        try:
            record = EmailVerification.objects.filter(email=email).latest('created_at')
        except EmailVerification.DoesNotExist:
            return Response({'detail': '인증 요청 기록이 없습니다.'}, status=404)

        if str(record.code) != code:
            return Response({'detail': '인증 코드가 일치하지 않습니다.'}, status=404)

        if record.is_expired():
            return Response({'detail': '인증 코드가 만료되었습니다.'}, status=400)
        
        record.is_verified = True
        record.save()

        return Response({'detail': '인증 성공'}, status=200)

    
        
    
    