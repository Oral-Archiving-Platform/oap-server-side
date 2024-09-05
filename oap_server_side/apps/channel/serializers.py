from rest_framework import serializers
from .models import Channel, ChannelMembership, Subscription, CollaborationInvitation
from apps.users.serializers import UserSerializer
from django.db import transaction
from django.db import IntegrityError
from apps.users.models import User

class ChannelSerializer(serializers.ModelSerializer):
    subscription_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'creationDate', 'icon', 'cover','subscription_count']
        read_only_fields = ['id', 'creationDate']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        channel = Channel.objects.create(**validated_data)
        ChannelMembership.objects.create(
            channelID=channel,
            userID=user,
            role=ChannelMembership.OWNER
        )
        return channel
    def get_subscription_count(self, obj):
        return Subscription.objects.filter(channelID=obj).count()



class ChannelMembershipSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(source='channelID', read_only=True)
    user = UserSerializer(source='userID', read_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = ChannelMembership
        fields = ['id', 'channel', 'user', 'role','channelID','email']
        read_only_fields = ['id']
        extra_kwargs = {
            'channelID': {'write_only': True},
        }
    def create(self, validated_data):
        print("gnos")
        email = validated_data.pop('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})
        
        validated_data['userID'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if set(validated_data.keys()) - {'role'}:
            raise serializers.ValidationError({"detail": "Only 'role' field can be updated."})
        return super().update(instance, validated_data)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['id', 'subscriptionDate','userID']

class CollaborationInvitationSerializer(serializers.ModelSerializer):
    channel_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    inviter_email = serializers.SerializerMethodField()

    class Meta:
        model = CollaborationInvitation
        fields = ['id', 'channel', 'channel_name', 'inviter', 'inviter_email', 'invitee_email', 'role', 'role_display', 'created_at', 'token', 'is_accepted']
        read_only_fields = ['id', 'created_at', 'token', 'is_accepted', 'inviter', 'channel_name', 'role_display', 'inviter_email']

    def get_channel_name(self, obj):
        return obj.channel.name

    def get_role_display(self, obj):
        return dict(ChannelMembership.ROLE_CHOICES)[obj.role]

    def get_inviter_email(self, obj):
        return obj.inviter.email

