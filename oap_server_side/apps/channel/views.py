from django.shortcuts import render
from rest_framework import viewsets
from .models import Channel, ChannelMembership, Subscription, CollaborationInvitation
from .serializers import ChannelSerializer,ChannelMembershipSerializer,SubscriptionSerializer,CollaborationInvitationSerializer
from .permissions import IsChannelOwner
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import uuid
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from apps.media.models import Media
from apps.video.models import Video
from apps.channel.models import Channel
from apps.video.serializers import VideoSerializer



class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    
    def get_queryset(self): #get all channels of the usereven those where he is a member
        user = self.request.user
        return Channel.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['get'])
    def subscriptions(self, request, pk=None):
        channel = self.get_object()
        subscriptions = Subscription.objects.filter(channelID=channel)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
class ChanneVideolViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    # Other existing methods...

    @action(detail=True, methods=['get'], url_path='videos', permission_classes=[IsAuthenticated])
    def channel_videos(self, request, pk=None):
        """
        List all videos that belong to a specific channel based on channel ID.
        """
        # Get the channel by ID (pk)
        channel = get_object_or_404(Channel, id=pk)

        # Get the media entries that belong to this channel
        media_items = Media.objects.filter(channelID=channel)

        # Filter the videos based on the media items
        videos = Video.objects.filter(mediaID__in=media_items)

        # Serialize the video data
        serializer = VideoSerializer(videos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
 


class ChannelMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelMembershipSerializer
    permission_classes = [IsChannelOwner]

    def get_queryset(self):
        if self.request.method == 'GET':
            return ChannelMembership.objects.filter(userID=self.request.user)
        else:
            return ChannelMembership.objects.all()



    @action(detail=False, methods=['get'], url_path='channel/(?P<channel_id>[^/.]+)')
    def channel_members(self, request, channel_id=None): #get all members of a channel
        if not channel_id:
            return Response({"error": "channel_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({"error": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)

        if not ChannelMembership.objects.filter(channelID=channel, userID=request.user).exists():
            return Response({"error": "You are not a member of this channel"}, status=status.HTTP_403_FORBIDDEN)

        members = ChannelMembership.objects.filter(channelID=channel)
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='invite')
    def invite_collaborator(self, request):
        print(request.data)
        serializer = CollaborationInvitationSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save(
                inviter=request.user,
                token=str(uuid.uuid4())
            )
            self.send_invitation_email(invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_invitation_email(self, invitation):
        subject = f'Invitation to collaborate on {invitation.channel.name}'
        message = f'''
            Dear User,

            You have been invited to collaborate on the channel "{invitation.channel.name}" by {invitation.inviter.email}.

            To accept this invitation, please follow these steps:
            1. Log in to your account at {settings.FRONTEND_URL}
            2. Go to your account settings or dashboard
            3. Look for the "Accept Invitations" section
            4. Enter the following invitation token:

            {invitation.token}

            If you don't want to accept this invitation, you can safely ignore this email.

            If you have any questions or issues, please contact our support team.

            Best regards,
            OAP Team
            '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.invitee_email],
            fail_silently=False,
        )

    @action(detail=False, methods=['get', 'post'], url_path='accept-invitation/(?P<token>[^/.]+)', permission_classes=[IsAuthenticated])
    def accept_invitation(self, request, token=None):
        try:
            invitation = CollaborationInvitation.objects.get(token=token, is_accepted=False)
        except CollaborationInvitation.DoesNotExist:
            return Response({"error": "Invalid or expired invitation"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            serializer = CollaborationInvitationSerializer(invitation)
            return Response(serializer.data)

        invitation.is_accepted = True
        invitation.save()

        ChannelMembership.objects.create(
            channelID=invitation.channel,
            userID=request.user,
            role=invitation.role
        )

        self.send_acceptance_email(invitation)

        return Response({"message": "Invitation accepted successfully"}, status=status.HTTP_200_OK)

    def send_acceptance_email(self, invitation):
        subject = f'Collaboration invitation accepted for {invitation.channel.name}'
        message = f'''
        {invitation.invitee_email} has accepted your invitation to collaborate on the channel {invitation.channel.name}.
        
        They have been added as a {invitation.get_role_display()} to the channel.
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.inviter.email],
            fail_silently=False,
        )




    

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(userID=self.request.user)

    
    def perform_create(self, serializer):
        user = self.request.user
        channel = serializer.validated_data['channelID']
        existing_subscription = Subscription.objects.filter(channelID=channel, userID=user).first()
        
        if existing_subscription:
            existing_subscription.delete()
            return Response({'message': 'Unsubscribed successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer.save(userID=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    def get_queryset(self):
        # Get channels where the current user is the owner
        return Channel.objects.filter(
            channelmembership__userID=self.request.user,
        )


