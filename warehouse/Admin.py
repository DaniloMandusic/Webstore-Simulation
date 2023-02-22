import csv
import io
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, get_jwt
from sqlalchemy import and_

from configuration import Configuration
from models import database, Category, ProductCategory, Product, ProductOrder, Order
from RoleCheckDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
jwt = JWTManager(application)
database.init_app(application)

@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="admin")
def productStatistics():
    #za svaki product vrati ime koliko je prodato i koliko ceka
    # prodato je u svim orderima received zbir
    # ceka je u svim orderima requested - received zbir

    #query all products
        #nadji productOrder iz daemona
        #za svaki productOrder:
            #nadji order
            #dodaj potrebne vrednosti

    productStatistics = []
    products = Product.query.all()

    for product in products:
        orderProducts = ProductOrder.query.filter(
            and_(
                ProductOrder.productId == product.id  # ,
                # ProductOrder.productId == productInDatabase.id
            )
        ).all()

        sold = 0
        waiting = 0
        for order in orderProducts:
            #order = Order.query.filter(Order.id == o.orderId).all()
            sold += order.received
            waiting += (order.requested - order.received)

        productStatistics.append({
            "name": product.name,
            "sold": sold,
            "waiting": waiting
        })

    return jsonify(statistics = productStatistics), 200

@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="admin")
def categoryStatistics():
    #opadajuce sortiran niz kategorija (vrednost je po broju prodatih proizvoda)
    #pronadji broj proizvoda prodatih po kategoriji

    #for all categories
        #for all productCategory
            #for all productOrder
                #saberi received

    categories = Category.query.all()

    categorySold = []
    for category in categories:
        categoryProducts = ProductCategory.query.filter(
            and_(
                ProductCategory.categoryId == category.id  # ,
                # ProductOrder.productId == productInDatabase.id
            )
        ).all()

        sold = 0

        for product in categoryProducts:
            orderProducts = ProductOrder.query.filter(
                and_(
                    ProductOrder.productId == product.productId  # ,
                    # ProductOrder.productId == productInDatabase.id
                )
            ).all()

            for order in orderProducts:
                sold += order.received

        categorySold.append([category.name, sold])

    #print(categorySold)

    categorySold = sorted(categorySold, key=lambda x: x[1], reverse=True)

    categoryStatistics = []

    for category in categorySold:
        categoryStatistics.append(category[0])


    return jsonify(statistics = categoryStatistics), 200

if (__name__ == "__main__"):
    application.run(debug=True, host="0.0.0.0" ,port=5005)