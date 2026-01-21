from rest_framework.permissions import BasePermission
from .models import TeamMember

class IsTeamAdmin(BasePermission):
    def has_permission(self, request, view):
        team = getattr(view, "team", None)
        if team is None:
            return False
        return TeamMember.objects.filter(team=team, user=request.user, role=TeamMember.Role.ADMIN).exists()
