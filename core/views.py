from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from io import BytesIO
import pandas as pd
import csv
from django.contrib.auth import logout, authenticate, login
from .decorators import user_only
from .forms import UserRegisterForm, ProjectForm
from .models import Project, InventoryItem, UserProfile
from .services import import_data
from django.contrib.auth.models import User
from pathlib import Path

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

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)

            if user.is_staff:
                return redirect('/admin-panel/')
            else:
                return redirect('dashboard')

        else:
            messages.error(request, "Usuário ou senha inválidos")

    return render(request, 'core/login.html')

# --- DASHBOARD ---
@login_required
@user_only
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    projects = Project.objects.filter(user=request.user)

    return render(request, 'core/dashboard.html', {'projects': projects})

@login_required
@user_only
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
@user_only
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
@user_only
def download_template(request):
    fmt = request.GET.get('format', 'excel')

    cols = ['Resource', 'Quantity', 'Unit', 'Process']
    data = [['Energia Solar', 1500000, 'J', 'Natureza']]
    df = pd.DataFrame(data, columns=cols)

    # pasta Downloads do usuário
    downloads = Path.home() / "Downloads"

    if fmt == 'csv':
        file_path = downloads / 'template_scale.csv'
        df.to_csv(file_path, index=False)

    else:
        file_path = downloads / 'template_scale.xlsx'

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

    return JsonResponse({
        'success': True,
        'path': str(file_path)
    })

@login_required
@user_only
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

def logout_view(request):
    logout(request)
    return redirect('login')

def setup_admin(request):

    # se já existe admin, bloqueia acesso
    if User.objects.filter(is_superuser=True).exists():
        return redirect('/login/')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "As senhas não coincidem.")
            return redirect('setup_admin')

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Administrador criado com sucesso!")
        return redirect('/login/')

    return render(request, 'core/setup_admin.html')

def check_admin(request):

    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse(
            "http://127.0.0.1:8000/login/"
        )

    return HttpResponse(
        "http://127.0.0.1:8000/setup/"
    )