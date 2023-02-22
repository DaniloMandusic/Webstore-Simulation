import shutil
import time

from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, Role, UserRole, User;
from sqlalchemy_utils import database_exists, create_database;

application = Flask ( __name__ );
application.config.from_object ( Configuration );

migrateObject = Migrate ( application, database );

if ( not database_exists ( application.config["SQLALCHEMY_DATABASE_URI"] ) ):
    create_database ( application.config["SQLALCHEMY_DATABASE_URI"] );

database.init_app ( application );

with application.app_context ( ) as context:

    try:
        shutil.rmtree('migrations')
    except Exception:
        pass

    init ( );
    migrate ( message = "Production migration" );
    upgrade ( );

    adminRole = Role ( name = "admin" );
    buyerRole = Role ( name = "buyer" );
    storageWorkerRole = Role(name="storageworker");
    #userRole = Role(name="user");

    database.session.add ( adminRole );
    database.session.add ( buyerRole );
    database.session.add ( storageWorkerRole );
    #database.session.add ( userRole );
    database.session.commit()

    admin = User (
            email = "admin@admin.com",
            password = "1",
            forename = "admin",
            surname = "admin",
            isCustomer=False
            #roles="admin"
    )
    #
    database.session.add ( admin )
    database.session.commit ( );

    userRole = UserRole (
            userId = admin.id,
            roleId = adminRole.id
    );

    database.session.add(userRole)
    database.session.commit()

    #time.sleep(1000)