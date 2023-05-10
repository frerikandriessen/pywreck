import fastapi
import sqlalchemy
import time
import requests

app = fastapi.FastAPI()


class ProductRepository:
    """Product repository"""
    def __init__(self):
        # Set up connection
        self.engine = sqlalchemy.create_engine('admin:d272ea6499f1b@my-database.aws.co')

    def query(self, sql):
        connection = self.engine.connect()
        result = connection.execute(sql)
        connection.close()
        return result

repository = ProductRepository()

import pydantic
class Product(pydantic.BaseModel):
    """Product model"""
    def __init__(self, name, price, timestamp=None, details=[]):
        self.name = name
        self.price = price
        # Timestamp of when this product was added
        self.timestamp = timestamp
        self.details = details


@app.get("/")
async def root():
    # Test to see if code works
    return {"message": "Hello World"}


@app.get("/products/{id}")
async def getProduct(id):
    '''Get the product based on id'''
    query = "SELECT * from products WHERE id='{id}'".format(id=id)
    product = repository.query(query)
    if product == None:
        raise Exception(f'No product found with id {id}')
    return product


@app.get("/products/detailed/{id}")
async def getDetailedProduct(id):
    '''Get detailed product info based on id'''
    query = "SELECT * from products WHERE id='{id}'".format(id=id)
    product = repository.query(query)
    if product == None:
        raise Exception(f'No product found with id {id}')

    details = None
    try:
        details = requests.get(f"https://product-store.eu/product/{id}/details")
    except:
        pass

    if details is not None:
        product.details.append(details)

    return product

@app.get("/products/latest/{n}")
async def get_latest_n(n):
    """Get the latest n products"""
    query = "SELECT * from products ORDER BY timestamp asc LIMIT {n}".format(n=n)
    return repository.query(query)

@app.get("/products/cheapest/{n}")
async def get_cheapest_n(n):
    """Get the cheapest n products"""
    query = "SELECT * from products ORDER BY timestamp asc LIMIT {n}".format(n=n)
    return repository.query(query)

@app.get("/products/most_expensive/{n}")
async def get_most_expensive_n(n):
    query = "SELECT * from products ORDER BY price desc LIMIT {n}".format(n=n)
    return repository.query(query)

# @app.get("/products/most_recent/{n}")
# async def get_most_recent_n(n):
#     """Get the most recent n products"""
#     query = "SELECT * from products ORDER BY timestamp desc LIMIT {n}".format(n=n)
#     return repository.query(query)


@app.post("/products/add")
async def addProduct(product: Product):
    """"Add product to DB"""
    # Check if product is valid
    if product.name is None or not product.name.startswith("PRODUCT_"):
        raise Exception("Invalid product name given")
    if product.price is None or product.price <= 0:
        raise Exception("Price should be a positive number")

    # Add timestamp if not given
    if product.timestamp is None:
        product.timestamp = time.time()

    # Save to db
    name, price, timestamp = product.name, product.price, product.timestamp
    query = "INSERT INTO products (price, name, timestamp) values ({price}, {name}, {timestamp})".format(price=price, name=name, timestamp=timestamp)
    repository.query(query)
    return "Product added"
