from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Project, Process, InventoryItem

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.project = Project.objects.create(user=self.user, name='Projeto Teste')

    def test_project_creation(self):
        self.assertEqual(self.project.name, 'Projeto Teste')
        self.assertEqual(self.project.user.username, 'testuser')

    def test_process_relation(self):
        process = Process.objects.create(project=self.project, name='Processo 1')
        self.assertEqual(process.project, self.project)

    def test_inventory_item_calculation(self):
        process = Process.objects.create(project=self.project, name='P1')
        item = InventoryItem.objects.create(
            process=process,
            resource_name='Solar',
            quantity=100,
            applied_uev=2.5,
            calculated_emergy=250.0
        )
        self.assertEqual(item.calculated_emergy, 250.0)