from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from neighborapi.models import Post, Neighbor, PostType
from django.contrib.auth.models import User
from .categories import CategorySerializer
from .users import NeighborSerializer
from .postTypes import PostTypeSerializer


class SimplePostSerializer(serializers.ModelSerializer):
    # is_owner = serializers.SerializerMethodField()

    # def get_is_owner(self, obj):
    #     # Check if the authenticated user is the owner
    #     return self.context["request"].user == obj.rare_user.user

    class Meta:
        model = Post
        fields = [
            "post_type",
            "title",
            "image_url",
            "content",
            "approved",
            "categories",
            # "is_owner",
        ]


class PostSerializer(serializers.ModelSerializer):
    neighbor = NeighborSerializer(many=False)
    is_owner = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    post_types = PostTypeSerializer(many=False)

    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        return self.context["request"].user == obj.neighbor.user

    class Meta:
        model = Post
        fields = [
            "id",
            "neighbor",
            "post_type",
            "title",
            "publication_date",
            "image_url",
            "content",
            "approved",
            "categories",
            "is_owner",
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
        neighbor = Neighbor.objects.get(user=request.auth.user)
        post_type = PostType.objects.get(pk=request.data["type"])
        title = request.data.get("title")
        publication_date = request.data.get("publication_date")
        image_url = request.data.get("image_url")
        content = request.data.get("content")
        approved = request.data.get("approved")

        # Create a post database row first, so you have a
        # primary key to work with
        post = Post.objects.create(
            # maybe issues with rare_user /  request.user
            neighbor=neighbor,
            post_type=post_type,
            title=title,
            publication_date=publication_date,
            image_url=image_url,
            content=content,
            approved=approved,
        )

        # Establish the many-to-many relationships
        tag_ids = request.data.get("tags", [])
        post.tags.set(tag_ids)

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this post?
            self.check_object_permissions(request, post)

            serializer = SimplePostSerializer(data=request.data)
            if serializer.is_valid():
                # post.rare_user = serializer.validated_data["rare_user"]
                post.category = serializer.validated_data["category"]
                post.title = serializer.validated_data["title"]
                # post.publication_date = serializer.validated_data["publication_date"]
                post.image_url = serializer.validated_data["image_url"]
                post.content = serializer.validated_data["content"]
                post.approved = serializer.validated_data["approved"]
                post.save()

                tag_ids = request.data.get("tags", [])
                post.tags.set(tag_ids)

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
