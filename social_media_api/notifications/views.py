from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

# Create your views here.


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        # Mark all notifications as read when user views them
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return super().get(request, *args, **kwargs)

class NotificationUnreadCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, read=False).count()
        return Response({'unread_count': count})