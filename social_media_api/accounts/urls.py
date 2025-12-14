from django.urls import path
from . import views
from .views import FollowView, UnfollowView, FollowingListView, FollowersListView 
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('follow/<int:user_id>/', FollowView.as_view(), name='follow'),
    path('unfollow/<int:user_id>/', UnfollowView.as_view(), name='unfollow'),
    path('following/', FollowingListView.as_view(), name='following'),
    path('followers/', FollowersListView.as_view(), name='followers'),
]



router = DefaultRouter()
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', views.PostViewSet.as_view({'get': 'feed'}), name='feed'),
    path('posts/<int:post_id>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('posts/<int:post_id>/comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]