import csv
import sys
import validators
import inflect
from datetime import date
from tabulate import tabulate


"""This program creates and maintains a user database. Users are stored
in a .csv file. Users can be administrators or regular users and options
after logging in vary based on this status.

This is obviously not a secure way to store user info but exists purely
for the purpose of practicing what I have learned in CS50.

Project started on 11/9 and completed on 11/16.
pycodestyle run on completion to ensure propoer PEP8 formatting.
"""


class User:
    """This class sets up a user with common format. Defining this as a
    class saves having all of this code appear multiple times throughout
    the program. This class takes in a user_type so that it can be
    initialized for both admin and regular users without having to create
    a separate class."""
    def __init__(self, user_type):
        self.user_type = user_type
        self.username = input("Enter a username for the account: ")
        self.password = input("Enter a password for the account: ")
        self.user_name = input("Enter your name: ").lower()
        self.email = self.validate_email()
        self.created_date = str(date.today())

    def validate_email(self):
        while True:
            _email = input("Enter your email: ")
            if validators.email(_email):
                return _email
            else:
                print("Invalid email format.")
                continue

    def user_dictionary(self):
        return {
            'username': self.username,
            'password': self.password,
            'name': self.user_name,
            'email': self.email,
            'user_type': self.user_type,
            'created_date': self.created_date
            }


def main():
    try:
        with open('users.csv') as user_file:
            reader = csv.DictReader(user_file)
            user_info = list(reader)
            login_page(user_info)
    except FileNotFoundError:
        if input("User file was not found. Would you like to proceed with"
                 " first time setup? Y/N ").lower() == "y":
            first_time_setup()
        else:
            sys.exit("Closing database...")


