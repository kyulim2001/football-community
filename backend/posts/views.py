from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Post, Comment, Board
from .serializers import PostSerializer, CommentSerializer, ReportSerializer
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.paginator import Paginator
from accounts.models import Block
from notifications.models import Notification
from posts.models import PostMedia
import json
from django.db.models import Q, Count
from rest_framework import serializers

class SafeJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None

class PostViewSet(viewsets.ModelViewSet):
    '''
    게시글(Post) 관련 CRUD 및 좋아요/싫어요/신고/인기글 조회 기능을 모두 포함하는 ViewSet.

    주요 기능:
      - 게시글 목록 조회 (검색, 필터링, 페이지네이션 포함)
      - 게시글 상세 조회 (조회수 증가 포함)
      - 게시글 작성 (파일 업로드 포함)
      - 게시글 수정 / 삭제
      - 좋아요 / 싫어요 기능
      - 인기글 조회 (좋아요 3개 이상)
      - 게시판별 게시글 조회
      - 게시글 신고 기능

    인증 및 권한:
      - 로그인하지 않아도 게시글 목록/상세 조회 가능 (IsAuthenticatedOrReadOnly)
      - 작성, 수정, 삭제 등은 로그인 필요
      - JWT, 세션, Basic 인증 모두 지원

    설정:
      - serializer_class = PostSerializer
      - parser_classes = [MultiPartParser, FormParser]: 파일 업로드 지원
      - ordering, filtering, search 지원
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all().order_by('-id') # 쿼리셋 = db에서 갖고올 데이터 목록
    serializer_class = PostSerializer # 게시글을 json으로 변환
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] # 검색 정렬 기능 설정
    ordering_fields = ['created_at', 'id'] # ?ordering=created_at 또는 ?ordering=id로 정렬 가능
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser] # api로 파일 받을땐 특별한 파서가 필요함. 파일 첨부가 포함된 요청을 처리 가능하게끔 해줌
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    
    def list(self, request, *args, **kwargs):
        '''
        전체 게시글 목록을 조회하는 메서드.
        지원하는 기능: 1. 게시판(board) 필터 2. 작성자(user) 필터3. 차단된 유저 제외4. 검색 기능(제목, 내용, 작성자 닉네임 기준) 5. 페이지네이션
        동작 순서: 1. 검색 쿼리와 필터링 조건 파악 2. queryset을 조건에 맞게 필터링 3. 로그인한 사용자가 차단한 유저의 글은 제외 4. 페이지네이션이 필요한 경우 나눠서 응답
        '''
        user_id = request.GET.get('user')
        board_id = request.GET.get('board') # 쿼리 스트링으로 user 또는 board 값이 전달됐는지 확인
        search_query = request.query_params.get('search')
        search_scope = request.query_params.get('scope')
        queryset = Post.objects.all()
        
        if search_query:
            if search_scope == 'title':
                queryset = queryset.filter(title__icontains=search_query)
            elif search_scope == 'title_content':
                queryset = queryset.filter(
                    Q(title__icontains=search_query) | Q(content__icontains=search_query)
                )
            elif search_scope == 'author':
                queryset = queryset.filter(user__nickname__icontains=search_query)
        
        if board_id and board_id.isdigit():
            queryset = queryset.filter(board_id=int(board_id)) # id로 필터링
        if request.user.is_authenticated:
            blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True) # 로그인한 사용자가 차단한 유저 게시글 안 보이게끔 필터링
            queryset = queryset.exclude(user_id__in=blocked_users)
        if user_id:
            queryset = queryset.filter(user_id = user_id) # 특정 사용자가 작성한 글만 필터링
            
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset) # 페이지네이션 적용, paginate_queryset = 데이터를 쪼갬
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)  # 나눠진 데이터에 페이지 정보도 같이 담아 응답

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data) # 전체 데이터를 json으로 변환해서 응답

    def retrieve(self, request, pk=None, *args, **kwargs):
        '''
        특정 게시글 하나를 상세 조회하는 메서드
        동작: 1. 해당 게시글의 조회수를 1 증가, 2. 게시글 데이터를 직렬화해서 응답.
        예외: 존재하지 않는 게시글이면 404 띄우기
        '''
        post = self.get_object()
        post.views += 1
        post.save() # 해당 게시글을 갖고 오고 조회수 1 올리고 저장
        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data) # 게시글을 json으로 직렬화해서 응답

    def create(self, request, *args, **kwargs):
        '''
        게시글을 새로 생성하는 메서드.
        동작: 1. 클라이언트가 보낸 데이터를 복사, 2. board가 문자열이면 정수로 변환, 3. 시리얼라이저로 데이터 유효성 검사, 4. perform_create 호출로 db 저장 5. 생성된 데이터와 함께 응답 반환
        '''
        data = request.data.copy() # 클라이언트가 보낸 데이터를 복사
        if 'board' in data: # 보드값이 문자열일수도 있으니 정수형으로 바꿈
            try:
                data['board'] = int(data['board'])
            except ValueError:
                return Response({'board': '정수형 ID여야 합니다.'}, status=400)
        serializer = self.get_serializer(data=data) # 시리얼라이저에 데이터 넣고 유효한지 검사
        serializer.is_valid(raise_exception=True) # 오류가 있으면 에러 응답 발생
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data) # 새로 만든 게시글 정보를 넣어서 성공 응답용 헤더를 생성
        return Response(serializer.data, status=201, headers=headers) # 사용자에게 게시글을 json으로 바꾼걸 응답함, 위에서 만든 헤더로 응답
    
    def perform_create(self, serializer):
        '''
        게시글을 실제 db에 저장하는 로직.
        create() 메서드는 내부적으로 perform_create()를 호출. 클라이언트는 보안상 유저 정보를 넘기지 않기 때문에 서버에서 직접 넣어줘야 하는걸 여기 메서드에서 해줌.
        사용자 인증: 로그인한 사용자를 게시글 작성자로 저장.
        '''
        serializer.save(user=self.request.user)
        

    def update(self, request, pk=None, *args, **kwargs):
        '''
        게시글 전체 수정(PUT 요청)
        동작: 클라이언트가 보낸 데이터로 전체 필드를 덮어씀
        '''
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        '''
        게시글 일부 수정(PATCH 요청)
        동작: 1. 본문/제목 등 일부 필드만 수정, 2. deleted_media_ids: 삭제할 첨부파일 id처리 3. files: 새로 업로드한 파일 추가
        '''
        post = self.get_object()

        # 🔹 기본 필드 수정
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 🔹 기존 파일 삭제
        deleted_ids_json = request.data.get('deleted_media_ids', [])
        if deleted_ids_json:
            try:
                deleted_ids = json.loads(deleted_ids_json)
                PostMedia.objects.filter(id__in=deleted_ids, post=post).delete()
            except json.JSONDecodeError:
                return Response({'detail': '삭제할 파일 ID가 유효하지 않음'}, status=400)

        # 🔹 새 파일 추가
        new_files = request.FILES.getlist('files')
        for file in new_files:
            PostMedia.objects.create(post=post, file=file)

        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_post(self, request, *args, **kwargs):
        '''
        게시글 삭제 전용 엔드포인트(DELETE /posts/{id}/delete_post/)
        detail=True: 특정 게시글 대상으로 처리한다는 뜻
        실제 삭제 수행.
        '''
        post = self.get_object()
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='like', permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication])
    def like_post(self, request, pk=None):
        '''
        게시글 좋아요 기능 (POST /posts/{id}/like/)
        기능: 이미 좋아요 누른 경우: 좋아요 취소, 처음 누른 경우: 좋아요 추가 & 싫어요 제거, 게시글 작성자에게 알림 전송
        '''
        post = self.get_object()
        user = request.user
        if post.like.filter(pk=user.pk).exists():
            post.like.remove(user)
            return Response({'detail': '좋아요가 취소되었습니다.'}, status=status.HTTP_200_OK)
        else:
            post.like.add(user)
            post.dislike.remove(user)
            
            if post.user != user:
                Notification.objects.create(
                    type='like',
                    sender=user,
                    receiver=post.user,
                    post=post
                )
            return Response({'detail': '좋아요를 눌렀습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='dislike', permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication])
    def dislike_post(self, request, pk=None):
        '''
        게시글 싫어요 기능(POST  /posts/{id}/dislike/)
        기능: 이미 싫어요 누른 경우: 취소, 처음 누른 경우: 싫어요 추가 + 좋아요 제거
        '''
        post = self.get_object()
        user = request.user
        if post.dislike.filter(pk=user.pk).exists():
            post.dislike.remove(user)
            return Response({'detail': '싫어요가 취소되었습니다.'}, status=status.HTTP_200_OK)
        else:
            post.dislike.add(user)
            post.like.remove(user)
            return Response({'detail': '싫어요를 눌렀습니다.'}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path = 'boards/(?P<name>[^/.]+)')
    def posts_by_board(self, request, name=None):
        '''
        특정 게시판 이름으로 게시글 조회(GET /posts/boards/{name})
        board 이름을 통해 게시글 목록 필터링
        '''
        try:
            board = Board.objects.get(name=name)
        except Board.DoesNotExist:
            return Response({'error': 'Board not found'}, status=404)
        
        posts = Post.objects.filter(board__name__contains=name).order_by('-created_at')
        serializer = self.get_serializer(posts, many = True)
        return Response(serializer.data)
    
    @action(detail=False, methods = ['post'], permission_classes = [IsAuthenticated])
    def report(self, request):
        '''
        게시글 신고 기능(POST /posts/report/)
        요청 데이터: 신고 대상+ 이유, 로그인한 사용자만 가능, 유효성 검사 후 저장.
        '''
        serializer = ReportSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_posts(self, request):
        '''
        인기 게시글 조회 기능(GET /posts/popular/)
        좋아요 3개 이상 게시글만 반환, 게시판이랑 검색 쿼리 필터링 가능, 조회수 & 좋아요 수 기준 정렬
        '''
        board_id = request.query_params.get('board')
        search_query = request.query_params.get('search')
        search_scope = request.query_params.get('scope')
        
        posts = Post.objects.annotate(
            like_count=Count('like')
        ).filter(like_count__gte=3)
        
        if board_id:
            posts = posts.filter(board_id=board_id)
        
        if search_query:
            if search_scope == 'title':
                posts = posts.filter(title__icontains=search_query)
            elif search_scope == 'title_content':
                posts = posts.filter(
                    Q(title__icontains=search_query) | Q(content__icontains=search_query)
                )
            elif search_scope == 'author':
                posts = posts.filter(user__nickname__icontains=search_query)
                
        posts = posts.order_by('-like_count', '-views')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    def get_is_liked(self, obj):
        '''
        현재 로그인 사용자가 이 게시글을 좋아요 눌렀는지 여부 반환
        '''
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like.filter(pk=request.user.pk).exists()
        return False

    def get_is_disliked(self, obj):
        '''
        현재 로그인한 사용자가 이 게시글을 싫어요 눌렀는지 여부 반환
        '''
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.dislike.filter(pk=request.user.pk).exists()
        return False
        

# TODO: COMMENTVIEWSET도 POSTVIEWSET처럼 @ACTION DECORATOR 쓰기. 
class CommentViewSet(viewsets.ModelViewSet):
    '''
    댓글(Comment) 관련 CRUD 및 대댓글 알림 기능을 포함한 ViewSet.

    주요 기능:
      - 특정 게시글(post_pk)에 달린 댓글 목록 조회
      - 댓글 작성 (대댓글 포함)
      - 댓글 수정 / 삭제 (내용 비우고 삭제 표시)
      - 알림(Notification) 생성: 댓글/대댓글 작성 시

    인증 및 권한:
      - 읽기: 누구나 가능
      - 쓰기/수정/삭제: 로그인 필요 (IsAuthenticatedOrReadOnly)
      - 작성자 본인만 수정/삭제 가능

    설정:
      - serializer_class = CommentSerializer
      - authentication_classes: JWT + 세션 + Basic 지원

    주의사항:
      - URL 패턴 상 post_pk가 반드시 포함되어야 함
      - 삭제 시 실제 삭제하지 않고 '삭제된 댓글'로 처리 (soft delete)
    '''
    authentication_classes = [SafeJWTAuthentication]
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        '''
        특정 게시글(post_id)의 댓글 목록을 조회하는 메서드.
        kwargs['post_pk']는 라우팅 url 내에서 추출한 게시글 id
        댓글은 작성 시간 순으로 정렬
        '''
        post_id = self.kwargs['post_pk'] # kwargs 같은 딕셔너리에 get 쓰면 쉼표를 꼭 붙여넣어야 한다.
        if not post_id or not str(post_id).isdigit():
            return None
        return Comment.objects.filter(post_id=post_id).order_by('created_at')

    
    def perform_create(self, serializer):
        '''
        새로운 댓글을 생성하면서 작성자와 게시글을 자동으로 설정함.
        댓글이 대댓글인 경우 부모 댓글(parent)을 바탕으로 대댓글 알림을 전송하고
        일반 댓글이라면 게시글 작성자에게 알림을 전송함.
        알림은 Notification 모델을 통해 생성되며
        알림의 종류는 reply 또는 comment로 구분됨.
        '''
        
        comment = serializer.save(user=self.request.user, post_id=self.kwargs.get('post_pk',))
        post = comment.post
        parent = comment.parent

        if parent and parent.user != self.request.user:
            # 대댓글 알림
            Notification.objects.create(
                type='reply',
                sender=self.request.user,
                receiver=parent.user,
                post=post,
                comment=comment,
            )
        elif post.user != self.request.user:
            # 댓글 알림
            Notification.objects.create(
                type='comment',
                sender=self.request.user,
                receiver=post.user,
                post=post,
                comment=comment,
            )
    
     # 전체 댓글 목록
    def list(self, request, *args, **kwargs):
        '''
        댓글 전체 조회(GET 요청)
        post_pk 기준으로 필터링된 결과 반환
        '''
        return super().list(request, *args, **kwargs)

    # 특정 댓글 하나 조회
    def retrieve(self, request, *args, **kwargs):
        '''
        특정 댓글 하나 조회(GET /posts/{post_id}/comments/{comment_id}/)
        '''
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


    # 댓글 전체 수정 (PUT)
    def update(self, request, *args, **kwargs):
        '''
        댓글 전체 수정(PUT 요청)
        권한 확인: 작성자 본인만 수정 가능.
        유효성 검사 후 저장.
        '''
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'detail': '수정 권한이 없습니다.'}, status=403)
        serializer = self.get_serializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 일부 수정 (PATCH)
    def partial_update(self, request, *args, **kwargs):
        '''
        댓글 일부 수정(PATCH 요청)
        권한 확인: 작성자 본인만 가능.
        '''
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'detail': '수정 권한이 없습니다.'}, status=403)
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 삭제
    def destroy(self, request, *args, **kwargs):
        '''
        댓글 삭제 처리(DELETE 요청)
        실제로 DB에서 삭제하지 않고 내용만 비우고 "삭제됨" 표시
        권한: 작성자 본인만 삭제 가능.
        '''
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'detail': '삭제 권한이 없습니다.'}, status=403)
        comment.is_deleted = True
        comment.content = ''
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)  


