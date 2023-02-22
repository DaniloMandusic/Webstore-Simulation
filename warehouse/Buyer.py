import csv
import io
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from sqlalchemy import and_

from configuration import Configuration
from models import database, Category, ProductCategory, Product, ProductOrder, Order
from RoleCheckDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
jwt = JWTManager ( application )
database.init_app(application)

@application.route("/search", methods=["GET"])
@roleCheck(role="buyer")
#@jwt_required(refresh=False)
def search():
    product = request.args.get("name", "")
    category = request.args.get("category", "")

    productEmpty = product == ""
    categoryEmpty = category == ""

    #if(not productEmpty and not categoryEmpty):
        #sve kategorije koje su kao category i imaju makar 1 proizvod sa name
    categories = Category.query.join(ProductCategory).join(Product).filter(
        and_(*[
            Product.name.like(f"%{product}%"),
            Category.name.like(f"%{category}%")
        ]
             )
    ).group_by(Category.name).with_entities(Category.name).all()

    categoryArray = []
    for c in categories:
        categoryArray.append(c.name)

    products = Product.query.join(ProductCategory).join(Category).with_entities(Product.id,Product.name,Product.quantity,Product.price).filter(
        and_(
            *[
                Product.name.like(f"%{product}%"),
                Category.name.like(f"%{category}%")
            ]
        )
    ).group_by(Product.id).all()

    productArray = []
    for product in products:

        productCategories = []

        cats = ProductCategory.query.join(Category).with_entities(Category.name).filter(
            ProductCategory.productId == product[0]
        ).all()

        for c in cats:
            productCategories.append(c[0])

        productDict = {
            "categories": productCategories,
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        }
        productArray.append(productDict)

    productArray.sort(key=lambda x: x["id"])

    #print(products)
    return jsonify(categories=categoryArray, products=productArray),200

    #return Response(status=200)

@application.route("/order", methods=["POST"])
@roleCheck(role="buyer")
#@jwt_required(refresh=False)
def order():
    requests = request.json.get("requests", None)
    if not requests:
        return jsonify(message="Field requests is missing."), 400

    def isFloat(str):
        try:
            float(str)
            result = True
        except:

            result = False

        return result

    def isInt(str):
        try:
            int(str)
            result = True
        except:

            result = False
        return result

    count = 0
    for r in requests:
        id = r.get("id", "")
        idEmpty = id == ""
        if (idEmpty):
            return jsonify(message=f"Product id is missing for request number {count}."), 400

        quantity = r.get("quantity", "")
        quantityEmpty = quantity == ""
        if (quantityEmpty):
            return jsonify(message=f"Product quantity is missing for request number {count}."), 400
        #if not isInt(id) or (isInt(id) < 0):
        if(not isInt(id)):
        #if(id< 0 or not isinstance(id, int)):
            return jsonify(message=f"Invalid product id for request number {count}."), 400
        if(id < 0):
            return jsonify(message=f"Invalid product id for request number {count}."), 400
        #if not isInt(quantity):
        if(not isInt(quantity)):
        #if (quantity < 0 or not isinstance(quantity, int)):
            return jsonify(message=f"Invalid product quantity for request number {count}."), 400
        if (quantity < 0):
            return jsonify(message=f"Invalid product quantity for request number {count}."), 400

        product = Product.query.filter(Product.id == id).first()
        if (not product):
            return jsonify(message=f"Invalid product for request number {count}."), 400

        #if(price)

        count += 1

    quantities = []
    products = []
    prices = []
    totalPrice = 0
    for r in requests:
        id = r.get("id", "")
        product = Product.query.filter(Product.id == id).first()
        products.append(product.id)

        quantity = r.get("quantity", "")
        quantities.append(quantity)

        price = product.price
        prices.append(product.price)
        totalPrice += price*quantity

    claims = get_jwt()
    email = claims["sub"]

    newOrder = Order(price=totalPrice, customer=email, status="TBD", timestamp=datetime.today())
    database.session.add(newOrder)
    database.session.commit()

    pending = False

    for i in range(0, len(products)):
        productId = products[i]
        quantity = quantities[i]
        price = prices[i]
        
        product = Product.query.filter(Product.id == productId).first()
        product_order = ProductOrder(productId=product.id, orderId=newOrder.id, requested=quantity, price=price)

        if product.quantity >= quantity:
            product.quantity -= quantity
            delivered = quantity
        else:
            delivered = product.quantity
            product.quantity = 0
            pending = True
        product_order.received = delivered
        database.session.add(product_order)

    if pending:
        newOrder.status = "PENDING"
    else:
        newOrder.status = "COMPLETE"

    database.session.commit()

    return jsonify(id=newOrder.id), 200

@application.route("/status", methods=["GET"])
@roleCheck(role="buyer")
#@jwt_required(refresh=False)
def status():
    claims = get_jwt()
    email = claims["sub"]

    orders = Order.query.filter(Order.customer == email).all()

    ordersStatus = []
    for order in orders:
        orderedProducts = ProductOrder.query.filter(ProductOrder.orderId == order.id).all()

        products = []
        for p in orderedProducts:
            product = Product.query.filter(Product.id == p.productId).first()
            productCategoriesIndexes = ProductCategory.query.filter(ProductCategory.productId == product.id).all()

            categories = []
            for c in productCategoriesIndexes:
                category = Category.query.filter(Category.id == c.categoryId).first()
                categories.append(category.name)

            products.append({
                "categories": categories,
                "name": product.name,
                "price": p.price,
                "received": p.received,
                "requested": p.requested
            })

        #print(products)

        ordersStatus.append({
            "products": products,
            "price": order.price,
            "status": order.status,
            "timestamp": order.timestamp
        })

    return jsonify(orders=ordersStatus), 200


if ( __name__ == "__main__" ):
    application.run ( debug = True, host="0.0.0.0" , port = 5003 )