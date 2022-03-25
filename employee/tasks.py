from django.shortcuts import get_object_or_404
from django.utils import timezone
from emplatform.celery import app
from .models import Paylog, Employee


@app.task
def delete_total_salary_task(employee_ids):
    Paylog.objects.filter(employee_id__in=employee_ids).delete()


@app.task
def pay_salary_task(employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    paylog = Paylog(employee=employee, date=timezone.now(), amount=employee.salary)
    paylog.save()
