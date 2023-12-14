from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from neighborapi.models import Neighbor



class UserSerializer(serializers.ModelSerializer):   

    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name", "email",]
        extra_kwargs = {"password": {"write_only": True}}


class NeighborSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    full_name = serializers.SerializerMethodField()
    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = Neighbor
        fields = ("id", "user", "active", "profile_image", "bio", "address", "full_name")


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register_account(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                email=serializer.validated_data["username"],
            )
            neighbor = Neighbor.objects.create(
                user=user,
                active=True,
                profile_image= request.data.get("profile_image"),
                bio= request.data.get("bio"),
                address=request.data.get("address")
            )
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'valid': True,
                'token': token.key,
                'user_id': user.id,
                'neighbor_id': neighbor.id,
                'admin': user.is_superuser,
                'name': user.first_name
            }
            # return Response({"token": token.key}, status=status.HTTP_201_CREATED)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def user_login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token = Token.objects.get(user=user)
            neighbor = Neighbor.objects.get(user=user)
            data = {
                'valid': True,
                'token': token.key,
                'user_id': user.id,
                # user image
                'neighbor_id': neighbor.id,
                'admin': user.is_superuser,
                'name': user.first_name
            }
            # return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        try:
            neighbor = Neighbor.objects.get(pk=pk)
            serialized = NeighborSerializer(neighbor)
            return Response(serialized.data)

        except Neighbor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)