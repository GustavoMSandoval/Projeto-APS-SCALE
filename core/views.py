from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
import pandas as pd
import csv

from .forms import UserRegisterForm, ProjectForm
from .models import Project, InventoryItem
from .services import import_data

# --- AUTENTICAÇÃO ---
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Conta criada! Faça login.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

# --- DASHBOARD ---
@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'core/dashboard.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})

# --- UPLOAD ÚNICO ---
@login_required
def upload_inventory(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            total = import_data(request.FILES['excel_file'], project)
            messages.success(request, f"Sucesso: {total} itens importados!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Erro ao processar: {e}")
    return render(request, 'core/upload_inventory.html', {'project': project})

# --- DOWNLOAD ÚNICO (Detecta formato via URL) ---
@login_required
def download_template(request):
    fmt = request.GET.get('format', 'excel')
    cols = ['Resource', 'Quantity', 'Unit', 'Process']
    data = [['Energia Solar', 1500000, 'J', 'Natureza']]
    df = pd.DataFrame(data, columns=cols)

    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=template_scale.csv'
        df.to_csv(path_or_buf=response, index=False)
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=template_scale.xlsx'
    
    return response

@login_required
def project_results(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Busca todos os itens do inventário deste projeto
    inventory_items = InventoryItem.objects.filter(process__project=project)
    
    # Soma a emergia total
    total_emergy = sum(item.calculated_emergy for item in inventory_items)
    
    # Atualiza o campo total_emergy no modelo do projeto
    project.total_emergy = total_emergy
    project.save()
    
    context = {
        'project': project,
        'items': inventory_items,
        'total_emergy': total_emergy,
    }
    return render(request, 'core/project_results.html', context)