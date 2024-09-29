from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    gender = models.BooleanField(null=True, blank=True, verbose_name="Пол")
    
    INTEREST_CHOICES = [
        (1, 'Развлечения'),
        (2, 'Хобби'),
        (3, 'Животные'),
        (4, 'Разное'),
        (5, 'Телепередачи'),
        (6, 'Спорт'),
        (7, 'Недвижимость'),
        (8, 'Сериалы'),
        (9, 'Детям'),
        (10, 'Музыка'),
        (11, 'Юмор'),
        (12, 'Лайфстайл'),
        (13, 'Авто-мото'),
        (14, 'Сад и огород'),
        (15, 'Фильмы'),
        (16, 'Мультфильмы'),
        (17, 'Путешествия'),
        (18, 'Технологии и интернет'),
        (19, 'Лайфхаки'),
        (20, 'Видеоигры'),
        (21, 'Культура'),
        (22, 'Обзоры и распаковки товаров'),
        (23, 'Обучение'),
        (24, 'Здоровье'),
        (25, 'Охота и рыбалка'),
        (26, 'Строительство и ремонт'),
        (27, 'Аниме'),
        (28, 'Эзотерика'),
        (29, 'Еда'),
        (30, 'Интервью'),
        (31, 'Бизнес и предпринимательство'),
        (32, 'Техника и оборудование'),
        (33, 'Психология'),
        (34, 'Наука'),
        (35, 'Красота'),
        (36, 'Природа'),
        (37, 'Дизайн'),
        (38, 'Аудиокниги'),
        (39, 'Аудио'),
    ]
    interests = models.JSONField(default=INTEREST_CHOICES, blank=True, verbose_name="Интересы")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    # Дополнительные поля, если нужны
    pass


class Reaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=30)
    reaction_type = models.CharField(max_length=10)  # 'like' или 'dislike'
    created_at = models.DateTimeField(auto_now_add=True)


class SearchQuery(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ShownVideo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    video_id = models.CharField(max_length=30, verbose_name="ID видео")
    shown_at = models.DateTimeField(auto_now_add=True, verbose_name="Время показа")

    class Meta:
        verbose_name = "Показанное видео"
        verbose_name_plural = "Показанные видео"

    def __str__(self):
        return f"{self.user.username} - {self.video_id}"
