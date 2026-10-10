from django import forms
from .models import Post, Comment, Image

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder':'댓글을 입력하세요'})
    }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file',]

ImageFormSet = forms.inlineformset_factory(Post, Image, form = ImageForm, extra = 3)