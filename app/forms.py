from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Property

from .models import Blog, Comment, Property, PropertyImage


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label='Ваше имя', 
        min_length=2, 
        max_length=100
    )
    city = forms.CharField(
        label='Ваш город', 
        min_length=2, 
        max_length=100
    )
    job = forms.CharField(
        label='Ваш род занятий', 
        min_length=2, 
        max_length=100
    )
    gender = forms.ChoiceField(
        label='Ваш пол',
        choices=[('1', 'Мужской'), ('2', 'Женский')],
        widget=forms.RadioSelect
    )
    internet = forms.ChoiceField(
        label='Вы пользуетесь интернетом',
        choices=[
            ('1', 'Каждый день'),
            ('2', 'Несколько раз в день'),
            ('3', 'Несколько раз в неделю'),
            ('4', 'Несколько раз в месяц')
        ],
        initial=1
    )
    notice = forms.BooleanField(
        label='Получать новости сайта на email?', 
        required=False
    )
    email = forms.EmailField(
        label='Ваш email', 
        min_length=7
    )
    message = forms.CharField(
        label='Коротко о себе',
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 40})
    )


class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'description', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 10
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': "Комментарий"}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
        }


class PropertyForm(forms.ModelForm):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('commercial', 'Коммерческая'),
        ('land', 'Земельный участок'),
    ]
    
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'address', 'price', 
            'area', 'rooms', 'floor', 'description', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Название объекта'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Полный адрес'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Цена в рублях',
                'step': '0.01'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Площадь в м²',
                'step': '0.01'
            }),
            'rooms': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Количество комнат'
            }),
            'floor': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Этаж (необязательно)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Подробное описание'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Для земельного участка делаем комнаты и этаж необязательными
        property_type = self.initial.get('property_type', '')
        if property_type == 'land':
            self.fields['rooms'].required = False
            self.fields['floor'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        property_type = cleaned_data.get('property_type')
        
        # Для земельного участка делаем комнаты и этаж необязательными
        if property_type == 'land':
            self.fields['rooms'].required = False
            self.fields['floor'].required = False
            
            # Удаляем ошибки валидации для этих полей
            if 'rooms' in self.errors:
                del self.errors['rooms']
            if 'floor' in self.errors:
                del self.errors['floor']
            
            # Устанавливаем значения по умолчанию
            if not cleaned_data.get('rooms'):
                cleaned_data['rooms'] = 0
            if not cleaned_data.get('floor'):
                cleaned_data['floor'] = ''
        
        # Проверяем обязательные поля для других типов
        else:
            if not cleaned_data.get('rooms'):
                self.add_error('rooms', 'Это поле обязательно для данного типа недвижимости')
            if not cleaned_data.get('floor'):
                cleaned_data['floor'] = ''
        
        # Проверяем обязательные поля price и area
        if not cleaned_data.get('price'):
            self.add_error('price', 'Это поле обязательно')
        if not cleaned_data.get('area'):
            self.add_error('area', 'Это поле обязательно')
        
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropertyFilterForm(forms.Form):
    DEAL_TYPES = [
    ('', 'Любой тип сделки'),
    ('sale', 'Продажа'),
    ('rent', 'Аренда'),
]

    PROPERTY_TYPES = [('', 'Все типы')] + Property.PROPERTY_TYPES
    
    ROOMS_CHOICES = [
        ('', 'Любое количество'),
        ('1', '1 комната'),
        ('2', '2 комнаты'),
        ('3', '3 комнаты'),
        ('4', '4 комнаты'),
        ('5', '5 комнат'),
        ('6+', '6+ комнат'),
    ]
    
    SORT_CHOICES = [
        ('-created_at', 'Сначала новые'),
        ('created_at', 'Сначала старые'),
        ('price', 'Цена по возрастанию'),
        ('-price', 'Цена по убыванию'),
        ('area', 'Площадь по возрастанию'),
        ('-area', 'Площадь по убыванию'),
    ]
    deal_type = forms.ChoiceField(
        choices=DEAL_TYPES,
        required=False,
        label='Тип сделки',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPES,
        required=False,
        label='Тип недвижимости',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    rooms = forms.ChoiceField(
        choices=ROOMS_CHOICES,
        required=False,
        label='Количество комнат',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_min = forms.IntegerField(
        min_value=0,
        required=False,
        label='Цена от',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. цена',
            'min': '0'
        })
    )
    
    price_max = forms.IntegerField(
        min_value=0,
        required=False,
        label='Цена до',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. цена',
            'min': '0'
        })
    )
    
    area_min = forms.IntegerField(
        min_value=0,
        required=False,
        label='Площадь от',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. м²',
            'min': '0'
        })
    )
    
    area_max = forms.IntegerField(
        min_value=0,
        required=False,
        label='Площадь до',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. м²',
            'min': '0'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label='Сортировать по',
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_featured = forms.BooleanField(
        required=False,
        label='Только премиум',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_images = forms.BooleanField(
        required=False,
        label='Только с фото',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class QuickFilterForm(forms.Form):
    property_type = forms.ChoiceField(
        choices=[
            ('', 'Все объекты'),
            ('apartment', 'Квартиры'),
            ('house', 'Дома'),
            ('commercial', 'Коммерческая'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    price_range = forms.ChoiceField(
        choices=[
            ('', 'Любая цена'),
            ('0-10000000', 'До 10 млн'),
            ('10000000-20000000', '10-20 млн'),
            ('20000000-50000000', '20-50 млн'),
            ('50000000+', 'От 50 млн'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )