from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LikeView, UnlikeView

router = DefaultRouter()
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
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

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', views.PostViewSet.as_view({'get': 'feed'}), name='feed'),
    path('posts/<int:pk>/like/', LikeView.as_view(), name='like'),
    path('posts/<int:pk>/unlike/', UnlikeView.as_view(), name='unlike'),
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

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('unread-count/', views.NotificationUnreadCountView.as_view(), name='unread_count'),
]