def first_time_setup():
    """This function is called when main() does not find an existing users.csv
    file upon program run. Users are prompoted to enter necessary data for an
    admninistrative account and this data is written to a new users.csv file.
    This function will only be called and used once at database setup. Once
    this information is written, users are brought to the user page under admin
    account."""
    # initialize admin user
    admin_user = User('admin')

    # create users.csv and save admin info as first record
    with open('users.csv', 'w', newline='') as user_file:
        fields = [
            'username', 'password', 'name', 'email', 'user_type',
            'created_date'
            ]
        writer = csv.DictWriter(user_file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(admin_user.user_dictionary())
        
    with open('users.csv', 'r') as user_file:
        reader = csv.DictReader(user_file)
        user_info = list(reader)

    # initial admin user created, send user to admin user landing page
    user_landing_page(admin_user.username, admin_user.user_type, user_info)


def user_landing_page(username, user_type, user_info):
    """This function serves as a landing page once a user has been logged in.
    The options available vary based on user type.
    """
    # initialize inflection pacakge for a/an determination
    p = inflect.engine()

    # creates lists for tabulate module to use in formatted tables
    headers = ['Option', 'Title', 'Description']
    admin_options = [
        ['1', 'User Management', 'Add, delete or ban users.'],
        ['2', 'Reports', 'Generate user/system reports.'],
        ['3', 'User Search', 'Find specific users.'],
        ['4', 'Quit', 'Close database.']
        ]
    user_options = [
        ['1', 'User Search', 'Find specific users.'],
        ['2', 'Quit', 'Close database.']
        ]

    # prints formatted tables with options
    print(f"\nHello, {username}. You are logged in as {p.a(user_type)}.")
    while True:
        if user_type == 'admin':
            print(tabulate(
                admin_options,
                headers=headers,
                tablefmt="fancy_outline",
                numalign="left")
                )
            user_choice = str(input("Select an option: "))
            if user_choice == "1":
                # User management
                user_management(user_info)
            elif user_choice == "2":
                # Admin reports
                admin_reports(user_info)
            elif user_choice == "3":
                # User Search
                user_search(user_info)
            else:
                sys.exit("Closing database...")
        else:
            print(print(tabulate(
                user_options,
                headers=headers,
                tablefmt="fancy_outline",
                numalign="left"
                )))
            user_choice = str(input("Select an option: "))
            if user_choice == "1":
                # user Search
                user_search(user_info)
            else:
                sys.exit("Closing database...")


def formatted_header(text):
    """This function prints a formatted header set for consistency"""
    dashes = "-" * (len(text) - 2)
    print(f"+{dashes}+\n{text}\n+{dashes}+\n")


def login_page(user_info):
    """This function serves as the login page for users. Users can select
    options for loggin in, resetting a password, or exiting."""
    welcome_text = "Welcome to the user database. Please select an option."
    headers = ['Option', 'Title', 'Description']
    login_options = [
        ['1', 'Login', 'Enter your login information.'],
        ['2', 'Create Account', 'Create a new user account.'],
        ['3', 'Forgot Password', 'Reset your password.'],
        ['4', 'Exit', 'Close the database.']
        ]

    formatted_header(welcome_text)
    print(tabulate(
        login_options,
        headers=headers,
        tablefmt="fancy_outline",
        numalign="left"
        ))
    while True:
        user_choice = input(f"\nSelect an option: ")
        if user_choice == '1':
            username = input("Username: ")
            password = input("Password: ")
            login_result = verify_user(username, password, user_info)
            if login_result[0] == 1:
                user_type = login_result[1]
                user_landing_page(username, user_type, user_info)
            else:
                print(login_result)
                continue
        elif user_choice == '2':
            create_user(user_info)
        elif user_choice == '3':
            print(forgot_password(user_info))
            continue
        else:
            sys.exit("Closing database...")


def verify_user(username, password, user_info):
    """
    This function accepts user entered username and password combination,
    as well as the list of user dictionary information. It checks the entered
    combination to ensure that the user exists and the password is correct,
    then returns the result.
    """
    user_list = generate_user_list(user_info)

    if username in user_list:
        if password == user_info[user_list.index(username)]['password']:
            login_result = 1
            user_type = user_info[user_list.index(username)]['user_type']
        else:
            return "Incorrect password. Please try again, or select another" \
                    " option."
    else:
        return "Username does not exist. Please try again, or select another" \
                " option."

    return [login_result, user_type]


def create_user(user_info, create_user_type='user', new_admin=''):
    """This function will add a new user to the users.csv file"""
    # define and get user info for account creation
    created_user = User(create_user_type)
    fields = [
        'username',
        'password',
        'name',
        'email',
        'user_type',
        'created_date'
        ]

    with open('users.csv', 'a+', newline='') as user_file:
        writer = csv.DictWriter(user_file, fieldnames=fields)
        writer.writerow(created_user.user_dictionary())

    # once user is created, send to user landing page.
    if new_admin == '':
        user_landing_page(
            created_user.username,
            created_user.user_type,
            user_info
            )


def forgot_password(user_info):
    """This function accepts an entered username and email address in the event
    that a user has forgotten their password. If the username and email exists
    and match to the same record, this function will return the user's
    password. As mentioned in the docstring, this is not the most secure
    solution."""
    username = input("Enter your username: ")

    user_list = generate_user_list(user_info)

    if username in user_list:
        email = input("Enter the email associated with the account: ")
        if email == user_info[user_list.index(username)]['email']:
            password = user_info[user_list.index(username)]['password']
            return f"Your password is '{password}'."
        else:
            return "The entered email does not match the user record." \
                    " Please try again or select another option."
    else:
        return "User not found. Please try again or select another option."


def generate_user_list(user_info):
    """This function goes through the user info dictionary and returns a list
    of users in that dictionary."""
    user_list = []

    for user in user_info:
        user_list.append(user['username'])

    return user_list


def user_search(user_info):
    """This function allows a user to search for a specific other user based on
    different criteria."""
    user_list = generate_user_list(user_info)

    headers = ['Option', 'Title']
    search_options = [
        ['1', 'Search by Username'],
        ['2', 'Search by Email'],
        ['3', 'Search by Name'],
        ['4', 'Return to Main Page']
        ]

    print(tabulate(
        search_options,
        headers=headers,
        tablefmt="fancy_outline",
        numalign="left"
        ))
    while True:
        user_choice = input(f"\nSelect an option: ")
        if user_choice == '1':
            # search by username
            to_search = input("Enter username to look for: ")
            if to_search in user_list:
                display_user_info(to_search, user_info)
        elif user_choice == '2':
            # search by email
            to_search = input("Enter email to search for: ")
            username = return_user('email', to_search, user_info)
            if username is False:
                print("No user with that email address.")
            else:
                display_user_info(username, user_info)
        elif user_choice == '3':
            # search by name
            to_search = input("Enter name to search for: ")
            username = return_user('name', to_search, user_info)
            if username is False:
                print("No user with that name.")
            else:
                display_user_info(username, user_info)
        else:
            break


def display_user_info(username, user_info):
    """This function will display all information associated with a specific
    user for the sake of consistency and less code in the search function."""
    for user in user_info:
        if user['username'] == username:
            for item in user:
                if item != 'password':
                    print(f"{item.capitalize()}: {user[item]}")
            print("\n")
        else:
            found_flag = 0


def return_user(info_type, input, user_info):
    """This function will look in the user_info for a particular item and
    return the username associated with that record."""
    for user in user_info:
        if user[info_type] == input:
            return user['username']
        else:
            found_flag = 0

    if found_flag == 0:
        return False


def ban_user(username):
    """This function will allow an admin user to add a specific user to the
    banned users list"""
    with open('banned.txt', 'a') as banned_file:
        banned_file.write(username)
        banned_file.write("\n")


def unban_user(username):
    """This function will unban a user by removing them from banned.txt. File
    will need to be rewritten"""
    banned_users = return_banned_list()
    if username in banned_users:
        banned_users.remove(username)
        with open('banned.txt', 'w') as banned_file:
            for user in banned_users:
                banned_file.write(user)
                banned_file.write("\n")
    else:
        print("User is not currently banned.")


def return_banned_list():
    """This function will open the banned text file and return a list of those
    users in list format."""
    banned_users = []
    try:
        with open('banned.txt', 'r') as banned_file:
            for user in banned_file:
                banned_users.append(user.strip())
            return banned_users
    except FileNotFoundError:
        return banned_users


def user_management(user_info):
    """This function will allow an admin user to ban or unban users, as well as
    create new admin users."""
    headers = ['Option', 'Title', 'Description']
    user_options = [
        ['1', 'Ban Users', 'Enter usernames to ban.'],
        ['2', 'Unban Users', 'Remove users from the banned user list.'],
        ['3', 'Add New Administrator', 'Create a new admin account.'],
        ['4', 'Return to Main Page']
        ]
    user_list = generate_user_list(user_info)

    print(tabulate(
        user_options,
        headers=headers,
        tablefmt="fancy_outline",
        numalign="left"
        ))
    while True:
        user_input = input("Select an option: ")
        if user_input == "1":
            # ban user
            to_ban = input("Select a user to ban: ")
            if to_ban in user_list:
                ban_user(to_ban)
                print(f"{to_ban} has been banned.")
            else:
                print("User not found.")
        elif user_input == "2":
            # unban user
            to_unban = input("Select a user to unban: ")
            banned_users = return_banned_list()
            if to_unban in banned_users:
                unban_user(to_unban)
            else:
                print("User is not currently banned.")
        elif user_input == "3":
            # create new admin user
            create_user(user_info, 'admin', 'new admin')
        else:
            break


def admin_reports(user_info):
    banned_users = return_banned_list()
    for user in banned_users:
        print(user)
    """This function allows administrative users to run a few reports based on
    the user data in the system."""

    headers = ['Option', 'Title', 'Description']
    user_options = [
        ['1', 'Banned Users List', 'Displays the list of banned users.'],
        ['2', 'User List', 'Displays the list of users in the system.'],
        ['3', 'User Age Report', 'Displays the list of users from oldest to'
            'newest.'],
        ['4', 'Return to Main Page']
        ]
    user_list = generate_user_list(user_info)

    print(tabulate(
        user_options,
        headers=headers,
        tablefmt="fancy_outline",
        numalign="left"
        ))
    while True:
        user_choice = input("Select an option: ")
        if user_choice == "1":
            banned_users = return_banned_list()
            print(f"There are currently {len(banned_users)} banned users:")
            counter = 0
            for user in banned_users:
                print(f"{counter + 1}. {user}")
        elif user_choice == "2":
            print(f"There are currently {len(user_list)} total users:")
            counter = 0
            for user in user_list:
                print(f"{counter + 1}. {user}")
        elif user_choice == "3":
            print('age')
            today = date.today()
            counter = 0
            for user in user_list:
                created_date = date.fromisoformat(user_age(user, user_info))
                age = today - created_date
                print(f"{counter + 1}. {user} - {age.days} days old")
        else:
            break


def user_age(username, user_info):
    """This function will calculate an return a users age in days."""
    for user in user_info:
        if user['username'] == username:
            return user['created_date']


if __name__ == "__main__":
    main()
