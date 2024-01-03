# Imports all the necessary libraries for the program
import sqlite3
import bcrypt
import maskpass
import datetime
import os

# Sets Up Global Variables that holds current user's role (Admin or Normal)
global CurrentUserRole
CurrentUserRole = None

# Function which returns user to the correct menu
def ReturnToMenu():
    input("PRESS ENTER TO RETURN TO MENU...")
    if CurrentUserRole == "admin":
        AdminMenu()
    else:
        menu()

def Connect_To_Database():
    # Function to connect the Code to the database
    return sqlite3.connect("SDIMS.db")

    
def CreateTables():
    # Create the Tables required for the database if they don't exist
    with Connect_To_Database() as con:
        cur = con.cursor()
        # Creates the stock table
        cur.execute("""CREATE TABLE IF NOT EXISTS stock
                    (
                    Product_ID INTEGER PRIMARY KEY,
                    Product_Name TEXT,
                    Cost REAL,
                    Quantity INTEGER,
                    Supplier_ID INTEGER,
                    Supplier_Cost INTEGER
                    )
                    """)
        con.commit()
        # Creates the sales table
        cur.execute("""CREATE TABLE IF NOT EXISTS sales
                    (
                    Sale_ID INTEGER PRIMARY KEY,
                    Product_ID INTEGER,
                    Amount INTEGER,
                    Total REAL,
                    Date TEXT,
                    Profit REAL
                    )
                    """)
        con.commit()
        # Creates the users table
        cur.execute("""CREATE TABLE IF NOT EXISTS users
                    (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                    )
                    """)
        con.commit()
        # Creates the supplier table
        con.execute("""CREATE TABLE IF NOT EXISTS supplier
                    (
                    Supplier_ID INTEGER PRIMARY KEY,
                    Supplier_Name TEXT,
                    Email TEXT,
                    Phone INTEGER
                    )
                    """)
        con.commit()


def CreateUsers():
    # Function to allow the creation of new users that can log into the program
    while True:
        username = input("ENTER USERNAME: ").strip().lower()

        # Get the password and hashes it for security by running it through the HashPass() Function
        HiddenPassword = maskpass.advpass(prompt="ENTER PASSWORD: ")
        NormalPassword = HiddenPassword.strip().encode('utf-8')
        UserPass = HashPass(NormalPassword).decode('utf-8')

        # Set the Role for the user
        Role = input("IS THIS USER AN ADMIN? [Y/N]: ").strip().upper()
        UserRole = "admin" if Role == "Y" else "default"

        # Updates the User into the database
        if SaveUsers(username, UserPass, UserRole):
            print("USER ACCOUNT SUCCESSFULLY CREATED")
        else:
            print("ERROR CREATING ACCOUNT")
        # Prompts the user if they want to add another user to the database
        if input("WOULD YOU LIKE TO ADD ANOTHER? [Y/N]: ").strip().upper() != "Y":
            break


def HashPass(NormalPassword):
    # Function to hash the password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(NormalPassword, salt)


def SaveUsers(username, password, role):
    # Function to save the new user's credentials to the database
    os.system('cls')
    try:
        with Connect_To_Database() as con: # Calls back to the Connect_To_Database Function 
            cur = con.cursor() # Creates a cursor that will interact with database
            cur.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, role))
            con.commit()
        return True
    except sqlite3.Error as e: # If there is an error with the database, it gives back an error
        print(f"DATABASE ERROR: {e}")
        return False


