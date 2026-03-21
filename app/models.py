from datetime import datetime

from django.db import models
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(verbose_name="Полное содержание")
    posted = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    author = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name="Автор"
    )
    image = models.ImageField(
        upload_to='blog_images/', 
        null=True, 
        blank=True, 
        verbose_name="Изображение"
    )

    def get_absolute_url(self):
        return reverse('blogpost', args=[str(self.id)])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ['-posted']


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата комментария")
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Автор"
    )
    post = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name="comments",
        verbose_name="Статья"
    )

    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.post.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-date']


class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    photo = models.ImageField(
        upload_to='team/', 
        verbose_name="Фото",
        blank=True
    )
    experience = models.IntegerField(verbose_name="Опыт работы (лет)")
    deals_completed = models.IntegerField(verbose_name="Завершенные сделки")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Активный сотрудник"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    
    # Добавляем поле для ссылки на аттестат
    certificate_link = models.URLField(
        max_length=500,
        verbose_name="Ссылка на аттестат",
        blank=True,
        null=True,
        help_text="Вставьте ссылку на PDF файл или страницу с аттестатом"
    )
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    
    # Добавим метод для проверки наличия аттестата
    def has_certificate(self):
        return bool(self.certificate_link)
    has_certificate.short_description = "Есть аттестат"
    has_certificate.boolean = True

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['order', 'name']  # Сортировка по порядку, затем по имени

class Property(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('commercial', 'Коммерческая'),
        ('land', 'Земельный участок'),
        ('room', 'Комната'),
    ]

    DEAL_TYPES = [
        ('sale', 'Продажа'),
        ('rent', 'Аренда'),
    ]
    
    # Существующие поля
    title = models.CharField(max_length=200, verbose_name="Название объекта")
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES, 
        verbose_name="Тип недвижимости"
    )
    address = models.CharField(max_length=300, verbose_name="Адрес")
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Цена"
    )
    area = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Площадь (м²)"
    )
    rooms = models.IntegerField(verbose_name="Количество комнат")
    floor = models.CharField(
        max_length=20, 
        verbose_name="Этаж", 
        blank=True
    )
    description = models.TextField(verbose_name="Описание")
    is_featured = models.BooleanField(
        default=False, 
        verbose_name="Премиум объект"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    agent = models.ForeignKey(
        'TeamMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Агент",
        related_name='properties'
    )
    
    # Новое поле
    deal_type = models.CharField(
        max_length=10,
        choices=DEAL_TYPES,
        verbose_name="Тип сделки",
        default='sale'
    )
    
    def __str__(self):
        return self.title
    
    def get_main_image_url(self):
        """Возвращает URL главного изображения или первого, если главного нет"""
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image.url
        first = self.images.first()
        if first:
            return first.image.url
        return None

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"
        ordering = ['-created_at']
    
    # Существующие поля
    title = models.CharField(max_length=200, verbose_name="Название объекта")
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES, 
        verbose_name="Тип недвижимости"
    )
    address = models.CharField(max_length=300, verbose_name="Адрес")
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Цена"
    )
    area = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Площадь (м²)"
    )
    rooms = models.IntegerField(verbose_name="Количество комнат")
    floor = models.CharField(
        max_length=20, 
        verbose_name="Этаж", 
        blank=True
    )
    description = models.TextField(verbose_name="Описание")
    is_featured = models.BooleanField(
        default=False, 
        verbose_name="Премиум объект"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    agent = models.ForeignKey(
        TeamMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Агент",
        related_name='properties'
    )
    
    # НОВОЕ ПОЛЕ - тип сделки
    deal_type = models.CharField(
        max_length=10,
        choices=DEAL_TYPES,
        verbose_name="Тип сделки",
        default='sale',  # По умолчанию "Продажа"
        blank=False      # Не разрешать пустое значение
    )
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"
        ordering = ['-created_at']


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Объект недвижимости"
    )
    image = models.ImageField(
        upload_to='properties/%Y/%m/', 
        verbose_name="Изображение"
    )
    is_main = models.BooleanField(
        default=False, 
        verbose_name="Главное изображение"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="Порядок отображения"
    )
    
    def __str__(self):
        return f"Изображение для {self.property.title}"

    class Meta:
        verbose_name = "Изображение объекта"
        verbose_name_plural = "Изображения объектов"
        ordering = ['order', 'id']


class Service(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание")
    price = models.CharField(
        max_length=100, 
        verbose_name="Стоимость", 
        blank=True
    )
    icon = models.CharField(
        max_length=50, 
        verbose_name="Иконка",
        help_text="Например: 🏠, 💰, ⚖️"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="Порядок отображения"
    )
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['order']


class ConsultationRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    message = models.TextField(verbose_name="Сообщение", blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата заявки"
    )
    is_processed = models.BooleanField(
        default=False, 
        verbose_name="Обработано"
    )
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"
        ordering = ['-created_at']


class Review(models.Model):
    SOURCE_CHOICES = [
        ('yandex', 'Яндекс.Карты'),
        ('site', 'Сайт'),
        ('google', 'Google'),
    ]
    
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    author_name = models.CharField(max_length=200, verbose_name='Имя автора')
    rating = models.IntegerField(
        verbose_name='Оценка', 
        choices=RATING_CHOICES
    )
    text = models.TextField(verbose_name='Текст отзыва')
    date = models.DateTimeField(
        verbose_name='Дата отзыва', 
        default=timezone.now
    )
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES, 
        default='yandex'
    )
    source_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='ID отзыва в источнике'
    )
    reply_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Ответ компании'
    )
    reply_date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name='Дата ответа'
    )
    is_verified = models.BooleanField(
        default=False, 
        verbose_name='Проверенный отзыв'
    )
    is_featured = models.BooleanField(
        default=False, 
        verbose_name='Показать на главной'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Активный'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.author_name} - {self.rating}/5"
    
    def get_stars_html(self):
        """Генерирует HTML для звезд рейтинга"""
        stars = ['<i class="fas fa-star text-warning"></i>' if i <= self.rating 
                else '<i class="far fa-star text-warning"></i>' 
                for i in range(1, 6)]
        return ''.join(stars)
    
    def get_short_text(self, length=150):
        """Сокращенный текст отзыва"""
        if len(self.text) <= length:
            return self.text
        return self.text[:length] + '...'
    
    @property
    def time_ago(self):
        """Время, прошедшее с момента отзыва"""
        now = timezone.now()
        diff = now - self.date
        
        if diff.days > 365:
            years = diff.days // 365
            return f'{years} год назад' if years == 1 else f'{years} года назад'
        elif diff.days > 30:
            months = diff.days // 30
            return f'{months} месяц назад' if months == 1 else f'{months} месяца назад'
        elif diff.days > 0:
            return f'{diff.days} дней назад'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'{hours} часов назад'
        else:
            return 'Только что'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['source', 'is_active']),
            models.Index(fields=['rating', 'is_featured']),
        ]