from django.contrib import admin
from .models import Blog, Comment, Property, TeamMember, Service, PropertyImage


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted', 'author']
    list_filter = ['posted']
    search_fields = ['title', 'description']
    date_hierarchy = 'posted'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'date', 'short_text']
    list_filter = ['date', 'post']
    search_fields = ['author__username', 'post__title', 'text']
    date_hierarchy = 'date'
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Text'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'deal_type', 'property_type', 'price', 'rooms', 'is_featured')
    list_filter = ('deal_type', 'property_type', 'is_featured')
    search_fields = ('title', 'address')
    
    # Обязательно включаем поле deal_type в форму
    fields = (
        'title',
        'deal_type',         
        'property_type',
        'address',
        'price',
        'utilities_price',
        'area',
        'rooms',
        'floor',
        'description',
        'is_featured',
        'agent',
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image_preview', 'is_main', 'order']
    list_filter = ['is_main', 'property__property_type']
    search_fields = ['property__title', 'property__address']
    list_editable = ['is_main', 'order']
    ordering = ['property', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="75" style="object-fit: cover;" />'
        return "Нет изображения"
    image_preview.allow_tags = True
    image_preview.short_description = "Превью"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'experience', 'deals_completed', 'is_active', 'has_certificate', 'order']
    list_filter = ['is_active', 'position']
    search_fields = ['name', 'position', 'email']
    list_editable = ['is_active', 'order']
    list_display_links = ['name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'position', 'photo', 'is_active')
        }),
        ('Статистика', {
            'fields': ('experience', 'deals_completed')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Порядок отображения', {
            'fields': ('order',)
        }),
        ('Аттестат', {
            'fields': ('certificate_link',),
            'description': 'Добавьте ссылку на PDF или страницу с аттестатом сотрудника'
        }),
    )
    
    # Метод для отображения наличия аттестата в списке
    def has_certificate(self, obj):
        return obj.has_certificate()
    has_certificate.short_description = "Аттестат"
    has_certificate.boolean = True


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'order', 'icon']
    list_filter = ['order']
    search_fields = ['title', 'description']
    list_editable = ['order', 'price']
    ordering = ['order']