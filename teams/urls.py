from django.urls import path
from .views import TeamCreateView, TeamInviteCreateView, JoinTeamView

urlpatterns = [
    path("teams/", TeamCreateView.as_view(), name="team-create"),
    path("teams/<uuid:team_id>/invites/", TeamInviteCreateView.as_view(), name="team-invite-create"),
    path("teams/join/", JoinTeamView.as_view(), name="team-join"),
]
