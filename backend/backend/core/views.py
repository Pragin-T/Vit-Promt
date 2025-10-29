import os
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PhishingReport, DomainReputation, ReputationToken
from .serializers import (
    PhishingReportSerializer,
    DomainReputationSerializer,
    ReputationTokenSerializer,
    RegisterSerializer,
)
from .blockchain_service import submit_phishing_report
import binascii

# Path to store last_hash.txt in project root folder (where manage.py is)
HASH_FILE_PATH = os.path.join(settings.BASE_DIR, "last_hash.txt")

class PhishingReportViewSet(viewsets.ModelViewSet):
    queryset = PhishingReport.objects.all()
    serializer_class = PhishingReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

class DomainReputationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DomainReputation.objects.all()
    serializer_class = DomainReputationSerializer
    permission_classes = [permissions.AllowAny]

class ReputationTokenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReputationToken.objects.all()
    serializer_class = ReputationTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReputationToken.objects.filter(user=self.request.user)

class SubmitPhishingReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            report_hash_hex = request.data.get("report_hash")
            domain_hash_hex = request.data.get("domain_hash")
            if not report_hash_hex or not domain_hash_hex:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
            report_hash = binascii.unhexlify(report_hash_hex[2:] if report_hash_hex.startswith("0x") else report_hash_hex)
            domain_hash = binascii.unhexlify(domain_hash_hex[2:] if domain_hash_hex.startswith("0x") else domain_hash_hex)
            sender_address = request.user.ethereum_address  # custom user field
            private_key = "YOUR_BACKEND_SIGNING_PRIVATE_KEY"  # Replace securely in production
            tx_hash = submit_phishing_report(report_hash, domain_hash, private_key, sender_address)
            return Response({"tx_hash": tx_hash}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LastHashView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            with open(HASH_FILE_PATH, "r") as f:
                last_hash = f.read().strip()
            return Response({"last_hash": last_hash})
        except FileNotFoundError:
            return Response({"last_hash": ""}, status=status.HTTP_200_OK)

    def post(self, request):
        new_hash = request.data.get("hash")
        if not new_hash:
            return Response({"error": "No hash provided"}, status=status.HTTP_400_BAD_REQUEST)
        with open(HASH_FILE_PATH, "w") as f:
            f.write(new_hash)
        return Response({"message": "Hash updated.", "last_hash": new_hash}, status=status.HTTP_200_OK)
