from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['id'] = user.id
        # token['role'] = user.role
        return token
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id",'username', 'email','password','first_name','last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_2fa_completed': {'read_only': True},  # Make read-only
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            # role=validated_data.get('role')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id",'email', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'is_2fa_completed': {'read_only': True},  # Make read-only
        }
