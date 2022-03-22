from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from .models import User, Position, Employee, Paylog


@admin.action(description='Delete total salary paid')
def delete_total_salary(modeladmin, request, queryset):
    Paylog.objects.filter(employee_id__in=queryset).delete()


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
    actions = [delete_total_salary]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.object_id = None

    # Get Total paid salary
    def total(self, obj):
        return Paylog.objects.filter(employee=obj.pk).aggregate(Sum('amount'))['amount__sum']

    # Get URL of the employee's boss
    def boss_url(self, obj):
        if obj.boss:
            return format_html("<a href='{url}'><b>{text}</b></a>", url=obj.boss.id, text=obj.boss)

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
