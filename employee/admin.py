import json

from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from celery.schedules import crontab

from .models import User, Position, Employee, Paylog
from .tasks import delete_total_salary_task, pay_salary_task


@admin.action(description='Delete total salary paid')
def delete_total_salary(modeladmin, request, queryset):
    list_ids = list(queryset.values_list('id', flat=True))
    if len(list_ids) > 20:
        delete_total_salary_task.delay(list_ids)
    else:
        delete_total_salary_task(list_ids)


@admin.action(description='Start paying salary')
def pay_salary(modeladmin, request, queryset):
    every = 2
    period = 'hours'
    list_ids = list(queryset.values_list('id', flat=True))
    interval = IntervalSchedule.objects.filter(every=every, period=period).first()
    if not interval:
        interval = IntervalSchedule(every=every, period=period)
        interval.save()
    for emp_id in list_ids:
        if not PeriodicTask.objects.filter(name=f'Employee: {emp_id}'):
            period_task = PeriodicTask.objects.create(
                name=f'Employee: {emp_id}',
                task='employee.tasks.pay_salary_task',
                interval=interval,
                args=json.dumps([emp_id]),
                start_time=timezone.now()
            )
            period_task.save()


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'father_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'father_name', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    list_display = ('email', 'last_name', 'first_name', 'father_name')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'boss_url', 'level', 'salary', 'total')
    exclude = ('level', )
    list_filter = ['position', 'level']
    actions = [delete_total_salary, pay_salary]

    # Get Total paid salary
    def total(self, obj):
        return Paylog.objects.filter(employee=obj.pk).aggregate(Sum('amount'))['amount__sum']

    # Get URL of the employee's boss
    def boss_url(self, obj):
        if obj.boss:
            return format_html("<a href='{url}'><b>{text}</b></a>", url=obj.boss.id, text=obj.boss)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.object_id = None

    # Prevent saving model if data is incorrect
    def save_model(self, request, obj, form, change):
        try:
            super(EmployeeAdmin, self).save_model(request, obj, form, change)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    # Set EmployeeAdmin.object_id = Employee.object_id if employee is opened for update
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.object_id = object_id
        return super(EmployeeAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    # Exclude self object from boss list to avoid making yourself a boss of yourself (if employee exists)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "boss" and self.object_id:
            kwargs['queryset'] = Employee.objects.exclude(pk=self.object_id)
        return super(EmployeeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Paylog)
class PaylogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'amount')
