from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'grade',
            'profile_photo',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            grade=validated_data.get('grade'),
            profile_photo=validated_data.get('profile_photo'),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'grade',
            'profile_photo',
            'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'profile_photo']

    def update(self, instance, validated_data):
        if 'profile_photo' in validated_data:
            # Delete old photo if it exists
            if instance.profile_photo:
                instance.profile_photo.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance