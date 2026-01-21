import secrets
from rest_framework import serializers
from .models import Team, TeamMember, TeamInvite

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "created_by", "created_at")
        read_only_fields = ("id", "created_by", "created_at")

    def create(self, validated_data):
        request = self.context["request"]
        team = Team.objects.create(created_by=request.user, **validated_data)
        TeamMember.objects.create(team=team, user=request.user, role=TeamMember.Role.ADMIN)
        return team


class TeamInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvite
        fields = ("id", "team", "code", "is_active", "expires_at", "max_uses", "uses_count", "created_at")
        read_only_fields = ("id", "team", "code", "uses_count", "created_at")

    def create(self, validated_data):
        request = self.context["request"]
        team = self.context["team"]

        # code court
        code = secrets.token_hex(3).upper()  # ex: "A1B2C3"
        invite = TeamInvite.objects.create(
            team=team,
            created_by=request.user,
            code=code,
            **validated_data
        )
        return invite


class JoinTeamSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs["code"].strip().upper()
        attrs["code"] = code
        return attrs
