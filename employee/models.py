from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """ User model: identification by email, additional fields: first_name, last_name, father_name. """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=30, verbose_name='Name')
    last_name = models.CharField(max_length=50, verbose_name='Surname')
    father_name = models.CharField(max_length=50, verbose_name='Father\'s Name')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'father_name']

    objects = UserManager()

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.father_name}'


class Position(models.Model):
    name = models.CharField(max_length=30, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, null=True, on_delete=models.SET_NULL)
    boss = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, )
    level = models.PositiveSmallIntegerField(default=5)
    salary = models.DecimalField(max_digits=6, decimal_places=2)
    start_date = models.DateTimeField(null=True)

    def get_level(self):
        if not self.boss:
            return 0
        else:
            level = 1
            current_employee = self
            while level < 6:
                current_employee = current_employee.boss
                if current_employee.boss:
                    level += 1
                else: return level
            return level

    def save(self, *args, **kwargs):
        self.level = self.get_level()
        if self.level > 5:
            raise ValueError("Cannot save employee with hierarchy level more than 5")
        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} {self.user.father_name}'


class Paylog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.date} {self.employee.user.email}'
