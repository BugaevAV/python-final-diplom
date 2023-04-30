from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django_rest_passwordreset.tokens import get_token_generator


USER_TYPES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель')
)


class UserManager(BaseUserManager):             # создание пользовательского менеджера использующего эл почту в качестве
                                                # идентификтора вместо имени пользователя
    use_in_migrations = True                    # поведение во время миграции .... пока не очень понятно????

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Необходимо указать email!')
        email = self.normalize_email(email)               # приведение email  к "стандартному" виду
        user = self.model(email=email, **extra_fields)    # создание обьекта класса
        user.set_password(password)
        user.save()                             # user.save(using=self._db) опция в скобках используется если несколько
        return user                             # баз данных определено в сеттингах

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Cуперпользователь должен иметь статус is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпозователь должен имеить статус is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):     # создание кастомной модели пользователя

    REQUIRED_FIELDS = []                # как именно работает эта переменная?????
    objects = UserManager()             # обьект юзерменеджера с данными для создания пользователя или супер (видимо..)
    USERNAME_FIELD = 'email'            # идентификация по адресу эл почты
    email = models.EmailField('email address', unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField('username', max_length=150,
                                help_text='Обязательное поле. Допустимы буквы, цифры и символы @/./+/-/_',
                                validators=[username_validator],
                                error_messages={'Проверка уникальности': 'Пользователь с таким именем уже существует!'},)
    is_active = models.BooleanField('active', default=False,
                                    help_text='Статус активности пользователя. \n'
                                              'Рекомендуется убрать метку вместо удаления пользователя')
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPES, max_length=10, default='buyer')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)


class ConfirmEmailToken(models.Model):

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE,
                              verbose_name='The User which is associated to this password reset token')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='When was this token generated')
    key = models.CharField('Key', max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return 'Password reset token for user {user}'.format(user=self.user)

    class Meta:
        verbose_name = 'Токен подтверждения email'
        verbose_name_plural = 'Токены подтверждения email'


