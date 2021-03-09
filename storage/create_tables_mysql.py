import mysql.connector


db_conn = mysql.connector.connect(host="acit3855-will.westus2.cloudapp.azure.com", user="root", password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE add_movie_orders
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           order_id VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           movie VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           movie_price FLOAT NOT NULL,
           movie_company VARCHAR(250) NOT NULL,
           CONSTRAINT add_movie_orders_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE payments
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           payment_id VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           movie_company VARCHAR(250) NOT NULL,
           movie VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT payments_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
