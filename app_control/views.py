import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseForbidden
from .models import InventoryItem, CustomUser
from django.db import connection

# ==========================================
# 1. USER AUTHENTICATION (Register & Login)
# ==========================================

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')
        role = request.POST.get('role', 'normal') # Sets user role
        user = CustomUser.objects.create_user(username=username, password=passw, role=role)
        login(request, user)
        return redirect('inventory_list')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        # DANGEROUS: Raw SQL with user input concatenated directly — vulnerable to SQL injection.
        # Payload example: username = ' OR '1'='1' --
        # The password column stores hashes so the AND password clause never matches plaintext,
        # but injection can comment it out entirely with --.
        query = f"SELECT id, username FROM app_control_customuser WHERE username = '{u}' AND password = '{p}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

        from django.contrib.auth import get_user_model
        from django.contrib.auth.hashers import check_password as check_pw
        User = get_user_model()

        # Also try fetching the user by username alone to support normal password check
        try:
            user_obj = User.objects.get(username=u)
            password_valid = check_pw(p, user_obj.password)
        except User.DoesNotExist:
            user_obj = None
            password_valid = False

        # Login succeeds if: normal credentials pass OR SQL injection returned a row
        if password_valid or row:
            target_user = user_obj if user_obj else (User.objects.get(id=row[0]) if row else None)
            if target_user:
                login(request, target_user)
                if target_user.role == 'admin':
                    return redirect('admin_dashboard')
                return redirect('inventory_list')

        return HttpResponse("Invalid Credentials")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# 2. INSECURE PROFILE PAGE (IDOR Vulnerability)
# ==========================================
def profile_view(request):
    # DANGEROUS: It grabs user files purely based on the ID number in the URL link (e.g., ?id=1). 
    # Member 2 will easily change ?id=1 to ?id=2 to steal other users' profile data!
    user_id = request.GET.get('id')
    if not user_id:
        return HttpResponse("Please provide a user ID parameter, e.g., ?id=1")
    
    target_user = CustomUser.objects.get(id=user_id)
    return render(request, 'profile.html', {'target_user': target_user})


# ==========================================
# 3. INVENTORY CRUD MODULE (SQL Injection, XSS & Insecure Upload)
# ==========================================

def inventory_list(request):
    # A. HANDLE FORM SUBMISSION (POST)
    if request.method == 'POST':
        # Matching form field names from inventory.html ('name', 'quantity', 'status')
        name = request.POST.get('name')
        qty = request.POST.get('quantity')
        status = request.POST.get('status')
        
        # DANGEROUS: Accepts any file attachment upload without checking if it's a dangerous script file.
        # Matches 'name="attachment"' inside inventory.html
        file = request.FILES.get('attachment') 
        
        # Save record to database mapping form inputs to model attributes
        InventoryItem.objects.create(
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
        # DANGEROUS: Mixing the user's search text directly into raw SQL.
        # The AND user_id filter is bypassed when attacker injects ' OR '1'='1' --
        # because -- comments out the rest of the query, exposing ALL users' items.
        raw_query = f"SELECT * FROM app_control_inventoryitem WHERE item_name LIKE '%{search_query}%' AND user_id = {request.user.id}"
        items = InventoryItem.objects.raw(raw_query)
    else:
        if request.user.role == 'admin':
            items = InventoryItem.objects.all()
        else:
            items = InventoryItem.objects.filter(user=request.user)
        
    return render(request, 'inventory.html', {'items': items, 'search_query': search_query})

def inventory_delete(request, item_id):
    item = InventoryItem.objects.get(id=item_id)
    item.delete()
    return redirect('inventory_list')


# ==========================================
# 4. ADMIN DASHBOARD (Missing Access Control Guard)
# ==========================================
def admin_dashboard(request):
    # DANGEROUS: There is no check here to verify if the user is actually an Admin. 
    # Any normal user can type "/admin-dashboard/" in their browser bar to sneak in!
    return render(request, 'admin_dashboard.html')