def ViewUsers():
    # Function to View all the users in the Database
    os.system('cls')
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            cur.execute("SELECT username, role FROM users")
            users = cur.fetchall()
            if not users:
                print("NO USERS FOUND")
                return
            print("USER'S LIST:")
            for user in users:
                print(f"USERNAME: {user[0]} | ROLE: {user[1]}")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def ResetPassword():
    # Function to reset a users password
    os.system('cls')
    ViewUsers()

    try:
        with Connect_To_Database() as con:
            cur = con.cursor()

            username = input("ENTER USERNAME YOU WISH TO RESET: ").strip().lower()
            cur.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cur.fetchone() is None:
                print("No user found with that username.")
                return

            new_password = maskpass.advpass(prompt="Enter new password: ").strip().encode('utf-8')
            hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode('utf-8')

            cur.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
            con.commit()
            print("Password reset successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

        
def DeleteNonAdmin():
    # Function to delete non-admin users, can only be accessed by admin users.
    ViewUsers()
    # Promt user input
    username = input("ENTER USERNAME YOU WOULD LIKE TO REMVE: ")

    try:
        with Connect_To_Database() as con:
            cur = con.cursor()

            cur.execute("SELECT role FROM users WHERE username = ?", (username,))
            user_role = cur.fetchone()

            if user_role is None:
                print("NO USER FOUND MATCHING THIS USERNAME")
            elif user_role[0].lower() == 'admin':
                print("CANNOT REMOVE ADMIN USERS")
            else:
                cur.execute("DELETE FROM users WHERE username = ?", (username,)) # Deletes user from table
                if cur.rowcount > 0:
                    print(f"{username} DELETED")
                else:
                    print(f"ERROR DELETING {username}")
            con.commit()

    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def AddProduct():
    # Function to add a product to the stock table
    while True:
        try:
            with Connect_To_Database() as con:
                cur = con.cursor()

                # Check for existing suppliers
                cur.execute("SELECT * FROM supplier")
                suppliers = cur.fetchall()

                if suppliers:
                    print("AVAILABLE SUPPLIERS:")
                    for supplier in suppliers:
                        print(f"ID: {supplier[0]}, NAME: {supplier[1]}")
                    print("ENTER 'NEW' TO ADD A NEW SUPPLIER.")
                else:
                    print("NO SUPPLIERS FOUND. PLEASE ADD A SUPPLIER FIRST.")

                supplier_input = input("ENTER SUPPLIER ID FOR THE PRODUCT OR 'NEW' TO ADD A SUPPLIER: ")

                if supplier_input.lower() == "new":
                    AddSupplier()  # Call function to add a new supplier
                    continue  # Restart the loop to show updated list of suppliers
                else:
                    supplier_id = int(supplier_input)

                product_name = input("ENTER PRODUCT NAME: ").strip()
                cur.execute("SELECT * FROM stock WHERE Product_Name = ?", (product_name,))
                if cur.fetchone():
                    print("PRODUCT ALREADY EXISTS IN STOCK")
                    return

                while True:
                    cost = input("ENTER COST PER UNIT: ")
                    if cost.isdigit() and float(cost) >= 0:
                        cost = float(cost)
                        break
                    else:
                        print("ENTER VALID INPUT")
                        
                while True:
                    quantity = input("ENTER QUANTITY: ")
                    if quantity.isdigit() and int(quantity) >= 0:
                        quantity = int(quantity)
                        break
                    else:
                        print("ENTER VALID INPUT")
                        
                while True:
                    supplier_cost = input("ENTER SUPPLIER COST PER UNIT: ")
                    if supplier_cost.isdigit() and float(supplier_cost) >= 0:
                        supplier_cost = float(supplier_cost)
                        break
                    else:
                        print("ENTER VALID INPUT")


                cur.execute("INSERT INTO STOCK (Product_Name, Cost, Quantity, Supplier_ID, Supplier_Cost) VALUES (?, ?, ?, ?, ?)", 
                            (product_name, cost, quantity, supplier_id, supplier_cost))
                con.commit()
                print("PRODUCT SUCCESSFULLY ADDED TO THE STOCK.")
                return

        except sqlite3.IntegrityError:
            print("THIS SUPPLIER DOES NOT EXIST. PLEASE ENTER A VALID SUPPLIER ID.")
        except sqlite3.Error as e:
            print(f"DATABASE ERROR: {e}")
        except ValueError:
            print("INVALID INPUT! PLEASE ENSURE CORRECT VALUES ARE ENTERED.")


def ViewStock():
# Function to display all the current stock
    with Connect_To_Database() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM stock")
        rows = cur.fetchall()

        if not rows:
            print("STOCK EMPTY")
            return
        
        for row in rows:
            print(f"PRODUCT ID: {row[0]} | PRODUCT NAME: {row[1]} | COST: {row[2]:.2f} | QUANTITY: {row[3]} | SUPPLIER ID: {row[4]} | SUPLLIER COST: {row[5]:.2f}")
            
def Reorder_Check():
    while True:
        threshold = input("ENTER REORDER VALUE (LEAVE BLANK TO RETURN TO MENU): ")
        if threshold.isdigit() and int(threshold) >= 0:
            break
        elif threshold == "":
            ReturnToMenu()
        else:
            print("INVALID INPUT, TRY AGAIN")
    with Connect_To_Database() as con:
        cur = con.cursor()
        
        cur.execute("SELECT Product_Name, Quantity FROM stock WHERE Quantity < ?", (threshold,))
        low_stock = cur.fetchall()
        if not low_stock:
            print("NO NEED TO REORDER ITEMS")
        else:
            print("LOW STOCK ITEMS TO REORDER: ")
            for item in low_stock:
                print(f"PRODUCT: {item[0]} | QUANTITY: {item[1]}")
        
        cur.execute("SELECT Product_Name, Quantity FROM stock WHERE Quantity = 0")
        OOS = cur.fetchall()
        if not OOS:
            print("NOTHING OUT OF STOCK")
        else:
            print("OUT OF STOCK:")
            for item in OOS:
                print(f"PRODUCT: {item[0]} | QUANTITY: {item[1]}")


def UpdateStock():
# Function to Update stock details
# Connects to the database, Prompts user to input the product they wish to update and then saves the updates to the table
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            ViewStock()
            
            Product_ID = int(input("ENTER PRODUCT ID: "))
            cur.execute("SELECT * FROM stock WHERE Product_ID = ?", (Product_ID,))
            product = cur.fetchone()
            if not product:
                print("INCORRECT ID, NO PRODUCT EXISTS WITH THIS ID")
                return
            print(f"PRODUCT NAME: {product[1]}, COST: {product[2]}, QUANTITY: {product[3]}")

            new_pname = input("INPUT NEW PRODUCT NAME: ").strip()
            
            while True:
                new_cost = input("INPUT NEW COST: ").strip()
                if new_cost.isdigit() and float(new_cost) >= 0:
                    new_cost = float(new_cost)
                    break
                else:
                    print("ENTER VALID INPUT: ")

            while True:
                new_quantity = input("INPUT NEW QUANTITY").strip()
                if new_quantity.isdigit() and int(new_quantity) >= 0:
                    new_quantity = int(new_quantity)
                    break
                else:
                    print("ENTER VALID INPUT: ")
        
            while True:
                new_Supp_cost = input("INPUT NEW SUPPLIER COST").strip()
                if new_Supp_cost.isdigit() and float(new_Supp_cost) >= 0:
                    new_Supp_cost = float(new_Supp_cost)
                    break
                else:
                    print("ENTER VALID INPUT: ")

            if new_pname:
                cur.execute("UPDATE stock SET Product_Name = ? WHERE Product_ID = ?", (new_pname, Product_ID))
            if new_cost:
                cur.execute("UPDATE stock SET Cost = ? Where Product_ID = ?", (float(new_cost), Product_ID))
            if new_quantity:
                cur.execute("UPDATE stock SET Quantity = ? WHERE Product_ID = ?", (int(new_quantity), Product_ID))
            if new_Supp_cost:
                cur.execute("UPDATE stock SET Supplier_Cost = ? WHERE Product_ID = ?", (float(new_Supp_cost), Product_ID))

            con.commit()
            print("PRODUCT DETAILS UPDATED")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: [e]")
    except ValueError:
        print("INVALID INPUT, ENSURE CORRECT VALUES ARE ENTERED FOR COST AND QUANTITY")

def DeleteProduct():
# Function to delete a product from the database
    ViewStock()
    product = input("ENTER THE USER YOU WISH TO REMOVE: ")
    
    with Connect_To_Database() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM stock WHERE Product_ID = ?", (product,))
        if cur.rowcount > 0:
            print("PRODUCT DELETED")
        else:
            print("NO PRODUCT MATCHING THIS NAME FOUND")
        con.commit()


def CreateSale():
# Function to create a sale with a customer, follows a similar process as the AddProduct Function but changes the table and column to sales table
# AlsO Calculates profit made on the sale
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            ViewStock()

            product_id = input("ENTER THE PRODUCT ID OF THE ITEM BEING SOLD (LEAVE BLANK TO RETURN TO MENU): ").strip()
            if product_id == "":
                SalesAndTransactions()
            cur.execute("SELECT * FROM stock WHERE Product_ID = ?", (product_id,))
            product = cur.fetchone()

            if not product:
                print("NO PRODUCT MATCHING THIS ID")
                return
                
            while True:
                quantity_sold = input(f"INPUT THE QUANTITY OF {product[1]} BEING SOLD: ").strip()
                if quantity_sold.isdigit() and int (quantity_sold) >= 0:
                    quantity_sold = int(quantity_sold)
                    if quantity_sold > product[3]:
                        print("INSUFFICIENT STOCK")
                        continue
                    break
                else:
                    print("ENTER VALID INPUT: ")

            total_cost = round(quantity_sold * product[2], 2)

            profit = total_cost - (product[5] * quantity_sold)

            new_quantity = product[3] - quantity_sold
            cur.execute("UPDATE stock SET Quantity = ? WHERE Product_ID = ?", (new_quantity, product_id))

            sale_date = datetime.date.today().strftime("%Y-%m-%d")

            cur.execute("INSERT INTO sales (Product_ID, Amount, Total, Date, Profit) VALUES (?, ?, ?, ?, ?)", (product_id, quantity_sold, total_cost, sale_date, profit))
            con.commit()

            print(f"SALE RECORDED: {quantity_sold} UNITS OF {product[1]} SOLD FOR {total_cost} ON {sale_date}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except ValueError:
        print("INVALID INPUT!")

def UpdateSales():
    #FUNCTION TO UPDATE THE DETAILS OF A SALE
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            ViewSales()

            sale_id = int(input("ENTER SALE ID YOU WISH TO UPDATE: "))
            cur.execute("SELECT * FROM sales WHERE Sale_ID = ?", (sale_id,))
            sale = cur.fetchone()

            if not sale:
                print("NO SALE FOUND MATCHING THIS ID")
                return

            cur.execute("SELECT Quantity, Cost, Supplier_Cost FROM stock WHERE Product_ID = ?", (sale[1],))
            stock = cur.fetchone()
            if not stock:
                print("NO STOCK FOR THIS PRODUCT")
                return

            current_stock, product_cost, supp_cost = stock

            new_amount = None
            while new_amount is None:
                try:
                    new_amount = int(input("ENTER THE NEW AMOUNT FOR THIS SALE: "))
                    if new_amount < 0:
                        print("AMOUNT CANNOT BE NEGATIVE")
                        new_amount = None
                except ValueError:
                    print("INVALID INPUT! PLEASE ENTER A NUMBER.")

            amount_difference = new_amount - sale[2]
            new_stock = current_stock - amount_difference

            if new_stock < 0:
                print("NOT ENOUGH STOCK AVAILABLE FOR THIS UPDATE")
                return

            new_total = round(new_amount * product_cost, 2)
            new_profit = round(new_total - (supp_cost * new_amount), 2)

            cur.execute("UPDATE sales SET Amount = ?, Total = ?, Profit = ? WHERE Sale_ID = ?", (new_amount, new_total, new_profit, sale_id))                          
            cur.execute("UPDATE stock SET Quantity = ? WHERE Product_ID = ?", (new_stock, sale[1]))
            con.commit()

            print("SALE DETAILS UPDATED")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")
        con.rollback()
    except ValueError:
        print("INVALID INPUT! ENSURE VALID INPUT IS GIVEN")
        con.rollback()


def ViewSales():
# View all sales made
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM sales")
            sales = cur.fetchall()
            if not sales:
                print("NO SALES RECORDED")
                return
            else:
                print("TRANSACTION HISTORY")
                for sale in sales:
                    print(f"SALE ID: {sale[0]} | PRODUCT ID: {sale[1]} | AMOUNT {sale[2]} | TOTAL: {sale[3]:.2f} | DATE: {sale[4]} | PROFIT: {sale[5]}")
    
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def AddSupplier():
# Function to add a new supplier to the database
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            supplier_name = input("ENTER SUPPLIER NAME: ").strip()
            email = input("ENTER EMAIL: ").strip()
            phone = input("ENTER PHONE NUMBER: ").strip()

            cur.execute("INSERT INTO supplier (Supplier_Name, Email, Phone) VALUES (?, ?, ?)", 
                        (supplier_name, email, phone))
            con.commit()
            print("SUPPLIER ADDED")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")

def ViewSuppliers():
# Function to view all the suppliers
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM supplier")
            suppliers = cur.fetchall()

            if not suppliers:
                print("NO SUPPLIERS FOUND")
                return
            
            for supplier in suppliers:
                print(f"SUPPLIER ID: {supplier[0]} | NAME: {supplier[1]} | EMAIL: {supplier[2]} | PHONE: {supplier[3]}")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def SaleProfits():
# Funciton to view all the profits made on individual sales
    try:
        with Connect_To_Database() as con:
            cur = con.cursor()
            cur.execute("SELECT Sale_ID, Profit FROM sales")
            sale_profits = cur.fetchall()

            if not sale_profits:
                print("NO SALES MADE")
                return
            
            for profit in sale_profits:
                print(f"SALE ID: {profit[0]} | PROFIT: {profit[1]}")
    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def MonthlyReport():
# Function to calculate the revenue and profit for each month
    os.system('cls')
    try:
        with Connect_To_Database() as con:

            cur = con.execute("""SELECT strftime('%Y-%m', Date) as Month, SUM(Total) as TotalRevenue, SUM(PROFIT) as TotalProfit, (SUM(Total) - SUM(Profit)) as TotalCost FROM sales GROUP BY Month""")
            monthly_reports = cur.fetchall()

            if not monthly_reports:
                print("NO DATA AT THE MOMENT")
            else:
                for month, revenue, profit, cost in monthly_reports:
                    print(f"MONTH: {month} | REVENUE: {revenue} | COSTS: {cost} | PROFIT: {profit}")

    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")


def AdminMenu():
# Main menu for the admin users, prompts for an input and then redirects them to their desired destination
    os.system('cls')
    print("------ADMIN MENU------")
    print("1) USER MANAGEMENT\n2) STOCK MANAGEMENT\n3) SALES AND TRANSACTIONS\n4) SUPPLIER MANAGEMENT\n5) REPORTS\n6) LOGOUT")
    choice = input("SELECT OPTION: ").strip()
    while choice not in ["1", "2", "3", "4", "5", "6"]:
        choice = input("ERROR! INVALID OPTION, TRY AGAIN: ").strip()
    if choice == "1":
        UserManagement()
    elif choice == "2":
        StockManagement()
    elif choice == "3":
        SalesAndTransactions()
    elif choice == "4":
        SupplierMenu()
    elif choice == "5":
        ReportMenu()
    elif choice == "6":
        Startup()

def menu():
# Main Menu for the non-admin users
    os.system('cls')
    print("-------MAIN MENU-------")
    print("1) STOCK MANAGEMENT\n2) SALES AND TRANSACTIONS\n3) SUPPLIER MANAGEMENT\n4) LOGOUT")
    choice = input("SELECT OPTION: ").strip()
    while choice not in ["1", "2", "3", "4"]:
        choice = input("INVALID OPTION! TRY AGAIN: ")
    if choice == "1":
        StockManagement()
    elif choice == "2":
        SalesAndTransactions()
    elif choice == "3":
        SupplierMenu()
    elif choice == "4":
        Startup()


def SupplierMenu():
# Menu for supplier management
    print("------SUPPLIER MANAGEMENT------")
    print("1) ADD SUPPLIER\n2) VIEW SUPPLIERS\n3) RETURN TO MAIN MENU")
    choice = input("SELECT OPTION: ").strip()
    while choice not in ["1", "2", "3"]:
        choice = input("INVALID OPTION! TRY AGAIN:")
    if choice == "1":
        os.system('cls')
        AddSupplier()
    elif choice == "2":
        os.system('cls')
        ViewSuppliers()
    elif choice == "3":
        ReturnToMenu()
    ReturnToMenu()

def ReportMenu():
# Menu for reports
    os.system('cls')
    print("------REPORTS------")
    print("1) SALE PROFITS\n2) MONTHLY PROFITS\n3) RETURN TO MAIN MENU")
    choice = input("SELECT OPTION: ").strip()
    while choice not in ["1", "2", "3"]:
        choice = input("INVALID OPTION! TRY AGAIN:")
    if choice == "1":
        os.system('cls')
        SaleProfits()
    elif choice == "2":
        os.system('cls')
        MonthlyReport()
    elif choice == "3":
        ReturnToMenu()
    ReturnToMenu()

def UserManagement():
# Menu for user management
    os.system('cls')
    print("------USER MANAGEMENT MENU ------")
    print("1) CREATE USERS\n2) VIEW USERS\n3) RESET PASSWORD\n4) DELETE USER\n5) RETURN TO MAIN MENU")
    choice = input("SELECT OPTION: ")
    while choice not in ["1", "2", "3", "4", "5"]:
        choice = input("INVALID OPTION! TRY AGAIN: ")
    if choice == "1":
        os.system('cls')
        CreateUsers()
    elif choice == "2":
        os.system('cls')
        ViewUsers()
    elif choice == "3":
        os.system('cls')
        ResetPassword()
    elif choice == "4":
        os.system('cls')
        DeleteNonAdmin()
    elif choice == "5":
        ReturnToMenu()
    ReturnToMenu()

def StockManagement():
# Menu for stock management
    os.system('cls')
    print("------STOCK MANAGEMENT------")
    print("1) ADD PRODUCT\n2) VIEW STOCK\n3) UPDATE STOCK\n4) REMOVE STOCK\n5) REORDER CHER\n6) RETURN TO MAIN MENU")
    choice = input("SELECT OPTION: ")
    while choice not in ["1","2","3","4","5","6"]:
        choice = input("INVALID OPTION! TRY AGAIN: ")
    if choice == "1":
        os.system('cls')
        AddProduct()
    elif choice == "2":
        os.system('cls')
        ViewStock()
    elif choice == "3":
        os.system('cls')
        UpdateStock()
    elif choice == "4":
        os.system('cls')
        DeleteProduct()
    elif choice == "5":
        os.system('cls')
        Reorder_Check()
    elif choice == "6":
        ReturnToMenu()
    ReturnToMenu()

def SalesAndTransactions():
# Menu for sales
    os.system('cls')
    print("------SALES------")
    print("1) CREATE SALE\n2) VIEW SALES\n3) UPDATE SALES\n4) RETURN TO MAIN MENU")
    choice = input("SELECT OPTION: ")
    while choice not in ["1","2","3", "4"]:
        choice = input("INVALID OPTION! TRY AGAIN: ")
    if choice == "1":
        os.system('cls')
        CreateSale()
    elif choice == "2":
        os.system('cls')
        ViewSales()
    elif choice == "3":
        os.system('cls')
        UpdateSales()
    elif choice == "4":
        ReturnToMenu()
    ReturnToMenu()

def Login():
# Function to log into the system
# If no users exist, goes to the create users function
# Saves the users role to the global variable CurrentUserRole
    global CurrentUserRole
    with Connect_To_Database() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT (*) FROM users")
        UserCount = cur.fetchone()[0]
        if UserCount == 0:
            print("NO USER'S FOUND, CREATE USER:")
            CreateUsers()

    while True:
        username = input("ENTER USERNAME: ").strip().lower()
        if username == "exit":
            print("CLOSING SYSTEM")
            return None

        PassCheck = maskpass.advpass(prompt="ENTER PASSWORD: ").strip().encode('utf-8')
        
        try:
            with Connect_To_Database() as con:
                cur = con.cursor()
                cur.execute("SELECT password, role FROM users WHERE username = ?", (username,))
                result = cur.fetchone()

                if result and bcrypt.checkpw(PassCheck, result[0].encode('utf-8')):
                    print(f"LOGIN COMPLETE. <{result[1].upper()}> ROLE")
                    CurrentUserRole = result[1].lower()
                    return result[1].lower()
                else:
                    print("LOGIN FAILED, INCORRECT USERNAME AND/OR PASSWORD. TRY AGAIN")

        except sqlite3.Error as e:
            print(f"DATABASE ERROR: {e}")
        
        
def Startup():
# Function to start up the program
    os.system('cls')
    CreateTables()
    Login()
    if CurrentUserRole == "admin": # If the user is an admin, takes them to the admin menu, if not, the normal menu
        AdminMenu()
    else:
        menu()

# Calls the startup function
Startup()