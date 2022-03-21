from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import User, Position, Employee, Paylog


@admin.action(description='Delete total salary paid')
def delete_total_salary(modeladmin, request, queryset):
    Paylog.objects.filter(employee_id__in=queryset).delete()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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

    # Get Total paid salary
    def total(self, obj):
        return Paylog.objects.filter(employee=obj.pk).aggregate(Sum('amount'))['amount__sum']

    # Get URL of the employee's boss
    def boss_url(self, obj):
        if obj.boss:
            return format_html("<a href='{url}'><b>{text}</b></a>", url=obj.boss.id, text=obj.boss)

    # Exclude self object from boss list (to avoid making yourself a boss of yourself =) )
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.object_id = object_id
        return super(EmployeeAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "boss":
            kwargs['queryset'] = Employee.objects.exclude(pk=self.object_id)
        return super(EmployeeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Paylog)
class PaylogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'amount')
