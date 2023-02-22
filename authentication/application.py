import re
from functools import wraps

from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
from models import database, User, UserRole;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity, verify_jwt_in_request;
from sqlalchemy import and_;

application = Flask ( __name__ );
application.config.from_object ( Configuration );
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

@application.route ( "/register", methods = ["POST"] )
def register ( ):
    print("random")

    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );
    forename = request.json.get ( "forename", "" );
    surname = request.json.get ( "surname", "" );
    isCustomer = request.json.get("isCustomer", None);

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;
    forenameEmpty = len ( forename ) == 0;
    surnameEmpty = len ( surname ) == 0;

    message = ""

    if (forenameEmpty):
        message = "Field forename is missing."
        return jsonify({"message": message}), 400

    if (surnameEmpty):
        message = "Field surname is missing."
        return jsonify({"message": message}), 400

    if (emailEmpty):
        message = "Field email is missing."
        return jsonify({"message": message}), 400

    if (passwordEmpty):
        message = "Field password is missing."
        return jsonify({"message": message}), 400

    if(isCustomer is None):
        message = "Field isCustomer is missing."
        return jsonify({"message": message}), 400

    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if(not re.fullmatch(regex, email)):
        return jsonify({"message": "Invalid email."}), 400

    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')
    if (not re.fullmatch(regex, password)):
        return jsonify({"message": "Invalid password."}), 400

    user = User.query.filter(and_(User.email == email)).first()

    if (user):
        message = "Email already exists."
        return jsonify({"message": message}), 400

    user = User ( email = email, password = password, forename = forename, surname = surname, isCustomer=isCustomer);
    database.session.add ( user );
    database.session.commit ( );

    if (isCustomer):
        userRole = UserRole(userId=user.id, roleId=2)
    else:
        userRole = UserRole(userId=user.id, roleId=3)

    database.session.add(userRole);
    database.session.commit ( );

    return Response ( status = 200 );

jwt = JWTManager ( application );

@application.route ( "/login", methods = ["POST"] )
def login ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;

    if ( emailEmpty ):
        message = "Field email is missing."
        return jsonify({"message": message}), 400

    if ( passwordEmpty ):
        message = "Field password is missing."
        return jsonify({"message": message}), 400

    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if (not re.fullmatch(regex, email)):
        return jsonify({"message": "Invalid email."}), 400


    user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( );

    if ( not user ):
        message = "Invalid credentials."
        return jsonify({"message": message}), 400

    additionalClaims = {
            "forename": user.forename,
            "surname": user.surname,
            "roles": [ str ( role ) for role in user.roles ]
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    return jsonify ( accessToken = accessToken, refreshToken = refreshToken ), 200

@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );

    additionalClaims = {
            "forename": refreshClaims["forename"],
            "surname": refreshClaims["surname"],
            "roles": refreshClaims["roles"]
    }

    return jsonify(accessToken = create_access_token ( identity = identity, additional_claims = additionalClaims )), 200

def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if("roles" in claims and role in claims["roles"]):
                return function(*arguments, **keywordArguments)
            else:
                #return jsonify({"msg": "Missing Authorization Header"}), 401
                return jsonify(msg="Missing Authorization Header"), 401
        return decorator
    return innerRole

@application.route ( "/delete", methods = ["POST"] )
@roleCheck(role="admin")
#@jwt_required ( refresh = False )
def delete ( ):
    claims = get_jwt()
    roles = claims['roles']
    if (not "admin" in roles):
        return jsonify(msg="Missing Authorization Header"), 401

    if("storageworker" in roles or "buyer" in roles):
        return jsonify(msg="Missing Authorization Header"), 401

    email = request.json.get("email", "");

    emailEmpty = len(email) == 0;

    if ( emailEmpty ):
        message = "Field email is missing."
        return jsonify({"message": message}), 400

    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if (not re.fullmatch(regex, email)):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(User.email == email).first()

    if (not user):
        return jsonify({"message": "Unknown user."}), 400

    database.session.delete(user)
    database.session.commit()

    return Response(status=200)

@application.route ( "/", methods = ["GET"] )
def index ( ):
    return "Hello world!";

database.init_app(application);

if ( __name__ == "__main__" ):

    application.run ( debug = True, host = "0.0.0.0", port = 5002 )