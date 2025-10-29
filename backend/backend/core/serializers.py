from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PhishingReport, DomainReputation, ReputationToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class PhishingReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)

    class Meta:
        model = PhishingReport
        fields = ['id', 'reporter', 'domain', 'incident_hash', 'description', 'detected_at', 'verified']


class DomainReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainReputation
        fields = ['domain', 'reputation_score', 'last_updated']


class ReputationTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ReputationToken
        fields = ['user', 'tokens']
