from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SupportRequest
from .serializers import SupportRequestSerializer, SupportRequestStatusUpdateSerializer


class SupportRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = SupportRequest.objects.all().order_by("-created_at")
    serializer_class = SupportRequestSerializer

    def get_serializer_class(self):
        if self.action == "update_status":
            return SupportRequestStatusUpdateSerializer
        return SupportRequestSerializer

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            SupportRequestSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )
