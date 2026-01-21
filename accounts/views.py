from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Créer catégories de base pour l'utilisateur
        from checklists.models import Category
        defaults = ["Général", "Son", "Vidéo", "Lumière"]
        for name in defaults:
            Category.objects.get_or_create(
                user=user,
                name=name,
                defaults={"is_default": True}
            )
