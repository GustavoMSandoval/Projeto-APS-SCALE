from django.contrib import admin
from .models import (
    UserProfile, EmergyReference, Project, 
    Process, InventoryItem, CalculationResult, ImportLog, Institution
)

admin.site.register(UserProfile)
admin.site.register(EmergyReference)
admin.site.register(Project)
admin.site.register(Process)
admin.site.register(InventoryItem)
admin.site.register(CalculationResult)
admin.site.register(ImportLog)
admin.site.register(Institution)