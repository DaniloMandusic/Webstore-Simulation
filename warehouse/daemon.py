import time
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
import json
from sqlalchemy import and_
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, ProductOrder
#from RoleCheckDecorator import roleCheck
from redis import Redis


'''
    treba da se ubaci u petlju i lpop i da se doda nesto sa narudzbinama
'''


#da li je u bazi proiz sa istim imenom
    #ne
        #dodaj u bazu, zajedno sa svim kategorijama
    #da
        #uporedi kategorije, ako nisu iste odbaci
        #ako jesu iste azuriraj kolicinu i cenu

#while True:
    #approve()
application = Flask(__name__)
print("usao0")
application.config.from_object(Configuration)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
jwt = JWTManager ( application )
database.init_app(application)

print("usao")

while True:
    print("usao1")
    with Redis(host=Configuration.REDIS_HOST) as redis:
    #with Redis(host=Configuration.REDIS_URL) as redis:
    #with Redis(host = "myRedis", port=6379) as redis:
        with application.app_context():

            orders = Order.query.filter(Order.status == "PENDING").all()

            bytes = redis.blpop(Configuration.REDIS_PRODUCT_LIST)

            if(not bytes):
                continue

            productString = bytes[1]#.decode("utf-8")
            product = json.loads(productString)
            categories = product["categories"].split("|")

            #print(product)

            productInDatabase = Product.query.filter(Product.name == product["name"]).first()

            if(not productInDatabase):
               # print("ne postoji")
                newProduct = Product(name=product["name"], quantity=product["quantity"], price=product["price"])
                database.session.add(newProduct)
                database.session.commit()

                for category in categories:
                    categoryInDatabase = Category.query.filter(Category.name == category).first()

                    if(not categoryInDatabase):
                        newCategory = Category(name=category)
                        database.session.add(newCategory)
                        database.session.commit()
                        pc = ProductCategory(productId=newProduct.id, categoryId=newCategory.id)
                    else:
                        pc = ProductCategory(productId=newProduct.id, categoryId=categoryInDatabase.id)

                    database.session.add(pc)
                    database.session.commit()
            else:
               # print("vec postoji")

                categoriesInDatabase = productInDatabase.categories

                tmpCategories = []
                for categoryInDatabase in categoriesInDatabase:
                    tmpCategories.append(categoryInDatabase.name)

                if(len(categories) == len(tmpCategories)):
                    categories.sort()
                    tmpCategories.sort()

                    count = 0
                    for i in range(0,len(categories)):
                        if(categories[i] == tmpCategories[i]):
                            count+=1

                    if(count == len(categories)):
                       # print("poklapa se")


                        newPrice = (productInDatabase.quantity * productInDatabase.price + product["price"] * product["quantity"])/float(productInDatabase.quantity + product["quantity"])
                        productInDatabase.price = newPrice
                        productInDatabase.quantity += product["quantity"]


                        # nova cena je postavljena, kolicina je azurirana
                        # pokupi sve pending narudzbine
                            # za svaku narudzbinu pokupi proizvode
                            # ako se proizvod iz narudzbine poklapa sa proizvodom iz baze
                                # oduzmi iz baze i pusti u narudzbinu

                            # prodji opet kroz pending narudzbine i proveri jel su skroz popunjene


                       # print(orders)

                        for order in orders:
                            orderProducts = ProductOrder.query.filter(
                                and_(
                                    ProductOrder.orderId == order.id,
                                    ProductOrder.productId == productInDatabase.id
                                )
                            ).all()

                            if(productInDatabase.quantity == 0):
                                break


                            for op in orderProducts:
                                requestedQuantity = op.requested
                                receivedQuantity = op.received
                                availableQuantity = productInDatabase.quantity
                                remainingQuantity = requestedQuantity - receivedQuantity

                                if(availableQuantity >= remainingQuantity):
                                    op.received += remainingQuantity
                                    productInDatabase.quantity -= remainingQuantity
                                else:
                                    op.received += availableQuantity
                                    productInDatabase.quantity = 0

                        for order in orders:
                            orderProducts = ProductOrder.query.filter(
                                and_(
                                    ProductOrder.orderId == order.id#,

                                )
                            ).all()

                            allProductsCount = len(orderProducts)
                            if(allProductsCount > 0):
                                count = 0
                                for op in orderProducts:
                                    requestedQuantity = op.requested
                                    receivedQuantity = op.received

                                    if(requestedQuantity == receivedQuantity):
                                        count += 1

                                if(allProductsCount == count):
                                    order.status = "COMPLETE"

                        database.session.commit()

                    else:
                        #print("ne poklapa se")
                        continue

                else:
                    #print("ne poklapa se")
                    continue

            #time.sleep(10)
            #print("odspavao")












