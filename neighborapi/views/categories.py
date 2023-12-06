from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from neighborapi.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "label"]


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        tags = Category.objects.all()
        serializer = CategorySerializer(tags, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        label = request.data.get("label")

        # Create a comment database row first, so you have a
        # primary key to work with
        category = Category.objects.create(
            # maybe issues with label /  request.user
            label=label
        )

        serializer = CategorySerializer(category, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this tag
            self.check_object_permissions(request, category)

            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                category.label = serializer.validated_data["label"]
                # tag.created_on = serializer.validated_data["created_on"]
                category.save()

                serializer = CategorySerializer(category, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            self.check_object_permissions(request, category)
            category.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
