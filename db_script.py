"""
Example of DB populating:
> py populate_db_script
"""
import os
import random
import psycopg2
from dotenv import load_dotenv


""" Clear all data and create employees """
REFRESH = 'refresh'

""" Clear all data """
CLEAR = 'clear'

# Modify executing options:
DEBUG = False       # Additional logs
MODE = REFRESH      # REFRESH / CLEAR
NUMBER = 200        # Final amount of employees to create


""" General random values """
POSITIONS = ["Team Lead", "Junior Developer", "Middle Developer", "Senior Developer",
             "Human Resource", "Junior Manager", "Middle Manager", "Senior Manager"]
FIRST_NAMES = ["Vano", "Rock", "Alex", "Justine", "Vlad", "Arnold", "Max", "Yuri",
              "Aska", "Sindzi", "Misato", "Ray", "Bruce", "Haruhiya", "Dzheki", "Djiraya"]
LAST_NAMES = ["Sidorov", "Petrov", "Ivanov", "Dashkevich", "Dzuba", "Savchenko", "Zahojiy", "Makarov",
             "Takamuro", "Hanokomaru", "Vi", "Sudzumiya", "Chan", "Lee", "Columb", "Schwarzenegger"]
FATHER_NAMES = ["Ivanovich", "Black", "Johnson", "Alexandrovich", "Peterson", "Vitalevich", "Jameson", "Hoan",
               "Richardson", "Clarkson", "Branson", "White", "Igorevich", "Pink", "Crandston", "Sergeevna"]
EMAILS = []
POSITIONS_ID = []
USERS_LEVEL_ID = []
EMPLOYEES_LEVEL_ID = []

# Import environment variables
load_dotenv()
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except psycopg2.OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        cursor.close()
    except psycopg2.OperationalError as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except psycopg2.Error as e:
        print(f"The error '{e}' occurred")


def clear_data(connection):
    # Save admin row
    admin_exists = False
    query = f"""
    SELECT password FROM employee_user
    WHERE email='{ADMIN_EMAIL}'
    """
    try:
        password = execute_read_query(connection, query)
        password = password[0][0]
        admin_exists = True
    except Exception as e:
        print("No admin instance", f"Exception: [{e}]")
        execute_query(connection, "ROLLBACK;")

    # Clearing all tables
    query = """
    BEGIN;
    TRUNCATE TABLE django_celery_beat_periodictask CASCADE;
    TRUNCATE TABLE django_celery_beat_intervalschedule CASCADE;
    TRUNCATE TABLE employee_basemodel CASCADE;
    TRUNCATE TABLE employee_user CASCADE;
    TRUNCATE TABLE employee_position CASCADE;
    COMMIT;
    """
    execute_query(connection, query)
    print("Tables cleared")

    if admin_exists:
        create_users(connection, [(ADMIN_EMAIL, password, 'admin',
                                   'admin', 'admin', True, True)])


def populate_positions(connection):
    ids = []
    query = """
    INSERT INTO employee_position (name)
    VALUES"""
    for pos in POSITIONS:
        query += f"\n('{pos}'),"
    query = query[:-1]
    query += "RETURNING id"
    positions_id = execute_read_query(connection, query)
    [ids.append(pk[0]) for pk in positions_id]
    POSITIONS_ID.extend(ids)
    print("Positions populated")


def create_users(connection, list_of_users):
    # Crate BaseModel objects
    query = """INSERT INTO employee_basemodel(date_created, date_updated) VALUES """
    for _ in list_of_users:
        query += "\n(current_timestamp, current_timestamp),"
    query = query[:-1]
    query += "\nRETURNING id"
    ids = execute_read_query(connection, query)
    pks = []
    [pks.append(pk[0]) for pk in ids]

    # Create Users
    query = f"""
        INSERT INTO employee_user
        (basemodel_ptr_id, email, password, first_name, last_name, 
        father_name, is_superuser, is_staff, is_active)
        VALUES """
    for i, user in enumerate(list_of_users):
        pk = pks[i]
        email = user[0]
        password = user[1]
        name = user[2]
        lname = user[3]
        fname = user[4]
        is_superuser = False
        if len(user) > 5:
            is_superuser = user[5]
        is_staff = False
        if len(user) > 6:
            is_staff = user[6]
        query += f"\n('{pk}', '{email}', '{password}', '{name}', " \
                 f"'{lname}', '{fname}', {is_superuser}, {is_staff}, true),"
    query = query[:-1]
    query += "\n RETURNING basemodel_ptr_id"
    execute_query(connection, query)
    return pks


def generate_email(email):
    if email in EMAILS:
        return generate_email("0" + email)
    else:
        return email


def create_paylogs(connection, employees_id, salaries):
    query = """INSERT INTO employee_paylog (date, amount, employee_id) VALUES"""
    for i in range(len(employees_id)):
        for paylog_count in range(random.randint(0, 5)):
            amount = salaries[i]
            query += f"\n(current_timestamp, {amount}, {employees_id[i]}),"
    query = query[:-1]
    execute_query(connection, query)
    if DEBUG: print("Paylogs populated")


def create_employees(connection, users_id, level):
    ids = []
    salaries = []
    query = """INSERT INTO employee_employee (level, salary, start_date, boss_id, position_id, user_id) VALUES"""
    for user_id in users_id:
        salary = str(random.randint(500, 10000))
        salaries.append(salary)
        boss_id = 'null' if level == 0 else str(random.choice(EMPLOYEES_LEVEL_ID[-1]))
        position_id = str(random.choice(POSITIONS_ID))
        query += f"\n({level}, {salary}, current_timestamp, {boss_id}, {position_id}, {user_id}),"
    query = query[:-1]
    query += "RETURNING id"
    pks = execute_read_query(connection, query)
    [ids.append(pk[0]) for pk in pks]
    EMPLOYEES_LEVEL_ID.append(ids)
    if DEBUG: print(f"Employees on level {level} created: {ids}")
    create_paylogs(connection, ids, salaries)
    return ids


def populate_employees_on_level(connection, level, amount):
    users = []
    for i in range(amount):
        # Generate User
        name = random.choice(FIRST_NAMES)
        surname = random.choice(LAST_NAMES)
        thirdname = random.choice(FATHER_NAMES)
        email = generate_email(f"{name.lower()}@{surname.lower()}.com")
        EMAILS.append(email)
        users.append((email, '123', name, surname, thirdname))

    # Get all created users id
    users_id = create_users(connection, users)

    # Create Employee
    create_employees(connection, users_id, level)   # list of employees' ids


def run_script():
    conn = create_connection(
        db_name=os.environ.get('POSTGRES_DB'),
        db_user=os.environ.get('POSTGRES_USER'),
        db_password=os.environ.get('POSTGRES_PASSWORD'),
        db_host=os.environ.get('POSTGRES_HOST'),
        db_port=os.environ.get('POSTGRES_PORT')
    )

    # Clear data from tables
    clear_data(conn)
    if MODE == CLEAR:
        return

    # Positions table
    populate_positions(conn)

    # Number of employees on each level:
    levels = (
        1,                                  # 0
        int(0.1 * NUMBER),                  # 1
        int(0.2 * NUMBER),                  # 2
        int(0.3 * NUMBER),                  # 3
        NUMBER - int(0.6 * NUMBER) - 1,     # 4
    )

    # User, Employee, Paylog tables
    for i, amount in enumerate(levels):
        populate_employees_on_level(conn, i, amount)
    print("Employees populated")


if __name__ == "__main__":
    run_script()

