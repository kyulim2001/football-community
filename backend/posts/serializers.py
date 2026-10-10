from rest_framework import serializers
from .models import Post, Comment, Report, Board, PostMedia
from accounts.models import User
from accounts.serializers import UserSerializer


class PostMediaSerializer(serializers.ModelSerializer): # 첨부파일용 시리얼라이저
    file = serializers.SerializerMethodField() # 단순히 모델의 file 필드로 직렬화하는것이 아닌, 커스텀 메서드를 사용해 처리
    # 파일 필드의 실제 내용 대신, 특정한 가공된 형태(url)로 출력하려는 의도
    
    class Meta: # 어떤 모델을 기반으로 직렬화할지, 어떤 필드를 포함할지 정의
        model = PostMedia # 이 serializer가 직렬화할 모델 클래스는 postmedia
        fields = ['id', 'file'] # api 응답시 url포함 id,file 필드만 보여줌
    
    def get_file(self, obj): # 위의 메서드에 대응되는 메서드
        request = self.context.get('request') # serializer의 context에서 http 요청 객체를 가져옴 보통 view에서 호출될 때 context로 request를 전달받음
        if request: # request 객체가 존재한다면
            return request.build_absolute_uri(obj.file.url) # 상대경로를 url로 바꿔줌. 이러면 클라이언트가 직접 접근 가능한 url이 응답으로 제공됨
        return obj.file.url # 첨부파일의 상대 경로

class PostSerializer(serializers.ModelSerializer): # 게시글을 직렬화하는 시리얼라이저
    user = UserSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True) # 첨부파일을 직렬화해서 media라는 배열로 응답
    like = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    dislike = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    files = serializers.ListField( # 클라이언트에서 파일을 여러개 업로드하기 위한 필드
        child = serializers.FileField(),
        write_only = True, # 응답에는 안 보이고 쓰기 전용
        required = False
    )
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField() # 댓글수, 좋아요수, 싫어요 수는 계산해서 보여줌
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all()) # 게시판 정보를 id로 받음
    has_image = serializers.SerializerMethodField()
    # author_nickname = serializers.CharField(source = 'user.nickname', read_only=True)
    author_nickname = serializers.SerializerMethodField()
    board_name = serializers.CharField(source='board.name', read_only=True)
    
    def get_author_nickname(self, obj):
        if obj.user is None or not obj.user.is_active:
            return "탈퇴한 회원"
        return obj.user.nickname
    
    def get_like_count(self, obj):
        return obj.like.count()
    
    def get_dislike_count(self, obj):
        return obj.dislike.count()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'created_at', 'updated_at', 'user', 'content', 'views', 'like', 'dislike',
                  'board', 'media', 'files', 'comment_count', 'like_count', 'dislike_count', 'has_image', 'author_nickname',
                  'board_name']
        
    def get_comment_count(self, obj):
        return obj.comment_set.count()
        
    def create(self, validated_data):
        files = validated_data.pop('files', []) # 유효성 검사를 통과한 데이터 중에 files라는 키가 있으면 files에 저장하고 validated_data에선 제거 없으면 []
        post = Post.objects.create(**validated_data) # validated_data에 남은 데이터를 사용해 post 객체를 생성 ** 는 키-값 쌍을 전달하는 문법
        
        for file in files: # 아까 꺼내는 files 리스트를 순회하면서 각각의 파일을 처리
            PostMedia.objects.create(post=post, file=file) # 각 파일에 대해 postmedia 객체를 생성하고, post와 연결하고 file을 저장함
            
        return post # 최종적으로 생성된 post 객체를 반환
    
    def to_internal_value(self, data): # 외부에서 들어온 데이터를 내부 파이썬 표현으로 변환
        if 'board' in data and isinstance(data['board'], str): # 데이터에 board라는 키가 있고 그 값이 문자열인 경우
            try:
                data['board'] = int(data['board']) # 문자열로 들어온 값을 정수형으로 변환
            except ValueError:
                pass
        return super().to_internal_value(data) # 나머지 처리는 drf 기본 동작에 맡김
    
    def get_has_image(self, obj):
        return obj.media.exists()
    
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source = 'user.nickname', read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset = Comment.objects.all(), allow_null = True, required = False)
    replies = serializers.SerializerMethodField()
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author_nickname = serializers.CharField(source = 'user.nickname', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    author_nickname = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'author_username', 'parent', 'replies', 'post', 'is_deleted', 'author_nickname', 'post_title']
        read_only_fields = ['user', 'author_username', 'replies']
        
    def get_replies(self, obj):
        children = obj.replies.all().order_by('created_at')
        return CommentSerializer(children, many = True, context = self.context).data
    
    def get_author_nickname(self, obj):
        if obj.user is None or not obj.user.is_active:
            return "탈퇴한 회원"
        return obj.user.nickname

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'created_at']
        

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
        
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_type', 'object_id', 'reason', 'reporter', 'created_at']
        read_only_fields = ['reporter', 'created_at']
        
