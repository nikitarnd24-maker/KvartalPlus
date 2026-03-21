from datetime import datetime
import json
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Max
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    BlogForm, FeedbackForm, CommentForm, 
    PropertyForm, PropertyFilterForm
)
from .models import (
    Comment, ConsultationRequest, Property, 
    TeamMember, Service, Blog, PropertyImage
)


def home(request):
    """Renders the home page."""
    try:
        all_properties = Property.objects.all()[:6]
    except:
        all_properties = []
    
    try:
        team_members = TeamMember.objects.filter(is_active=True)[:4]
    except:
        team_members = []
    
    try:
        services = Service.objects.all()[:6]
    except:
        services = []
    
    context = {
        'title': 'Главная - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
        'properties': Property.objects.all()[:6],
        'team_members': TeamMember.objects.filter(is_active=True)[:4],
        'services': Service.objects.all()[:6],
    }
    return render(request, 'app/index.html', context)


def send_telegram_message(name, phone, message):
    """Отправка заявки в Telegram через urllib."""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        
        text = f"""
🏠 *НОВАЯ ЗАЯВКА С САЙТА*

👤 Имя: {name}
📞 Телефон: `{phone}`
💬 Сообщение: {message or 'Не указано'}
⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}

⚠️ СРОЧНО ПЕРЕЗВОНИТЕ!
"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode() == 200
            
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False


def contact(request):
    """Renders the contact page."""
    success = False
    telegram_sent = False
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone') 
        message = request.POST.get('message', '')
        
        if name and phone:
            ConsultationRequest.objects.create(
                name=name,
                phone=phone, 
                message=message
            )
            
            telegram_sent = send_telegram_message(name, phone, message)
            success = True
    
    context = {
        'title': 'Контакты - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
    }
    return render(request, 'app/contact.html', context)


def links(request):
    """Renders the links page."""
    context = {
        'title': 'Полезные ссылки - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
    }
    return render(request, 'app/links.html', context)


def about(request):
    """Renders the about page."""
    context = {
        'title': 'О нас - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
    }
    return render(request, 'app/about.html', context)


def anketa(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data  
            return render(request, "app/anketa.html", {"form": None, "data": data})
    else:
        form = FeedbackForm()

    return render(request, "app/anketa.html", {"form": form})


def registration(request):
    """Renders the registration page."""
    if request.method == "POST":
        regform = UserCreationForm(request.POST)

        if regform.is_valid():
            user = regform.save(commit=False)
            user.is_staff = False
            user.is_active = True
            user.is_superuser = False
            user.date_joined = datetime.now()
            user.last_login = datetime.now()
            user.save()
            
            username = regform.cleaned_data.get('username')
            password = regform.cleaned_data.get('password1')
            
            authenticated_user = authenticate(
                username=username, 
                password=password
            )
            
            if authenticated_user is not None:
                login(request, authenticated_user)
            
            return redirect('home')
    else:
        regform = UserCreationForm()

    context = {
        'regform': regform,
        'year': datetime.now().year,
    }
    return render(request, 'app/registration.html', context)


def blog(request):
    """Renders the blog page."""
    posts = Blog.objects.all()
    context = {
        'title': 'Блог - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
        'posts': Blog.objects.all(),
    }
    return render(request, 'app/blog.html', context)


def blogpost(request, parametr):
    """Renders the blogpost page."""
    post_1 = Blog.objects.get(id=parametr)
    comments = Comment.objects.filter(post=parametr)
    
    if request.method == "POST" and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user
            comment_f.date = datetime.now()
            comment_f.post = Blog.objects.get(id=parametr)
            comment_f.save()
            return redirect('blogpost', parametr=post_1.id)
    else:
        form = CommentForm()

    context = {
        'post_1': post_1,
        'year': datetime.now().year,
        'comments': comments,
        'form': form,
    }
    return render(request, 'app/blogpost.html', context)


def newpost(request):
    if not request.user.is_superuser:
        return redirect('blog')

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog')
    else:
        form = BlogForm()

    context = {
        'form': form,
        'year': datetime.now().year
    }
    return render(request, 'app/newpost.html', context)


def video(request):
    return render(request, 'app/videopage.html', {'year': datetime.now().year})


def catalog(request):
    form = PropertyFilterForm(request.GET or None)
    properties = Property.objects.all().order_by('-created_at')

    if form.is_valid():
        data = form.cleaned_data

        if data.get('deal_type'):
            properties = properties.filter(deal_type=data['deal_type'])

        if data.get('property_type'):
            properties = properties.filter(property_type=data['property_type'])

        if data.get('rooms'):
            properties = properties.filter(rooms=data['rooms'])

        if data.get('price_min'):
            properties = properties.filter(price__gte=data['price_min'])

        if data.get('price_max'):
            properties = properties.filter(price__lte=data['price_max'])

        if data.get('area_min'):
            properties = properties.filter(area__gte=data['area_min'])

        if data.get('area_max'):
            properties = properties.filter(area__lte=data['area_max'])

        if data.get('has_images'):
            properties = properties.filter(images__isnull=False).distinct()

        if data.get('sort_by'):
            properties = properties.order_by(data['sort_by'])

    context = {
        'properties': properties,
        'property_count': properties.count(),
        'form': form,
        'active_filters': request.GET,
        'title': 'Каталог - Агентство недвижимости Квартал+',  
    }
    
    return render(request, 'app/catalog.html', context)





def filter_by_rooms(queryset, rooms):
    """Фильтрация по количеству комнат."""
    if rooms.endswith('+'):
        try:
            rooms_int = int(rooms.rstrip('+'))
            return queryset.filter(rooms__gte=rooms_int)
        except ValueError:
            return queryset
    else:
        try:
            rooms_int = int(rooms)
            return queryset.filter(rooms=rooms_int)
        except ValueError:
            return queryset

def apply_filters(queryset, filters):
    """Применяем фильтры к queryset объектов."""
    property_type = filters.get('property_type')
    rooms = filters.get('rooms')
    price_min = filters.get('price_min')
    price_max = filters.get('price_max')
    area_min = filters.get('area_min')
    area_max = filters.get('area_max')
    is_featured = filters.get('is_featured')
    has_images = filters.get('has_images')
    deal_type = filters.get('deal_type')
    
    sort_by = filters.get('sort_by') or '-created_at'

    # Фильтруем
    if property_type:
        queryset = queryset.filter(property_type=property_type)

    if rooms:
        queryset = queryset.filter(rooms=rooms)

    if price_min:
        queryset = queryset.filter(price__gte=price_min)
    if price_max:
        queryset = queryset.filter(price__lte=price_max)

    if area_min:
        queryset = queryset.filter(area__gte=area_min)
    if area_max:
        queryset = queryset.filter(area__lte=area_max)

    if is_featured:
        queryset = queryset.filter(is_featured=True)

    if has_images:
        queryset = queryset.filter(images__isnull=False).distinct()

    if deal_type in ['sale', 'rent']:  
        queryset = queryset.filter(deal_type=deal_type)

    try:
        return queryset.order_by(sort_by)
    except Exception:
        return queryset.order_by('-created_at')



def team(request):
    """Renders the team page."""
    team_members = TeamMember.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'title': 'Наша команда - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
        'team_members': TeamMember.objects.filter(is_active=True),
    }
    return render(request, 'app/team.html', context)


def services(request):
    """Renders the services page."""
    services_list = Service.objects.all()
    
    context = {
        'title': 'Наши услуги - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
        'services': Service.objects.all(),
    }
    return render(request, 'app/services.html', context)


@login_required
def add_property(request):
    """Добавление нового объекта недвижимости с фотографиями."""
    agents = TeamMember.objects.filter(is_active=True)

    if request.method == 'POST':
        property_data = extract_property_data(request)

        if not validate_required_fields(property_data):
            return render_property_form(request, agents, 'Пожалуйста, заполните все обязательные поля')

        try:
            property_obj = create_property_object(property_data)

            # Загружаем фотографии
            images = request.FILES.getlist('images')
            if not images:
                return render_property_form(request, agents, 'Пожалуйста, загрузите хотя бы одну фотографию')
            create_property_images(property_obj, images)

            return redirect('catalog')

        except Exception as e:
            return render_property_form(request, agents, f'Ошибка при сохранении: {str(e)}')

    return render_property_form(request, agents)


def extract_property_data(request):
    """Извлекаем данные из формы."""
    return {
        'title': request.POST.get('title'),
        'property_type': request.POST.get('property_type'),
        'deal_type': request.POST.get('deal_type'), 
        'address': request.POST.get('address'),
        'price': request.POST.get('price'),
        'area': request.POST.get('area'),
        'rooms': request.POST.get('rooms'),
        'floor': request.POST.get('floor', ''),
        'description': request.POST.get('description'),
        'is_featured': 'is_featured' in request.POST,
        'agent_id': request.POST.get('agent'),
    }


def create_property_object(data):
    """Создаём объект Property."""
    agent = TeamMember.objects.filter(id=data.get('agent_id')).first() if data.get('agent_id') else None
    return Property.objects.create(
        title=data['title'],
        property_type=data['property_type'],
        deal_type=data['deal_type'], 
        address=data['address'],
        price=data['price'],
        area=data['area'],
        rooms=data['rooms'],
        floor=data['floor'],
        description=data['description'],
        is_featured=data['is_featured'],
        agent=agent
    )


def validate_required_fields(data):
    """Validate that all required fields are present."""
    required_fields = ['title', 'property_type', 'address', 'price', 'area', 'description']
    
    # Для земельных участков комнаты не обязательны
    if data['property_type'] != 'land':
        required_fields.append('rooms')
    
    return all(data[field] for field in required_fields)


def create_property_object(data):
    """Create Property object from data."""
    agent = None
    if data['agent_id']:
        try:
            agent = TeamMember.objects.get(id=data['agent_id'])
        except TeamMember.DoesNotExist:
            pass

    return Property.objects.create(
        title=data['title'],
        property_type=data['property_type'],
        deal_type=data.get('deal_type', 'sale'),  
        address=data['address'],
        price=data['price'],
        area=data['area'],
        rooms=data['rooms'],
        floor=data['floor'],
        description=data['description'],
        is_featured=data['is_featured'],
        agent=agent
    )



def create_property_images(property_obj, images):
    """Create PropertyImage objects for a property."""
    for i, image_file in enumerate(images):
        PropertyImage.objects.create(
            property=property_obj,
            image=image_file,
            is_main=(i == 0),
            order=i
        )


def render_property_form(request, agents, error=None):
    """Render property form with context."""
    context = {
        'title': 'Добавить объект',
        'year': datetime.now().year,
        'agents': agents,
    }
    if error:
        context['error'] = error
    
    return render(request, 'app/add_property.html', context)


def property_detail(request, property_id):
    """Детальная страница объекта недвижимости."""
    try:
        property_obj = get_object_or_404(Property, id=property_id)
        images = property_obj.images.all().order_by('-is_main', 'order')
        
        main_image = images.filter(is_main=True).first() or images.first()
        
        similar_properties = Property.objects.filter(
            property_type=property_obj.property_type
        ).exclude(id=property_obj.id)[:3]
        
    except Property.DoesNotExist:
        return redirect('catalog')
    
    context = {
        'property': property_obj,
        'images': images,
        'similar_properties': similar_properties,
        'title': f'{property_obj.title} - Агентство недвижимости Квартал+',
        'year': datetime.now().year,
    }
    return render(request, 'app/property_detail.html', context)


@login_required
def edit_property(request, property_id):
    """Редактирование объекта недвижимости."""
    property_obj = get_object_or_404(Property, id=property_id)
    
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав для редактирования объектов")
        return redirect('property_detail', property_id=property_id)
    
    agents = TeamMember.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # основные данные объекта
            property_obj.title = request.POST.get('title')
            property_obj.property_type = request.POST.get('property_type')
            property_obj.address = request.POST.get('address')
            property_obj.price = request.POST.get('price')
            property_obj.area = request.POST.get('area')
            property_obj.rooms = request.POST.get('rooms')
            property_obj.floor = request.POST.get('floor', '')
            property_obj.description = request.POST.get('description')
            property_obj.is_featured = 'is_featured' in request.POST
            
            # ОБРАБОТКА ТИПА СДЕЛКИ 
            deal_type = request.POST.get('deal_type')
            if deal_type in ['sale', 'rent']:
                property_obj.deal_type = deal_type
            
            # Обработка коммунальных услуг для аренды
            utilities_price = request.POST.get('utilities_price')
            if utilities_price:
                property_obj.utilities_price = utilities_price
            elif deal_type == 'rent':
                # Если аренда, но поле пустое - ставим 0 или None
                property_obj.utilities_price = 0
            
            # Обработка агента
            agent_id = request.POST.get('agent')
            if agent_id and agent_id.isdigit():
                try:
                    property_obj.agent = TeamMember.objects.get(id=int(agent_id))
                except TeamMember.DoesNotExist:
                    property_obj.agent = None
            else:
                property_obj.agent = None
            
            property_obj.save()
            
            messages.success(request, "Объект успешно обновлен")
            return redirect('property_detail', property_id=property_id)
            
        except Exception as e:
            messages.error(request, f"Ошибка при обновлении: {str(e)}")
    
    # GET запрос
    images = property_obj.images.all().order_by('order')
    
    context = {
        'property': property_obj,
        'images': images,
        'agents': agents,
        'title': f'Редактирование: {property_obj.title}',
        'year': datetime.now().year,
    }
    return render(request, 'app/edit_property.html', context)


def update_property_from_request(property_obj, request):
    """Update property object from request data."""
    property_obj.title = request.POST.get('title')
    property_obj.property_type = request.POST.get('property_type')
    property_obj.address = request.POST.get('address')
    property_obj.price = request.POST.get('price')
    property_obj.area = request.POST.get('area')
    property_obj.rooms = request.POST.get('rooms')
    property_obj.floor = request.POST.get('floor', '')
    property_obj.description = request.POST.get('description')
    property_obj.is_featured = 'is_featured' in request.POST
    
    agent_id = request.POST.get('agent')
    if agent_id:
        try:
            property_obj.agent = TeamMember.objects.get(id=agent_id)
        except TeamMember.DoesNotExist:
            property_obj.agent = None
    else:
        property_obj.agent = None


def process_new_images(property_obj, request):
    """Process new images uploaded in edit form."""
    new_images = request.FILES.getlist('new_images')
    if new_images:
        max_order = property_obj.images.aggregate(Max('order'))['order__max'] or -1
        
        for i, image_file in enumerate(new_images, start=max_order + 1):
            PropertyImage.objects.create(
                property=property_obj,
                image=image_file,
                is_main=False,
                order=i
            )


def update_image_order(property_obj, request):
    """Update order of property images."""
    image_order = request.POST.get('image_order')
    if image_order:
        order_list = image_order.split(',')
        for i, image_id in enumerate(order_list):
            try:
                image = PropertyImage.objects.get(id=int(image_id), property=property_obj)
                image.order = i
                image.save()
            except PropertyImage.DoesNotExist:
                pass


@login_required
def delete_property_image(request, image_id):
    """Удаление фотографии объекта."""
    image = get_object_or_404(PropertyImage, id=image_id)
    property_id = image.property.id
    
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав для удаления фотографий")
        return redirect('edit_property', property_id=property_id)
    
    image.delete()
    messages.success(request, "Фотография удалена")
    return redirect('edit_property', property_id=property_id)


@login_required
def set_main_image(request, image_id):
    """Установка фотографии как главной."""
    try:
        # изображение
        image = get_object_or_404(PropertyImage, id=image_id)
        property_id = image.property.id
       
        if not request.user.is_superuser:
            messages.error(request, "У вас нет прав для изменения главной фотографии")
            return redirect('edit_property', property_id=property_id)
        
        # Сбрасываем все флаги is_main для этого объекта
        PropertyImage.objects.filter(property=image.property).update(is_main=False)
        
        # Устанавливаем выбранную фотографию как главную
        image.is_main = True
        image.save()
        
        messages.success(request, "Главная фотография обновлена")
        
    except Exception as e:
        messages.error(request, f"Ошибка при установке главной фотографии: {str(e)}")
    
    return redirect('edit_property', property_id=property_id)


@login_required
def delete_property(request, property_id):
    """Удаление объекта недвижимости."""
    property_obj = get_object_or_404(Property, id=property_id)
    
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав для удаления объектов")
        return redirect('property_detail', property_id=property_id)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "Объект успешно удален")
        return redirect('catalog')
    
    context = {
        'property': property_obj,
        'title': f'Удаление: {property_obj.title}',
        'year': datetime.now().year,
    }
    return render(request, 'app/delete_property.html', context)