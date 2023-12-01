# For testing SQL Server connection in CSIL through pyodbc connection (using SQL Server standard login)
#
# Author: Sadra Manouchehrifar
#
# You should run this program on a CSIL system.
# Last modified @ 2023.03.30, 2020.06.02, 2018.03.27
#  verified with Python 3.11.1 64bit & SQL Server 2019, 2023.03.30
#  verified with Python 3.8.3 64bit & SQL Server 2019 (CSIL Linux), 2023.03.30
#  verified with Python 3.7.7 64bit & SQL Server 2019, 2020.06.02
#
# Please modify this program before using.
# alternation includes: 
#       the standard SQL Server login (which is formatted as s_<username>)
#       the passphrase for CSIL SQL Server standard login

import pyodbc
import string
import random

# Establish a connection to the CSIL SQL Server database.
conn = pyodbc.connect('driver={ODBC Driver 18 for SQL Server};server=cypress.csil.sfu.ca;uid=s_sma295;pwd=A72GaaMd6dH4GMq3;Encrypt=yes;TrustServerCertificate=yes')

 #  ^^^ 2 values must be changed for your own program.
 #  Since the CSIL SQL Server has configured a default database for each user, there is no need to specify it (<username><coursenumber>)

# Create a cursor for executing SQL queries.
cur = conn.cursor()
conn.close()

#  This program will output your CSIL SQL Server standard login,
#  If you see the output as s_<yourusername>, it means the connection is a success. 
#  You can now start working on your assignment.

# Function for user login.
def login():
    conn = pyodbc.connect('driver={ODBC Driver 18 for SQL Server};server=cypress.csil.sfu.ca;uid=s_sma295;pwd=A72GaaMd6dH4GMq3;Encrypt=yes;TrustServerCertificate=yes')
    cur = conn.cursor()

    # Prompt the user to enter their CSIL SQL Server login ID.
    while True:
        user_id = input("Enter your user ID: ")

        # Check if the entered user ID exists in the database.
        cur.execute('SELECT COUNT(*) FROM dbo.user_yelp WHERE user_id = ?', user_id)
        count = cur.fetchone()[0]

        # If the user ID is valid, log in and print a welcome message.
        if count == 1:
            print("Login successful. Welcome, {}!".format(user_id))
            return conn, cur, user_id
        else:
            print("Invalid user ID. Please try again.")

# Function to search for businesses based on various criteria.
def search_business(cur):
    print("\nSearch Business:")
    min_stars = input("Enter minimum number of stars: ")
    city = input("Enter city (press Enter to skip): ")
    name = input("Enter name or part of the name (press Enter to skip): ")
    order_by_option = input("Choose ordering (name, city, stars): ").lower()

    # Define valid options for ordering.
    valid_order_by_options = {'name': 'name', 'city': 'city', 'stars': 'stars'}

    # Select the appropriate column for ordering.
    order_by_column = valid_order_by_options.get(order_by_option)
    if order_by_column is None:
        print("Invalid ordering option. Using default order by 'name'.")
        order_by_column = 'name'

    # Construct the SQL query based on user input.
    sql_query = f"SELECT business_id, name, address, city, stars FROM Business WHERE stars >= {min_stars}"
    if city:
        sql_query += f" AND city LIKE '%{city}%'"
    if name:
        sql_query += f" AND name LIKE '%{name}%'"
    sql_query += f" ORDER BY {order_by_column}"

    # Execute the query and print the results.
    cur.execute(sql_query)
    results = cur.fetchall()

    if results:
        print("\nSearch Results:")
    for result in results:
        print(f"ID: {result.business_id}, Name: {result.name}, Address: {result.address}, City: {result.city}, Stars: {result.stars}")
    else:
        print("No results found.")

# Function to search for users based on various criteria.
def search_users(cur):
    print("\nSearch Users:")
    name = input("Enter name or part of the name: ")
    review_count = input("Enter minimum review count: ")
    average_stars = input("Enter minimum average stars: ")

    # Construct the SQL query based on user input.
    sql_query = f"SELECT user_id, name, review_count, useful, funny, cool, average_stars, yelping_since FROM user_yelp WHERE name LIKE '%{name}%'"
    if review_count:
        sql_query += f" AND review_count >= {review_count}"
    if average_stars:
        sql_query += f" AND average_stars >= {average_stars}"
    sql_query += " ORDER BY name"

    # Execute the query and print the results.
    cur.execute(sql_query)
    results = cur.fetchall()

    if results:
        print("\nSearch Results:")
        for result in results:
            print(f"ID: {result.id}, Name: {result.name}, Review Count: {result.review_count}, Useful: {result.useful}, Funny: {result.funny}, Cool: {result.cool}, Average Stars: {result.average_stars}, Registration Date: {result.registration_date}")
    else:
        print("No results found.")

# Function to make a friend connection between users.
def make_friend(cur, logged_in_user):
    print("\nMake Friend:")
    user_id_to_add = input("Enter the ID of the user you want to add as a friend: ")

    # Check if the entered user ID exists in the database.
    cur.execute("SELECT * FROM user_yelp WHERE user_id = ?", user_id_to_add)
    user_to_add = cur.fetchone()

    # If the user ID is valid, create a friendship connection.
    if user_to_add:
        cur.execute("INSERT INTO friendship (user_id, friend) VALUES (?, ?)", (logged_in_user, user_to_add.user_id))
        print(f"You are now friends with {user_to_add.name}.")
    else:
        print("Invalid user ID. No friendship created.")

# Function to record a review for a business.
def review_business(cur, logged_in_user):
    print("\nReview Business:")
    business_id = input("Enter the ID of the business you want to review: ")
    stars = input("Enter the number of stars (1-5): ")

    # Validate the input for stars.
    if not stars.isdigit() or not (1 <= int(stars) <= 5):
        print("Invalid input for stars. Stars must be a number between 1 and 5.")
        return

    # Generate a random string for the review ID.
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for _ in range(22))

    # Insert the review into the database.
    cur.execute(f"INSERT INTO review (review_id, user_id, business_id, stars, useful, funny, cool, date) VALUES ('{random_string}', '{logged_in_user}', '{business_id}', '{stars}', 0, 0, 0, GETDATE())")

    # Update the business's star rating and review count.
    cur.execute(f"UPDATE business SET stars = (SELECT AVG(stars) FROM review WHERE business_id = '{business_id}'), review_count = review_count + 1 WHERE business_id = '{business_id}'")

    print("Review recorded successfully.")

def main():
    # Establish a connection, create a cursor, and log in the user.
    conn, cur, logged_in_user = login()

    # Main menu loop.
    while True:
        print("\nMain Menu:")
        print("1. Search Business")
        print("2. Search Users")
        print("3. Make Friend")
        print("4. Review Business")
        print("5. Logout")

        # Get the user's choice.
        choice = input("Enter your choice (1-5): ")

        # Execute the chosen option based on user input.
        if choice == '1':
            search_business(cur)
        elif choice == '2':
            search_users(cur)
        elif choice == '3':
            make_friend(cur, logged_in_user)
        elif choice == '4':
            review_business(cur, logged_in_user)
        elif choice == '5':
            # Close the connection and exit the program.
            conn.close()
            print("Logout successful. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    # Run the main function if the script is executed directly.
    main()