from rest_framework import serializers
from .models import Post, Comment, Like

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']
    
    def create(self, validated_data):
        user = self.context['user']
        post = self.context['post']
        return Comment.objects.create(user=user, post=post, **validated_data)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    comments = CommentSerializer(many=True, read_only=True)
    likes_objs = LikeSerializer(many=True, read_only=True, source='post_likes')
    like_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'image', 'caption', 'created_at', 'like_count', 'likes_objs', 'comments_count', 'comments']
        
    def get_like_count(self, obj):
        return obj.likes if obj.likes else 0
    
    def get_comments_count(self, obj):
        return obj.comments.count() if obj.comments else 0
    

