from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = Post.objects.get(id=self.kwargs['post_id'])
        context['user'] = self.request.user
        return context


class LikePostView(generics.GenericAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        existing_like = Like.objects.filter(post=post, user=user).first()

        if existing_like:
            # User already liked this post, unlike it
            existing_like.delete()
            post.likes = max(0, post.likes - 1)  # Prevent negative likes
            post.save()
            return response.Response({'status': 'post unliked'}, status=status.HTTP_200_OK)
        else:
            # User has not liked this post yet, like it
            Like.objects.create(post=post, user=user)
            post.likes += 1
            post.save()
            return response.Response({'status': 'post liked'}, status=status.HTTP_200_OK)