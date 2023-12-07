from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from neighborapi.models import Post, Neighbor, PostType
from django.contrib.auth.models import User
from .categories import CategorySerializer
from .users import NeighborSerializer
from .postTypes import PostTypeSerializer
from .comments import SimpleCommentSerializer


class SimplePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            "post_type",
            "title",
            "image_url",
            "content",
            "approved",
            "categories",
        ]


class PostSerializer(serializers.ModelSerializer):
    author = NeighborSerializer(many=False)
    is_owner = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    post_type = PostTypeSerializer(many=False)
    comments = SimpleCommentSerializer(many=True, read_only=True)

    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        # return self.context["request"].user == obj.author.user
        request = self.context.get("request")
        if request:
            return request.user == obj.author.user
        return False

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "post_type",
            "title",
            "publication_date",
            "image_url",
            "content",
            "approved",
            "categories",
            "is_owner",
            "comments"
        ]


class PostViewSet(viewsets.ViewSet):
    def list(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post, context={"request": request})
            return Response(serializer.data)

        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        author = Neighbor.objects.get(user=request.auth.user)
        post_type = PostType.objects.get(pk=request.data["post_type"])
        title = request.data.get("title")
        publication_date = request.data.get("publication_date")
        event_date = request.dat.get("event_date")
        image_url = request.data.get("image_url")
        content = request.data.get("content")
        approved = request.data.get("approved")
        accept_rsvp = request.data.get("accept_rsvp")

        # Create a post database row first, so you have a
        # primary key to work with
        post = Post.objects.create(
            # maybe issues with rare_user /  request.user
            author=author,
            post_type=post_type,
            title=title,
            publication_date=publication_date,
            event_date=event_date,
            image_url=image_url,
            content=content,
            approved=approved,
            accept_rsvp=accept_rsvp
        )

        # Establish the many-to-many relationships
        category_ids = request.data.get("categories", [])
        post.tags.set(category_ids)

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this post?
            self.check_object_permissions(request, post)

            serializer = SimplePostSerializer(data=request.data)
            if serializer.is_valid():
                post.post_type = serializer.validated_data["post_type"]
                post.title = serializer.validated_data["title"]
                post.image_url = serializer.validated_data["image_url"]
                post.content = serializer.validated_data["content"]
                post.approved = serializer.validated_data["approved"]
                post.save()

                category_ids = request.data.get("categories", [])
                post.tags.set(category_ids)

                serializer = PostSerializer(post, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            post.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
