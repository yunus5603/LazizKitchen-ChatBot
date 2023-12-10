import mysql.connector

# Replace these values with your actual database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'laziz_kitchen'
}
conn = mysql.connector.connect(**db_config)

def insert_order_tracking(order_id , status):

    cursor = conn.cursor()
    
    query = "INSERT INTO laziz_kitchen.order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(query,(order_id,status))
    
    conn.commit()
    
    cursor.close()

def get_total_order_price(order_id):
    # conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = f"select get_total_order_price({order_id})"
    
    cursor.execute(query)
    
    result = cursor.fetchone()[0]
    
    cursor.close()
    
    return result

def insert_order_item(food_item,quantity,order_id):
    try:
        # conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.callproc('insert_order_item',(food_item,quantity,order_id))
        
        conn.commit()
        cursor.close()
        
        print("order item inserted successfully")
        
        return 1
    
    except mysql.connector.Error as err:
        print(f"Error inserting order item :{err}")
        
        # Rollback changes if necessary
        conn.rollback()
        
        return -1
    
    except Exception as e:
        print(f"an error has occured: {e}")
        
        conn.rollback()
        
        return -1

def get_next_order_id():
    
    # Connect to the MySQL server
    # conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the SQL query
    query = ("select max(order_id) from laziz_kitchen.orders")
    
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    # Print the result
    if result is None:
        return 1
    else:
        return result[0] + 1


def get_order_status (order_id):
 
    # Connect to the MySQL server
    # conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")
    
    cursor.execute(query,(order_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    # Print the result
    if result is not None:
        return result[0]
    else:
        return None
