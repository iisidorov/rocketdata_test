from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib import admin
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

    class Meta:
        ordering = ('last_name', 'first_name', 'father_name',)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.father_name}'


class Position(models.Model):
    name = models.CharField(max_length=30, verbose_name='Name')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, null=True, on_delete=models.SET_NULL)
    boss = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, )
    level = models.PositiveSmallIntegerField(default=5)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(null=True)

    user.ordering = 'user__last_name'
    position.ordering = 'position__name'

    # Calculate hierarchy level
    def get_level(self):
        if not self.boss:
            return 0
        else:
            return self.boss.level + 1

    def is_boss_under_employee(self, boss):
        # If self record already exists
        if Employee.objects.filter(user=self.user):
            children = Employee.objects.filter(boss=self)
            for child in children:
                if child == boss:
                    return True
                else:
                    if child.is_boss_under_employee(boss):
                        return True
            return False

    def save(self, *args, **kwargs):
        self.level = self.get_level()
        if self.level > 4:
            raise ValueError("Cannot save employee with hierarchy level more than 5")
        if self.is_boss_under_employee(self.boss):
            raise ValueError("The specified boss is already obeys the current employee")

        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} {self.user.father_name}'


class Paylog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.date} {self.employee.user.email}'
