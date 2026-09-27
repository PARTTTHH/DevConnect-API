from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    List notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unread_only = self.request.query_params.get('unread')
        queryset = Notification.objects.filter(recipient=self.request.user).select_related('actor')
        if unread_only and unread_only.lower() in ['true', '1']:
            queryset = queryset.filter(is_read=False)
        return queryset


class NotificationMarkReadView(APIView):
    """
    Mark a specific notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'success': True, 'message': 'Notification marked as read.'})


class NotificationMarkAllReadView(APIView):
    """
    Mark all notifications as read for current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'success': True, 'message': 'All notifications marked as read.'})


class NotificationUnreadCountView(APIView):
    """
    Get unread notification count for badge display.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})
