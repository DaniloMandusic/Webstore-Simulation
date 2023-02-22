import csv
import io

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, jwt_required
import json
from configuration import Configuration
from models import database
from RoleCheckDecorator import roleCheck
from redis import Redis

application = Flask(__name__)
application.config.from_object(Configuration)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
jwt = JWTManager ( application )
database.init_app(application)

@application.route("/update", methods=["POST"])
@roleCheck(role="storageworker")
#@roleCheck(role="user")
#@jwt_required(refresh=False)
def update():
    file = request.files.get("file", None)

    if not file:
        return jsonify(message="Field file is missing."), 400

    reader = csv.reader(io.StringIO(file.stream.read().decode("utf-8")))

    count = 0
    products = []

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

    for row in reader:
        #print(str(row))
        if len(row) != 4:
            return jsonify(message=f"Incorrect number of values on line {count}."), 400
        if(not isInt(row[2])):
            return jsonify(message=f"Incorrect quantity on line {count}."), 400
        if(not isFloat(row[3])):
            return jsonify(message=f"Incorrect price on line {count}."), 400
        if(isInt(row[2])):
            if(int(row[2]) <= 0):
                return jsonify(message=f"Incorrect quantity on line {count}."), 400
        if (isFloat(row[3])):
            if (float(row[3]) <= 0):
                return jsonify(message=f"Incorrect price on line {count}."), 400

        product = {
            "categories": row[0],
            "name": row[1],
            "quantity": int(row[2]),
            "price": float(row[3])
        }
        products.append(product)

        count += 1

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for product in products:
            redis.rpush(Configuration.REDIS_PRODUCT_LIST, json.dumps(product))

            bytes = redis.lrange(Configuration.REDIS_PRODUCT_LIST, 0, -1)
            for b in bytes:
                product = b.decode("utf-8")
                print(product)

    #print(products)

    return Response(status=200)

if ( __name__ == "__main__" ):
    application.run ( debug = True, host="0.0.0.0", port = 5004 )