from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum

from core.models import (
    EmergyReference,
    Project,
    UserProfile,
    Process,
    InventoryItem,
    CalculationResult,
    ImportLog,
    Institution
)

from .forms import EmergyReferenceForm


# ======================
# DASHBOARD (MENU ADMIN)
# ======================
@staff_member_required
def dashboard(request):
    return render(request, 'panel_admin/dashboard.html')


# ======================
# USERS
# ======================
@staff_member_required
def users(request):
    users = User.objects.all()
    return render(request, 'panel_admin/users.html', {'users': users})


@staff_member_required
def user_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        # 🔐 opcional: alterar senha
        password = request.POST.get('password')
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, "Usuário atualizado com sucesso!")

        return redirect('users')

    return render(request, 'panel_admin/user_form.html', {'user': user})


# ======================
# EMERGY REFERENCES
# ======================
@staff_member_required
def emergy_list(request):
    data = EmergyReference.objects.all()
    return render(request, 'panel_admin/emergy_list.html', {'data': data})


@staff_member_required
def emergy_create(request):
    if request.method == 'POST':
        form = EmergyReferenceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Referência criada com sucesso!")
            return redirect('emergy_list')

        else:
            messages.error(request, "Erro ao criar referência!")

    else:
        form = EmergyReferenceForm()

    return render(request, 'panel_admin/emergy_form.html', {'form': form})


@staff_member_required
def emergy_edit(request, id):
    item = get_object_or_404(EmergyReference, id=id)

    if request.method == 'POST':
        form = EmergyReferenceForm(request.POST, instance=item)

        if form.is_valid():
            form.save()
            messages.success(request, "Referência atualizada!")
            return redirect('emergy_list')

    else:
        form = EmergyReferenceForm(instance=item)

    return render(request, 'panel_admin/emergy_form.html', {'form': form})


@staff_member_required
def emergy_delete(request, id):
    item = get_object_or_404(EmergyReference, id=id)
    item.delete()

    messages.success(request, "Referência excluída!")
    return redirect('emergy_list')


# ======================
# PROJECTS
# ======================
@staff_member_required
def project(request):
    projects = Project.objects.all().select_related('user')

    # calcular emergia pra cada projeto
    for p in projects:
        total = InventoryItem.objects.filter(
            process__project=p
        ).aggregate(total=Sum('calculated_emergy'))['total']

        p.total_emergy = total or 0

    return render(request, 'panel_admin/project.html', {
        'projects': projects
    })

@staff_member_required
def project_results_admin(request, id):
    project = get_object_or_404(Project, id=id)

    items = InventoryItem.objects.filter(process__project=project)
    total = sum(i.calculated_emergy for i in items)

    return render(request, 'panel_admin/project_results.html', {
        'project': project,
        'items': items,
        'total_emergy': total
    })

@staff_member_required
def project_edit(request, id):
    project = get_object_or_404(Project, id=id)

    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')

        user_id = request.POST.get('user')
        project.user_id = user_id

        project.save()
        messages.success(request, "Projeto atualizado!")

        return redirect('project')

    users = User.objects.all()

    return render(request, 'panel_admin/project_form.html', {
        'project': project,
        'users': users
    })


# ======================
# EXTRA (se quiser expandir depois)
# ======================
@staff_member_required
def full_data_overview(request):
    context = {
        'profiles': UserProfile.objects.all(),
        'processes': Process.objects.all(),
        'items': InventoryItem.objects.all(),
        'results': CalculationResult.objects.all(),
        'logs': ImportLog.objects.all(),
        'institutions': Institution.objects.all(),
    }

    return render(request, 'panel_admin/full_data.html', context)