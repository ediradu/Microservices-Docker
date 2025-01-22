# Microservices-Docker

As technologies, I used Flask, PostgreSQL for the database, Docker, and pgAdmin for database management.

To start the application, use: docker-compose up --build.

If any port is already in use, you can free it using the commands:
  * sudo lsof -i :<port>  
  * sudo kill -9 <port>

All routes are implemented in the server.py file.

The database is initialized using the init.sql file.

Regarding the routes:

The application follows a REST API architecture and communicates using JSON objects. It includes routes for managing countries, cities, and temperatures. These routes allow adding, retrieving, updating, and deleting data. For example:

- Countries: Routes handle operations such as adding a new country, retrieving all countries, updating country details, and deleting a country.
- Cities: Routes enable adding a city to a specific country, retrieving cities based on the country, and managing city data.
- Temperatures: Routes manage temperature data associated with cities or countries. This includes filtering based on geographical coordinates, time intervals, and other criteria.
- 
Each route is designed to handle different HTTP methods (POST, GET, PUT, DELETE) with proper success and error responses, ensuring robust communication with the database.
