import uuid
from django.conf import settings
from django.db import models
from django.db.models import TextChoices
from teams.models import Team


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'name')
        
    def __str__(self):
        return f"{self.name} ({self.user})"
    
class ChecklistTemplate(models.Model):
    class Visibility(TextChoices):
        PERSONAL = 'PERSONAL', 'Personal'
        TEAM = 'TEAM', 'Team'
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='templates')
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PERSONAL)
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='templates_owned')
    owner_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='templates')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        # A implémenter plus tard 
        pass
    
    def __str__(self):
        return self.title

class ChecklistTemplateItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name='items')
    label = models.CharField(max_length=200)
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        
    def __str__(self):
        return self.label