from django.contrib import admin
from django.urls import path
from app_control import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # <--- Add this import

urlpatterns = [
    # Automatically redirects http://127.0.0.1:8000/ straight to the login page
    path('', RedirectView.as_view(url='/login/', permanent=False)), 
    
    path('superadmin/', admin.site.urls),

    # 1. Authentication Routes
    path('register/', views.register_view, name='register_view'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 2. Insecure Profile (IDOR target)
    path('profile/', views.profile_view, name='profile_view'),

    # 3. Inventory Matrix Routes (SQLi, XSS & File Upload targets)
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/delete/<int:item_id>/', views.inventory_delete, name='inventory_delete'),

    # 4. Unprotected Admin Panel (Broken Access Control target)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)