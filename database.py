import pymysql

#Open database

conn = pymysql.connect(user='root',
            passwd='GTG24DDa',
            host='localhost',
            db='flaskshop')
conn = conn.cursor()
#Create table
conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT
		)''')

conn.execute('''CREATE TABLE categories
                (categoryId INTEGER PRIMARY KEY,
                name TEXT
                )''')
#conn.execute('''INSERT INTO categories (name) VALUES ('a category')''')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')
#conn.execute('''INSERT INTO products (name,price,description,image,stock,categoryId) VALUES ('thing',0,'desc','img',5,1)''')

conn.execute('''CREATE TABLE kart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')




conn.close()

