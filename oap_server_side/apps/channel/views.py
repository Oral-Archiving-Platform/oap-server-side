from django.shortcuts import render
from rest_framework import viewsets
from .models import Channel, ChannelMembership, Subscription
from .serializers import ChannelSerializer,ChannelMembershipSerializer,SubscriptionSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

class ChannelMembershipViewSet(viewsets.ModelViewSet):
    queryset = ChannelMembership.objects.all()
    serializer_class = ChannelMembershipSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer