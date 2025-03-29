import sqlite3
import hashlib

# Connect to the SQLite database
conn = sqlite3.connect('food_ordering.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        restaurant_id INTEGER,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES menu_items(id)
    )
''')

# Sample data initialization
# Insert restaurants
cursor.execute("INSERT OR IGNORE INTO restaurants (name) VALUES ('Pizza Palace')")
cursor.execute("INSERT OR IGNORE INTO restaurants (name) VALUES ('Sushi Heaven')")
cursor.execute("INSERT OR IGNORE INTO restaurants (name) VALUES ('Burger Barn')")

# Insert menu items for Pizza Palace
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Margherita Pizza', 10.99, 1)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Pepperoni Pizza', 12.99, 1)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Veggie Supreme Pizza', 11.99, 1)")

# Insert menu items for Sushi Heaven
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Sushi Roll', 8.99, 2)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Sashimi', 12.99, 2)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Tempura', 9.99, 2)")

# Insert menu items for Burger Barn
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Classic Burger', 9.99, 3)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Cheeseburger', 10.99, 3)")
cursor.execute("INSERT OR IGNORE INTO menu_items (name, price, restaurant_id) VALUES ('Bacon Burger', 11.99, 3)")


# Function for user registration
def register_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    print("Registration successful!")

# Function for user login
def login_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_password))
    user = cursor.fetchone()
    if user:
        print("Login successful! Welcome, " + username + "!")
        return user[0]  # Return the user ID
    else:
        print("Invalid username or password.")
        return None

def browse_restaurants():
    cursor.execute('SELECT * FROM restaurants')
    restaurants = cursor.fetchall()
    if not restaurants:
        print("No restaurants available.")
        return
    print("Available Restaurants:")
    for restaurant in restaurants:
        print(f"{restaurant[0]}. {restaurant[1]}")
    
    restaurant_id = input("Please enter the number of the restaurant you'd like to browse: ")
    cursor.execute('SELECT * FROM menu_items WHERE restaurant_id=?', (restaurant_id,))
    menu_items = cursor.fetchall()
    if not menu_items:
        print("No menu items available for this restaurant.")
        return
    print(f"\nMenu for {restaurants[int(restaurant_id)-1][1]}:")
    
    # Create a set to store unique menu item names
    unique_items = set()
    for item in menu_items:
        if item[1] not in unique_items:  # Check if item name is unique
            print(f"{item[0]}. {item[1]} - ${item[2]}")
            unique_items.add(item[1])  # Add item name to the set of unique items







# Function for placing orders
def place_order(user_id):
    item_id = input("\nPlease enter the number of the item you'd like to add to your cart (or 0 to go back): ")
    if item_id == '0':
        return
    quantity = int(input("Quantity: "))
    cursor.execute('INSERT INTO orders (user_id, item_id, quantity) VALUES (?, ?, ?)', (user_id, item_id, quantity))
    conn.commit()
    print("Item added to cart.")

# Function for viewing cart
def view_cart(user_id):
    cursor.execute('''
        SELECT menu_items.name, menu_items.price, orders.quantity
        FROM orders
        JOIN menu_items ON orders.item_id = menu_items.id
        WHERE orders.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    total = sum(item[1] * item[2] for item in cart_items)
    print("\nYour Cart:")
    if not cart_items:
        print("Your cart is empty.")
    else:
        for i, item in enumerate(cart_items, 1):
            print(f"{i}. {item[0]} - ${item[1]} x {item[2]}")
        print(f"\nTotal: ${total}")

    return cart_items, total

# Function for removing item from cart
def remove_item(user_id):
    while True:
        cart_items, _ = view_cart(user_id)
        if not cart_items:
            print("Your cart is empty.")
            return

        item_number = int(input("Enter the number of the item you want to remove: "))
        if item_number < 1 or item_number > len(cart_items):
            print("Invalid item number.")
            continue

        item_id = cart_items[item_number - 1][0]
        cursor.execute('DELETE FROM orders WHERE user_id=? AND item_id=?', (user_id, item_id))
        conn.commit()
        print("Item removed from cart.")
        choice = input("Do you want to view your updated cart (1) or proceed to checkout (2)? ")
        if choice == '1':
            view_cart(user_id)  # View the updated cart
        elif choice == '2':
            checkout(user_id)  # Proceed to checkout
        else:
            print("Invalid choice.")
            
# Function for checking out
def checkout(user_id):
    cursor.execute('''
        SELECT menu_items.name, menu_items.price, orders.quantity
        FROM orders
        JOIN menu_items ON orders.item_id = menu_items.id
        WHERE orders.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    if not cart_items:
        print("Your cart is empty.")
        return

    total = sum(item[1] * item[2] for item in cart_items)
    print("\nYour Cart:")
    for i, item in enumerate(cart_items, 1):
        print(f"{i}. {item[0]} - ${item[1]} x {item[2]}")
    print(f"\nTotal: ${total}")

    confirm = input("Confirm checkout (yes/no): ").lower()
    if confirm == 'yes':
        print(f"Order placed successfully! Your total is ${total}.")
        cursor.execute('DELETE FROM orders WHERE user_id=?', (user_id,))
        conn.commit()
    else:
        print("Checkout cancelled.")
        
def view_cart(user_id):
    # Fetch the cart items
    cursor.execute('''
        SELECT menu_items.name, menu_items.price, orders.quantity
        FROM orders
        JOIN menu_items ON orders.item_id = menu_items.id
        WHERE orders.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    total = 0
    
    # Check if the cart is empty
    if not cart_items:
        print("Your cart is empty.")
        return [], total
    
    # Display the cart items
    print("\nYour Cart:")
    for i, item in enumerate(cart_items, 1):
        print(f"{i}. {item[0]} - ${item[1]} x {item[2]}")
        total += item[1] * item[2]

    print(f"\nTotal: ${total}")

    return cart_items, total









def main():
    print("Welcome to Our Food Ordering System!")
    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Please enter your choice: ")

        if choice == '1':
            username = input("Username: ")
            password = input("Password: ")
            user_id = login_user(username, password)
            if user_id:
                while True:
                    print("\n1. Browse Restaurants")
                    print("2. View Cart")
                    print("3. Logout")
                    inner_choice = input("\nPlease enter your choice: ")
                    if inner_choice == '1':
                        browse_restaurants()
                        place_order(user_id)
                    elif inner_choice == '2':
                        while True:
                            print("\nYour Cart:")
                            cart_items, total = view_cart(user_id)
                            if not cart_items:
                                break
                            print("\n1. Checkout")
                            print("2. Remove Item")
                            print("3. Back to Menu")
                            cart_choice = input("\nPlease enter your choice: ")
                            if cart_choice == '1':
                                checkout(user_id)
                                break
                            elif cart_choice == '2':
                                remove_item(user_id)
                            elif cart_choice == '3':
                                break
                            else:
                                print("Invalid choice.")
                    elif inner_choice == '3':
                        print("Logged out successfully. Goodbye!")
                        break
                    else:
                        print("Invalid choice.")
        elif choice == '2':
            username = input("Username: ")
            password = input("Password: ")
            register_user(username, password)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
