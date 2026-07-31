#init created as just a function for ease of use

def init():
    
    import sqlite3 as sql

    con = sql.connect('./quickcast.db')

    c = con.cursor()

    #foreign_keys off right now to make table creation throw less errors

    query = '''
    PRAGMA foreign_keys = OFF;
    '''

    c.execute(query)

    #creation of the records table, which is the main table where most joins occur
    #comprises of mostly ids, which link to the tables around it. These ids are also foreign keys
    #created as strict as to prevent SQLites loose typing from throwing errors further down

    query = '''
    CREATE TABLE IF NOT EXISTS records(
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT

    ) STRICT;
    '''

    c.execute(query)

    #users table, is mainly used to be able to seperate users data according to the user, password field mostly unused

    query = '''
    CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT ""
    ) STRICT;
    '''

    c.execute(query)

    #customers table, to prevent similarly named people from screwing up queries, as queries use group by

    query = '''
    CREATE TABLE IF NOT EXISTS customers(
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL
    ) STRICT;
    '''

    c.execute(query)

    #employees table, similar purpose to customers table

    query = '''
    CREATE TABLE IF NOT EXISTS employees(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    retail_sales_people TEXT NOT NULL
    ) STRICT;
    '''

    c.execute(query)

    #locations table, purposefully not fully normalized to reduce join complexity
    #importantly, state and postal code are not required fields, so that other countries can be represented

    query = '''
    CREATE TABLE IF NOT EXISTS locations(
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    state TEXT,
    city TEXT NOT NULL,
    postal_code TEXT
    ) STRICT;
    '''

    c.execute(query)

    #products table, also not fully normalized, category and subcategory are not required fields as they 
    #currently are unused fields for QuickCast 

    query = '''
    CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT
    ) STRICT;
    '''

    c.execute(query)

    #orders table, has a very interesting combination of order_id, product_id, and row_id
    #as the orders table has a one to many relationship with both records and products
    #as a product can be in many orders, and a order can have many products
    #profit is a not required field, as sales can be used as a metric similar to it
    #returned is not required because it is a currently unused field
    #references both the products and records table

    query = '''
    CREATE TABLE IF NOT EXISTS orders(
    order_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    row_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 1,
    sales INTEGER NOT NULL,
    discount INTEGER NOT NULL DEFAULT 0,
    profit INTEGER,
    returned INTEGER CHECK (returned IN (0, 1)),

    FOREIGN KEY (order_id) REFERENCES records(order_id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT

    ) STRICT;
    '''

    c.execute(query)

    query = '''
    PRAGMA foreign_keys = ON;
    '''

    c.execute(query)

    con.commit()
    con.close()