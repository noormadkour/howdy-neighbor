from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from neighborapi.models import PostType


class PostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostType
        fields = ["id", "type"]


class PostTypeViewSet(viewsets.ViewSet):
    def list(self, request):
        categories = PostType.objects.all()
        serializer = PostTypeSerializer(categories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            post_type = PostType.objects.get(pk=pk)
            serializer = PostTypeSerializer(post_type)
            return Response(serializer.data)
        except PostType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        type = request.data.get("type")

        # Create a comment database row first, so you have a
        # primary key to work with
        post_type = PostType.objects.create(
            # maybe issues with label /  request.user
            type=type
        )

        serializer = PostTypeSerializer(post_type, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            post_type = PostType.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this post_type?
            self.check_object_permissions(request, post_type)

            serializer = PostTypeSerializer(data=request.data)
            if serializer.is_valid():
                post_type.type = serializer.validated_data["type"]
                # post_type.created_on = serializer.validated_data["created_on"]
                post_type.save()

                serializer = PostTypeSerializer(post_type, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except PostType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            post_type = PostType.objects.get(pk=pk)
            self.check_object_permissions(request, post_type)
            post_type.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except PostType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
