from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from neighborapi.models import Comment, Neighbor, Post
from .users import NeighborSerializer


class SimpleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "author",
            "post",
            "content",
        ]


class CommentSerializer(serializers.ModelSerializer):
    # !Unsure of which user serializer to use. Don't forget to import UserSerializer from .users
    # user = UserSerializer(many=False)
    author = NeighborSerializer(many=False)
    is_owner = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    def get_post(self, obj):
        from .posts import PostSerializer
        request = self.context.get("request")
        return PostSerializer(obj.post, context={"request":request}).data

    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        # return self.context["request"].user == obj.neighbor.user
        request = self.context.get("request")
        if request:
            return request.user == obj.author.user
        return False

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "content",
            "is_owner",
            "created_on",
        ]
        # read_only_field = ["user"]


class CommentViewSet(viewsets.ViewSet):
    def list(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
            context={"request": request}
            serializer = CommentSerializer(comment, context=context)
            return Response(serializer.data)

        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        post = Post.objects.get(pk=request.data["post"])
        author = Neighbor.objects.get(user=request.auth.user)
        content = request.data.get("content")
        created_on = request.data.get("created_on")

        # Create a comment database row first, so you have a
        # primary key to work with
        comment = Comment.objects.create(
            # maybe issues with post /  request.user
            post=post,
            author=author,
            content=content,
            created_on=created_on,
        )

        serializer = CommentSerializer(comment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this comment?
            self.check_object_permissions(request, comment)

            serializer = SimpleCommentSerializer(data=request.data)
            if serializer.is_valid():
                comment.post = serializer.validated_data["post"]
                comment.author = serializer.validated_data["author"]
                comment.content = serializer.validated_data["content"]
                # comment.created_on = serializer.validated_data["created_on"]
                comment.save()

                serializer = CommentSerializer(comment, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(request, comment)
            comment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
