from django.db import models
from django.contrib.auth.models import User


class PhishingReport(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    domain = models.CharField(max_length=255)
    incident_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash
    description = models.TextField(blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.domain} reported by {self.reporter.username} at {self.detected_at}"


class DomainReputation(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    reputation_score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.domain}: {self.reputation_score}"


class ReputationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tokens = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} has {self.tokens} RPT"
