from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy ( )

class ProductCategory(database.Model):
    __tablename__ = "productCategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.productId, self.categoryId)


class ProductOrder(database.Model):
    __tablename__ = "productOrder"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    price = database.Column(database.Float, nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    received = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.productId, self.orderId)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=ProductOrder.__table__, back_populates="products")

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.id, self.name, self.price, self.quantity)


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return "({}, {})".format(self.id, self.name)


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    customer = database.Column(database.String(256), nullable=False)
    status = database.Column(database.String(256), nullable=False) # PENDING, DELI|VERED
    timestamp = database.Column(database.DateTime, nullable=False)

    products = database.relationship("Product", secondary=ProductOrder.__table__, back_populates="orders")

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.id, self.price, self.status, self.timestamp)

