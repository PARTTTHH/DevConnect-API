from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, Skill, Follow, ConnectionRequest
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserPublicSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    SkillSerializer,
    FollowSerializer,
    ConnectionRequestSerializer
)
from core.permissions import IsOwnerOrReadOnly


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint returning JWT Access and Refresh tokens with customized claims.
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Registers a new user (Developer or Recruiter) and automatically issues JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for instant session initialization
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response({
            'success': True,
            'message': 'User registered successfully.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    Logs out user by blacklisting the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}})
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'success': True, 'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the profile of the currently logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserPublicSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change user password securely.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'success': True, 'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class DeveloperListView(generics.ListAPIView):
    """
    List and search developers with filtering by skills, availability, and keyword search.
    """
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_available_for_hire', 'is_verified', 'location']
    search_fields = ['username', 'headline', 'bio', 'location', 'skills__name']
    ordering_fields = ['created_at', 'username']

    def get_queryset(self):
        queryset = User.objects.prefetch_related('skills').all()
        skill_param = self.request.query_params.get('skill')
        if skill_param:
            queryset = queryset.filter(skills__name__icontains=skill_param)
        return queryset


class DeveloperDetailView(generics.RetrieveAPIView):
    """
    Retrieve public details of a specific developer by username.
    """
    queryset = User.objects.prefetch_related('skills').all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


class FollowToggleView(APIView):
    """
    Follow or unfollow a developer by username.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        if target_user == request.user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance = Follow.objects.filter(follower=request.user, following=target_user).first()
        if follow_instance:
            follow_instance.delete()
            return Response({
                'is_following': False,
                'message': f'Unfollowed {target_user.username}.',
                'followers_count': target_user.followers_count
            }, status=status.HTTP_200_OK)
        else:
            Follow.objects.create(follower=request.user, following=target_user)
            # Create notification
            from notifications.models import Notification
            Notification.objects.create(
                recipient=target_user,
                actor=request.user,
                verb='started following you',
                notification_type='FOLLOW'
            )
            return Response({
                'is_following': True,
                'message': f'Now following {target_user.username}.',
                'followers_count': target_user.followers_count
            }, status=status.HTTP_201_CREATED)


class FollowersListView(generics.ListAPIView):
    """
    List followers of a specific user.
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Follow.objects.filter(following=user).select_related('follower')


class FollowingListView(generics.ListAPIView):
    """
    List users that a specific user is following.
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Follow.objects.filter(follower=user).select_related('following')


class SkillListCreateView(generics.ListCreateAPIView):
    """
    List existing skills or add new skills (Admin/Authenticated).
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']


class ConnectionRequestListCreateView(generics.ListCreateAPIView):
    """
    List received connection requests or send a new connection request.
    """
    serializer_class = ConnectionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filter_type = self.request.query_params.get('type', 'received')
        if filter_type == 'sent':
            return ConnectionRequest.objects.filter(sender=self.request.user)
        return ConnectionRequest.objects.filter(receiver=self.request.user)

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver')
        if not receiver_id:
            return Response({'receiver': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        receiver = get_object_or_404(User, id=receiver_id)
        if receiver == request.user:
            return Response({'error': 'You cannot send a connection request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = ConnectionRequest.objects.filter(sender=request.user, receiver=receiver).first()
        if existing:
            return Response({'error': f'Connection request already exists with status: {existing.status}'}, status=status.HTTP_400_BAD_REQUEST)

        conn = ConnectionRequest.objects.create(
            sender=request.user,
            receiver=receiver,
            message=request.data.get('message', '')
        )

        from notifications.models import Notification
        Notification.objects.create(
            recipient=receiver,
            actor=request.user,
            verb='sent you a connection request',
            notification_type='CONNECTION_REQUEST'
        )

        serializer = self.get_serializer(conn)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConnectionRequestActionView(APIView):
    """
    Accept or Reject a received connection request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, action):
        conn = get_object_or_404(ConnectionRequest, pk=pk, receiver=request.user)
        if action == 'accept':
            conn.status = 'ACCEPTED'
            conn.save()
            from notifications.models import Notification
            Notification.objects.create(
                recipient=conn.sender,
                actor=request.user,
                verb='accepted your connection request',
                notification_type='CONNECTION_ACCEPTED'
            )
            return Response({'status': 'ACCEPTED', 'message': 'Connection request accepted.'})
        elif action == 'reject':
            conn.status = 'REJECTED'
            conn.save()
            return Response({'status': 'REJECTED', 'message': 'Connection request rejected.'})
        return Response({'error': 'Invalid action. Use accept or reject.'}, status=status.HTTP_400_BAD_REQUEST)
