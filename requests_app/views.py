from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import (
    ChatRoomStatusChoices,
    ChatSenderChoices,
    ChatMessageTypeChoices,
    StatusChoices,
    SupportRequest,
    SupportRequestChatMessage,
)
from .serializers import (
    SupportRequestChatMessageCreateSerializer,
    SupportRequestChatMessageSerializer,
    SupportRequestSerializer,
    SupportRequestStatusUpdateSerializer,
)


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
        if self.action == "chat_messages":
            if self.request.method == "POST":
                return SupportRequestChatMessageCreateSerializer
            return SupportRequestChatMessageSerializer
        return SupportRequestSerializer

    def get_parser_classes(self):
        if self.action == "chat_messages" and self.request.method == "POST":
            return [MultiPartParser, FormParser, JSONParser]
        return [JSONParser]

    def get_chat_token(self, request):
        return request.headers.get("X-Chat-Token") or request.query_params.get("token")

    def get_room_and_role(self, support_request, request):
        if not hasattr(support_request, "chat_room"):
            raise PermissionDenied("Chat room not found.")

        room = support_request.chat_room
        token = self.get_chat_token(request)

        if not token:
            raise PermissionDenied("Chat token is required.")

        if str(room.customer_token) == str(token):
            return room, ChatSenderChoices.CUSTOMER

        if str(room.operator_token) == str(token):
            return room, ChatSenderChoices.OPERATOR

        raise PermissionDenied("Invalid chat token.")

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

    @action(detail=True, methods=["get"], url_path="chat")
    def chat_room(self, request, pk=None):
        support_request = self.get_object()
        room, role = self.get_room_and_role(support_request, request)

        return Response(
            {
                "room_id": room.id,
                "request_id": support_request.id,
                "status": room.status,
                "role": role,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"], url_path="chat/messages")
    def chat_messages(self, request, pk=None):
        support_request = self.get_object()
        room, role = self.get_room_and_role(support_request, request)

        if request.method == "GET":
            serializer = SupportRequestChatMessageSerializer(
                room.messages.all(),
                many=True,
                context=self.get_serializer_context(),
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        if room.status == ChatRoomStatusChoices.CLOSED:
            return Response(
                {"detail": "Chat room is closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save(
            chat_room=room,
            sender=role,
        )

        return Response(
            SupportRequestChatMessageSerializer(
                message,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="chat/complete")
    def complete_chat(self, request, pk=None):
        support_request = self.get_object()
        room, role = self.get_room_and_role(support_request, request)

        if role != ChatSenderChoices.OPERATOR:
            raise PermissionDenied("Only operator can complete the chat.")

        if room.status == ChatRoomStatusChoices.CLOSED:
            return Response(
                {"detail": "Chat room already closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SupportRequestChatMessage.objects.create(
            chat_room=room,
            sender=ChatSenderChoices.SYSTEM,
            message_type=ChatMessageTypeChoices.SYSTEM,
            message="Your request has been completed. Thank you.",
        )

        room.status = ChatRoomStatusChoices.CLOSED
        room.save(update_fields=["status", "updated_at"])

        support_request.status = StatusChoices.COMPLETED
        support_request.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "detail": "Chat room closed and request completed.",
                "request_id": support_request.id,
                "chat_status": room.status,
                "request_status": support_request.status,
            },
            status=status.HTTP_200_OK,
        )