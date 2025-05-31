from rest_framework import serializers
from .models import MeFollow
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

from django.contrib.auth import get_user_model

MeUser = get_user_model()

class MeFollowSerializer(serializers.ModelSerializer):
    """Суриализатор подписок"""
    class Meta:
        model = MeFollow
        fields = ['user', 'author']

    def validate(self, data):
        """ пользователь не подписывается на себя """
        if data['user'] == data['author']:
            raise serializers.ValidationError("Нельзя подписаться на самого себя")
        return data

class MeUserRegistrationSerializer(serializers.Serializer):
    """Суриализатор регистрации"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MeUser
        fields = ['username', 'last_name', 'first_name', 'password']

        extra_password = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        meuser = MeUser(**data)
        password = data.get('password')

        try:
            validate_password(password, meuser)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return data
        
    def create(self, validated_data):
        user = MeUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class MeUserSerializer(serializers.Serializer):
    """Сериализатор пользователя"""
    is_followers = serializers.SerializerMethodField()

    class Meta:
        model = MeUser
        fields = ['id', 'username', 'last_name', 'first_name', 'email', 'is_followers']

    def get_is_followers(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MeFollow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False
    
class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор изменения пароля"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
