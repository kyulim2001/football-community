from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PostReport, CommentReport
from .serializers import PostReportSerializer, CommentReportSerializer

class PostReportViewSet(viewsets.ModelViewSet):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''
        현재 로그인한 사용자가 신고한 게시글 목록만 조회.
        다른 사용자가 신고한 내용은 보지 못하게 제한.
        '''
        return PostReport.objects.filter(reporter=self.request.user)

    def create(self, request, *args, **kwargs):
        '''
        게시글을 신고할 때 사용되는 메서드(POST 요청 처리)
        동작순서: 1. 클라이언트가 신고하려는 post_id 추출, 2. 이미 해당 게시글을 신고한 이력 있는지 확인 3. 신고했다면 400 4. 신고 이력 없으면 원래 create() 로직 실행
        '''
        post_id = request.data.get('post')
        if PostReport.objects.filter(reporter=request.user, post_id=post_id).exists():
            return Response({'detail': '이미 신고하셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        '''
        게시글 신고 저장 처리.
        목적: 클라이언트가 신고자를 직접 전달하지 않도록, 서버에서 현재 로그인한 사용자를 자동으로 신고자에 설정.
        '''
        serializer.save(reporter=self.request.user)


class CommentReportViewSet(viewsets.ModelViewSet):
    serializer_class = CommentReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''
        현재 로그인한 사용자가 신고한 댓글 목록만 조회.
        내가 신고한 댓글만 볼 수 있도록 제한.
        '''
        return CommentReport.objects.filter(reporter=self.request.user)

    def create(self, request, *args, **kwargs):
        '''
        댓글을 신고하는 POST 요청 처리.
        처리 순서: 1. 신고 대상 댓글 ID(comment_id)를 추출, 2. 중복 신고 여부 확인 3. 중복 신고면 400 4. 아니면 super().create()로 정상처리 진행
        '''
        comment_id = request.data.get('comment')
        if CommentReport.objects.filter(reporter=request.user, comment_id=comment_id).exists():
            return Response({'detail': '이미 신고하셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        '''
        댓글 신고 저장 처리.
        목적: 신고자가 직접 reporter 필드를 전달하지 않아도 되도록 함, 서버가 자동으로 reporter 필드에 현재 사용자 설정
        '''
        serializer.save(reporter=self.request.user)
