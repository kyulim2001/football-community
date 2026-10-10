from rest_framework import viewsets
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatMessage.objects.all().order_by('timestamp')
    serializer_class = ChatMessageSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='room/(?P<room_name>[^/.]+)')
    def by_room(self, request, room_name=None):
        messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
