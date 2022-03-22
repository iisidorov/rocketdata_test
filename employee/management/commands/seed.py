"""
Seeds Database tables with random data. Example to launch seeding:
> python manage.py seed --mode=refresh --number=40
mode options: refresh/clear
number: final amount of created Employees
"""

import random
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from employee.models import Position, User, Employee, Paylog

DEBUG = False

""" Clear all data and create employees """
MODE_REFRESH = 'refresh'

""" Clear all data """
MODE_CLEAR = 'clear'

""" General random values """
POSITIONS = ["Team Lead", "Junior Developer", "Middle Developer", "Senior Developer",
             "Human Resource", "Junior Manager", "Middle Manager", "Senior Manager"]
FIRST_NAMES = ["Vano", "Rock", "Alex", "Justine", "Vlad", "Arnold", "Max", "Yuri",
              "Aska", "Sindzi", "Misato", "Ray", "Bruce", "Haruhiya", "Dzheki", "Djiraya"]
LAST_NAMES = ["Sidorov", "Petrov", "Ivanov", "Dashkevich", "Dzuba", "Savchenko", "Zahojiy", "Makarov",
             "Takamuro", "Hanokomaru", "Vi", "Sudzumiya", "Chan", "Lee", "Columb", "Schwarzenegger"]
FATHER_NAMES = ["Ivanovich", "Black", "Johnson", "Alexandrovich", "Peterson", "Vitalevich", "Jameson", "Hoan",
               "Richardson", "Clarkson", "Branson", "White", "Igorevich", "Pink", "Crandston", "Sergeevna"]


class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")
        parser.add_argument('--number', type=int, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        run_seed(self, options)
        self.stdout.write('Done.')


def random_date():
    start = datetime.strptime('2021-01-01 16:50:00', '%Y-%m-%d %H:%M:%S')
    delta = datetime.strptime('2022-03-22 19:07:18', '%Y-%m-%d %H:%M:%S') - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return make_aware(start + timedelta(seconds=random_second))


def generate_email(email):
    if User.objects.filter(email=email):
        return generate_email("0" + email)
    else:
        return email


def clear_data(cmd):
    """Deletes all the table data"""
    Position.objects.all().delete()
    User.objects.all().delete()
    cmd.stdout.write("Tables cleared")


def populate_positions():
    for pos in POSITIONS:
        position = Position(name=pos)
        position.save()


def populate_employees_on_level(level, count, cmd):
    for i in range(count):
        # Create User
        name = random.choice(FIRST_NAMES)
        surname = random.choice(LAST_NAMES)
        thirdname = random.choice(FATHER_NAMES)
        email = generate_email(f"{name.lower()}@{surname.lower()}.com")
        user = User(
            email=email,
            password="123",
            first_name=name,
            last_name=surname,
            father_name=thirdname,
        )
        user.save()
        if DEBUG: cmd.stdout.write(f"User {email} created.")

        # Create Employee
        if level == 0:
            boss = None
        else:
            boss = Employee.objects.filter(level=level - 1).order_by('?').first()
        employee_salary = random.randint(500, 10000)
        employee = Employee(
            user=user,
            position=Position.objects.filter(name=random.choice(POSITIONS)).first(),
            boss=boss,
            salary=employee_salary,
            start_date=random_date(),
        )
        employee.save()

        # Populate Pay Log
        for _ in range(random.randint(0, 5)):
            paylog = Paylog(
                employee=employee,
                date=random_date(),
                amount=employee_salary,
            )
            paylog.save()

        if DEBUG: cmd.stdout.write(f"Employee {surname} {name} created.")


def run_seed(cmd, options):
    """ Seed database based on mode: refresh / clear """
    # Clear data from tables
    clear_data(cmd)
    if options['mode'] == MODE_CLEAR:
        return

    # Positions table
    populate_positions()

    # General number of employees to create (=100 if empty)
    number = options['number'] if options['number'] else 100

    # Number of employees on each level:
    levels = (
        1,                                  # 0
        int(0.1 * number),                  # 1
        int(0.2 * number),                  # 2
        int(0.3 * number),                  # 3
        number - int(0.6 * number) - 1,     # 4
    )

    User.objects.create_superuser(email='admin@admin.com', password='admin')

    # User, Employee, Paylog tables
    for i, level in enumerate(levels):
        populate_employees_on_level(i, level, cmd)
