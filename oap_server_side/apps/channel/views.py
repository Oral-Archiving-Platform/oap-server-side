from django.shortcuts import render
from rest_framework import viewsets
from .models import Channel, ChannelMembership, Subscription
from .serializers import ChannelSerializer,ChannelMembershipSerializer,SubscriptionSerializer
from .permissions import IsChannelOwner
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
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


class ChannelMembershipViewSet(viewsets.ModelViewSet):
    queryset = ChannelMembership.objects.all()
    serializer_class = ChannelMembershipSerializer
    permission_classes = [IsChannelOwner]

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


        


