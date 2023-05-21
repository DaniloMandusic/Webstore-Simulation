# Webstore-Simulation
Amazon like webstore made in flask and set up to run in docker containers with docker compose for "Infrastructure for e-business" school project.
<br>
<br>
Project contains 2 databases (user authentication and warehouse database), API requests and Redis thread for data handling and Docker compose files for automated start of application, necessary services and database migrations.
<br>

<b>List of requests:</b>
<br>
/login - login existing user
<br>
/register - make new user
<br>
/refresh - refresh java web token
<br>
/delete - delete user (admin only)
<br>
/update - update product and categories quantity
<br>
/search?name=<PRODUCT_NAME>&category=<CATEGORY_NAME> - filter search products and categories
<br>
/order - make new order
<br>
/status - return status of users orders (delivered and requested quantities and prices)
<br>
/productStatistics - statistics of sold products
<br>
/categoryStatistics - statistics of categories of products that are sold

