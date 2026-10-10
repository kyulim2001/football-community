from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class NotificationViewSet(viewsets.ModelViewSet):
    '''
    사용자 알림(Notification)을 조회하고 상태를 변경하는 기능을 제공하는 ViewSet.

    인증:
        - 로그인한 사용자만 접근 가능 (permissions.IsAuthenticated)
        - JWTAuthentication 사용

    기본 제공 기능 (ModelViewSet):
        - list(): 전체 알림 목록 조회
        - retrieve(): 특정 알림 상세 조회
        - destroy(): 알림 삭제
        - update/partial_update(): 알림 수정 (실제 사용은 거의 없음)

    커스텀 액션:
        - GET /notifications/unread-count/
            → 읽지 않은 알림의 개수를 반환 (배지에 사용)
        - PATCH /notifications/{id}/mark-read/
            → 특정 알림을 읽음 처리

    제한 사항:
        - 다른 사용자의 알림을 조회하거나 수정할 수 없음 (get_queryset 필터링 + mark_as_read 권한 검사)
        - 알림 생성은 클라이언트가 직접 호출하지 않으며, 게시글/댓글/좋아요 등 이벤트에서 자동 생성됨
    '''
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        '''
        현재 로그인한 사용자의 알림 목록만 조회.
        '''
        return Notification.objects.filter(receiver=self.request.user)

    #안읽은알림
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        '''
        읽지 않은 알림 개수를 조회하는 커스텀 액션
        동작: 현재 로그인한 사용자의 알림 중 is_read=false인 개수만 셈, 숫자 형태로 응답.
        '''
        count = Notification.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'unread_count': count})

    #알림읽음
    @action(detail=True, methods=['patch'], url_path='mark-read')
    def mark_as_read(self, request, pk=None):
        '''
        특정 알림을 읽음 상태로 처리하는 커스텀 액션
        동작: 1. 알림id(pk)를 통해 notification 인스턴스 조회 2. 이 알림의 수신자가 현재 사용자와 동일한지 확인. 3. 맞으면 is_read=true로 설정하고 저장.
        '''
        notification = self.get_object()

        if notification.receiver != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()
        return Response({'detail': '읽음 처리 완료'})
