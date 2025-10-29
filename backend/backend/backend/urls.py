from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import (
    PhishingReportViewSet,
    DomainReputationViewSet,
    ReputationTokenViewSet,
    SubmitPhishingReportView,
    RegisterView,
    LastHashView,   # Added this import
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'phishing-reports', PhishingReportViewSet, basename='phishingreport')
router.register(r'domain-reputations', DomainReputationViewSet, basename='domainreputation')
router.register(r'reputation-tokens', ReputationTokenViewSet, basename='reputationtoken')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/submit-report/', SubmitPhishingReportView.as_view(), name='submit-phishing-report'),
    path('api/last-hash/', LastHashView.as_view(), name='last-hash'),  # Added API endpoint here
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
