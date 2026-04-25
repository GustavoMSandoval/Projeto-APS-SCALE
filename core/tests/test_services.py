from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from core.models import Project, EmergyReference, InventoryItem
from core.services import import_data
import io
import pandas as pd

class ServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='worker', password='password')
        self.project = Project.objects.create(user=self.user, name='Import Test')
        EmergyReference.objects.create(
            resource_name='Solar Energy', 
            uev_value=1.0, 
            unit='J'
        )

    def test_import_data_csv(self):
        content = "Resource,Quantity,Unit,Process\nSolar Energy,1000,J,Nature"
        csv_file = SimpleUploadedFile("test.csv", content.encode('utf-8'), content_type="text/csv")
        
        count = import_data(csv_file, self.project)
        
        self.assertEqual(count, 1)
        item = InventoryItem.objects.get(resource_name='Solar Energy')
        self.assertEqual(item.applied_uev, 1.0)
        self.assertEqual(item.calculated_emergy, 1000.0)

    def test_import_invalid_data_skips(self):
        content = "Resource,Quantity,Unit,Process\nInvalid,text_here,J,Nature"
        csv_file = SimpleUploadedFile("error.csv", content.encode('utf-8'), content_type="text/csv")
        
        count = import_data(csv_file, self.project)
        self.assertEqual(count, 0)