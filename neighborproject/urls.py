from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from neighborapi.views import UserViewSet, PostTypeViewSet, PostViewSet, CategoryViewSet, CommentViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"posts", PostViewSet, "post")
router.register(r"categories", CategoryViewSet, "category")
router.register(r"posttypes", PostTypeViewSet, "posttype")
router.register(r"comments", CommentViewSet, "comment")
router.register(r"users", UserViewSet, "user")




urlpatterns = [
    path('', include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

