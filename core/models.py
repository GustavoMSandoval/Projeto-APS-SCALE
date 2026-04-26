from django.db import models
from django.contrib.auth.models import User

class Institution(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return self.user.username

class EmergyReference(models.Model):
    resource_name = models.CharField(max_length=150, unique=True)
    unit = models.CharField(max_length=50)
    uev_value = models.FloatField()
    source = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Emergy Reference"
        verbose_name_plural = "Emergy References"

    def __str__(self):
        return f"{self.resource_name} ({self.uev_value})"

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_emergy = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

class Process(models.Model):
    project = models.ForeignKey(Project, related_name='processes', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    matrix_index = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    process = models.ForeignKey(Process, related_name='items', on_delete=models.CASCADE)
    resource_name = models.CharField(max_length=150)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    reference = models.ForeignKey(EmergyReference, on_delete=models.SET_NULL, null=True, blank=True)
    applied_uev = models.FloatField()
    calculated_emergy = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

class CalculationResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    leontief_matrix_json = models.JSONField(null=True, blank=True)
    sustainability_indicators = models.JSONField(null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Calculation Result"
        verbose_name_plural = "Calculation Results"

class ImportLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    imported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    error_messages = models.TextField(blank=True)

    class Meta:
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"