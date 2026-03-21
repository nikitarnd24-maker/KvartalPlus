"""
Definition of urls for DjangoWebProject1.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import views, forms
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('anketa/', views.anketa, name='anketa'),
    path('registration/', views.registration, name='registration'),
    path('blog/', views.blog, name='blog'),
    path('blogpost/<int:parametr>/', views.blogpost, name='blogpost'),
    path('newpost/', views.newpost, name='newpost'),
    path('video/', views.video, name='video'),
    path('links/', views.links, name='links'),
    
    # Недвижимость
    path('catalog/', views.catalog, name='catalog'),
    path('property/add/', views.add_property, name='add_property'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/edit/', views.edit_property, name='edit_property'),
    path('property/<int:property_id>/delete/', views.delete_property, name='delete_property'),
    path('property/image/<int:image_id>/delete/', views.delete_property_image, name='delete_property_image'),
    path('property/image/<int:image_id>/set-main/', views.set_main_image, name='set_main_image'),
    
    # Команда и услуги
    path('team/', views.team, name='team'),
    path('services/', views.services, name='services'),
    
    # Аутентификация
    path('login/',
         LoginView.as_view(
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Авторизация',
                 'year': datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # Админка
    path('admin/', admin.site.urls),
]

# ТОЛЬКО в режиме DEBUG добавляем медиа файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)