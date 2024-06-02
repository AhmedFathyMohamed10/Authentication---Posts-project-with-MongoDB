import re #FOR MAKING MATCH IN PASSWORD
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # Validate username
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username is already taken."})

        # Validate the email
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use.")

        # Validate password
        password = data.get('password')
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise serializers.ValidationError({"password": "Password must contain at least 8 characters, including an uppercase letter, a lowercase letter, a number, and a special character."})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        # Check for at least one lowercase letter, one uppercase letter, one digit, and one symbol
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise serializers.ValidationError(
                "Password must contain at least 8 characters, including an uppercase letter, a lowercase letter, a number, and a special character."
            )
        return value

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "The new password cannot be the same as the old password."})
        
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
