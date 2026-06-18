import os
import uuid  # 🟢 WAJIB TAMBAH: Untuk janji nama fail rawak UUID
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseForbidden  # 🟢 WAJIB TAMBAH: HttpResponseForbidden untuk sekat IDOR
from .models import InventoryItem, CustomUser
from django.db import connection

# ==========================================
# 1. USER AUTHENTICATION (Register & Login)
# ==========================================

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')
        role = request.POST.get('role', 'normal') 
        user = CustomUser.objects.create_user(username=username, password=passw, role=role)
        login(request, user)
        return redirect('inventory_list')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # 🟢 SELAMAT (PATCH 1): Menggunakan Django ORM authenticate() asli (Anti-SQLi)
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('inventory_list')
        else:
            return render(request, 'login.html', {'error': 'Username atau Password salah!'})
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# 2. USER PROFILE (IDOR Mitigation)
# ==========================================

def profile_view(request):
    user_id = request.GET.get('id')
    
    if user_id:
        # 🟢 SELAMAT (PATCH 2): Semakan Autorisasi Ownership & Admin (Anti-IDOR)
        if request.user.id != int(user_id) and request.user.role != 'admin':
            return HttpResponseForbidden("Akses Disekat: Anda tidak mempunyai hak untuk melihat profil ini!")
            
        target_user = CustomUser.objects.get(id=user_id)
    else:
        target_user = request.user
        
    return render(request, 'profile.html', {'target_user': target_user})


# ==========================================
# 3. INVENTORY MATRIX (CRUD, SQLi & File Upload Mitigation)
# ==========================================

def inventory_list(request):
    # A. HANDLE RECORD CREATION (POST)
    if request.method == 'POST':
        name = request.POST.get('item_name')
        qty = request.POST.get('quantity')
        status = request.POST.get('status')
        file = request.FILES.get('attachment')

        # 🟢 SELAMAT (PATCH 4): Tapis Extension & Rename guna UUID (Anti-RCE)
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.png', '.jpg', '.jpeg', '.pdf']
            if ext not in valid_extensions:
                return HttpResponseForbidden("Format fail tidak dibenarkan!")
            
            # Tukar nama fail jadi random UUID mengikut kehendak soalan
            random_filename = f"{uuid.uuid4()}{ext}"
            file.name = random_filename

        item = InventoryItem.objects.create(
            user=request.user,
            item_name=name,
            quantity=qty,
            status=status,
            uploaded_file=file
        )
        return redirect('inventory_list')

    # B. HANDLE PAGE DISPLAY & SEARCH FILTER (GET)
    search_query = request.GET.get('search', '')

    if search_query:
        # 🟢 SELAMAT (PATCH 3): Ganti .raw() kepada Django ORM .filter() (Anti-SQLi)
        if request.user.role == 'admin':
            items = InventoryItem.objects.filter(item_name__icontains=search_query)
        else:
            items = InventoryItem.objects.filter(item_name__icontains=search_query, user=request.user)
    else:
        if request.user.role == 'admin':
            items = InventoryItem.objects.all()
        else:
            items = InventoryItem.objects.filter(user=request.user)
        
    return render(request, 'inventory.html', {'items': items, 'search_query': search_query})

def inventory_delete(request, item_id):
    # Tambahan: Hanya pemilik atau admin boleh delete item
    item = InventoryItem.objects.get(id=item_id)
    if item.user == request.user or request.user.role == 'admin':
        item.delete()
    return redirect('inventory_list')


# ==========================================
# 4. ADMIN DASHBOARD (Broken Access Control Mitigation)
# ==========================================

def admin_dashboard(request):
    # 🟢 SELAMAT (PATCH 5): Pagar Autorisasi Peranan RBAC (Anti-Broken Access Control)
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.user.role != 'admin':
        return HttpResponseForbidden("Akses Dinafikan: Halaman ini memerlukan hak keistimewaan Admin.")
        
    return render(request, 'admin_dashboard.html')