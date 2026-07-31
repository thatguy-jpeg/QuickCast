#File consists of query functions controlled by app.py, augmented by the different buttons selected 

#setup creates a temporary user_records table, which is just the records table filtered by user_id
#prevents a user from accessing another user's records

def setup(cur, user_id):
    
    query = '''
    DROP TABLE IF EXISTS user_records;
    '''

    cur.execute(query)
    
    subquery = f'''
    SELECT * 
    FROM records
    WHERE user_id = {user_id};
    '''

    query = f'''
    CREATE TEMP TABLE user_records AS
    {subquery}
    '''

    cur.execute(query)

#links to the customer_query button on the frontend
#takes arguments of the cursor, whether they want the name or id, the limit, the wanted order, aggregation type, and whether or note sales or profit is wanted
#is intended to be a modular query which can adjust to the different settings the user selects

def customer_query(cur, name=True, limit=10, order="DESC", agg="COUNT", sale_profit=False):
    if name:
        col = "customer_name"
    else:
        col = "customer_id"

    if sale_profit != False:
        query = f'''
        SELECT {col}, {agg}({sale_profit})
        FROM user_records
        LEFT JOIN customers
        USING (customer_id)
        LEFT JOIN orders
        USING (order_id)
        GROUP BY customer_id
        ORDER BY {agg}({sale_profit}) {order}
        LIMIT {limit};
        '''
    else:
        query = f'''
        SELECT {col}, {agg}(record_id)
        FROM user_records
        LEFT JOIN customers
        USING (customer_id)
        GROUP BY customer_id
        ORDER BY {agg}(record_id) {order}
        LIMIT {limit};
        '''

    cur.execute(query)

    return cur.fetchall()

#links to the product_query button on the frontend
#takes arguments of the cursor, whether they want the name or id, the limit, the wanted order, aggregation type, and whether or note sales or profit is wanted
#is intended to be a modular query which can adjust to the different settings the user selects
#very similar in style as the customer_query function

def product_query(cur, name=True, limit=10, order="DESC", agg="COUNT", sale_profit=False):
    if name:
        col = "product_name"
    else:
        col = "product_id"

    if sale_profit != False:
        query = f'''
        SELECT {col}, {agg}({sale_profit})
        FROM user_records
        LEFT JOIN orders
        USING (order_id)
        LEFT JOIN products
        USING (product_id)
        GROUP BY product_id
        ORDER BY {agg}({sale_profit}) {order}
        LIMIT {limit};
        '''
    else:
        query = f'''
        SELECT {col}, {agg}(record_id)
        FROM user_records
        LEFT JOIN orders
        USING (order_id)
        LEFT JOIN products
        USING (product_id)
        GROUP BY product_id
        ORDER BY {agg}(record_id) {order}
        LIMIT {limit};
        '''

    cur.execute(query)
    return cur.fetchall()

#links to the location_query button on the frontend
#takes the SQLite cursor, limit amount, wanted order, type of aggregation, and the level (city, country, state)
#only finds the count for the level of orders 

def location_query(cur, limit=10, order="DESC", agg="COUNT", level="city"):
    query = f'''
    SELECT {level}, {agg}(DISTINCT order_id)
    FROM user_records
    LEFT JOIN locations
    USING (location_id)
    GROUP BY {level}
    ORDER BY {agg}(DISTINCT order_id) {order}
    LIMIT {limit};
    '''

    cur.execute(query)
    return cur.fetchall()


#links to the employee_query on the frontend
#takes the SQLite cursor, limit amount, wanted order, type of aggregation, and if the sales or profit is wanted

def employee_query(cur, name=True, limit=10, order="DESC", agg="COUNT", sales_profit=False):
    if name:
        col = "retail_sales_people"
    else: 
        col = "employee_id"
    
    if sales_profit != False:
        query = f'''
        SELECT {col}, {agg}({sales_profit})
        FROM user_records
        LEFT JOIN employees
        USING (employee_id)
        LEFT JOIN orders
        USING (order_id)
        GROUP BY employee_id
        ORDER BY {agg}({sales_profit}) {order}
        LIMIT {limit};
        '''
    else:
        query = f'''
        SELECT {col}, {agg}(record_id)
        FROM user_records
        LEFT JOIN employees
        USING (employee_id)
        GROUP BY employee_id
        ORDER BY {agg}(record_id) {order}
        LIMIT {limit};
        '''
    
    cur.execute(query)
    return cur.fetchall()

#links to the forecast button on the frontend
#takes the SQLite cursor, the product name chosen, and if the product name is wanted
#takes all the quantities month by month to make for a graph visualization

def forecast(cur, name_chosen, product_name=True):
    if product_name:
        col = "product_name"
    else:
        col = "product_id"

    query = f'''
    SELECT strftime('%Y-%m', order_date) AS month, SUM(quantity)
    FROM user_records
    LEFT JOIN orders
    USING (order_id)
    LEFT JOIN products
    USING (product_id)
    WHERE {col} = ?
    GROUP BY month
    ORDER BY month;
    '''

    cur.execute(query, (name_chosen,))
    return cur.fetchall()

#takes the SQLite cursor, row_id, quantity, sales, discount, profit, and returned as arguments
#simply updates the row_id with the given values
#does pose security risk due to no authentication

def update(cur, row_id, quantity, sales, discount, profit, returned):
    
    sales = round(sales * 100)
    profit = round(profit * 100)
    discount = round(discount * 100)

    query = f'''
    UPDATE orders SET 
    quantity=?, sales=?, discount=?, profit=?, returned=?
    WHERE row_id=?;
    '''

    cur.execute(query, (quantity, sales, discount, profit, returned, row_id))
    cur.connection.commit()

#takes the SQLite cursor and user_id as arguments
#deletes all of a user's data
def delete(cur, user_id):

    #deletes the orders in the orders table which have the user's records

    subquery = f'''
    SELECT order_id
    FROM records
    WHERE user_id=?
    '''
    query = f'''
    DELETE FROM orders
    WHERE order_id IN ({subquery});
    '''

    cur.execute(query, (user_id,))

    #deletes all the records from the records table which have the user's id

    query = f'''
    DELETE FROM records
    WHERE user_id=?;
    '''

    cur.execute(query, (user_id,))

    #deletes the user from users table

    query = f'''
    DELETE FROM users
    WHERE user_id=?
    '''

    cur.execute(query, (user_id,))

    cur.connection.commit()

