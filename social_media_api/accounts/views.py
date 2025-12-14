from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from django.shortcuts import get_object_or_404
from .serializers import FollowSerializer, UserProfileSerializer
# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=400)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user



class FollowView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        
        if user_to_follow == request.user:
            return Response({'error': 'You cannot follow yourself'}, status=400)
        
        request.user.follow(user_to_follow)
        
        # Create notification for followed user
        Notification.objects.create(
            recipient=user_to_follow,
            actor=request.user,
            verb="started following you"
        )
        
        return Response({'message': f'You are now following {user_to_follow.username}'})

class UnfollowView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
        request.user.unfollow(user_to_unfollow)
        return Response({'message': f'You have unfollowed {user_to_unfollow.username}'})

class FollowingListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.followers.all()

class FollowersListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CustomUser.objects.filter(followers=self.request.user)