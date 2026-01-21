from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Team, TeamMember, TeamInvite
from .serializers import TeamSerializer, TeamInviteSerializer, JoinTeamSerializer
from .permissions import IsTeamAdmin

class TeamCreateView(generics.CreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeamInviteCreateView(generics.CreateAPIView):
    serializer_class = TeamInviteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        self.team = Team.objects.get(id=kwargs["team_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated, IsTeamAdmin]
        return super().get_permissions()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["team"] = self.team
        return ctx


class JoinTeamView(generics.GenericAPIView):
    serializer_class = JoinTeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data["code"]

        invite = TeamInvite.objects.filter(code=code, is_active=True).first()
        if not invite or not invite.can_be_used():
            return Response({"detail": "Code invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        TeamMember.objects.get_or_create(team=invite.team, user=request.user, defaults={"role": TeamMember.Role.MEMBER})
        invite.uses_count += 1
        invite.save(update_fields=["uses_count"])

        return Response({"team_id": str(invite.team.id), "team_name": invite.team.name})
