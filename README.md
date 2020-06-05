Editor: Davis Bosworth dboswor2@uoregon.edu


## Building/Running my Program in terminal
$ docker-compose build
$ docker-compose up

All APIs are on localhost port 5000. Individual API links on localhost:5001/APIname. The brevet calculator is on localhost:5003.


# Project 7: Adding authentication and user interface to brevet time calculator service


## What is in this repo
This program, with the help of flask and ajax, calculates ACP controle times. It is an attempt to duplicate the calculator found at https://rusa.org/octime_acp.html. A full list of the rules may be found at https://rusa.org/pages/acp-brevet-control-times-calculator. The km entered may not exceed the distance significantly. Open to close times on the first 0km will have 1 hour added. Km values may not be negative. Values less than 20% of the original distance will be rounded down. Values less than the distance will be treated as normal. Project 7 builds off of project 6 by adding password and token-based authentication for the brevet APIs. Users may register an account, login, and then use the given token to access the APIs via URL. Functionalities such as: CSRF protection, remember me, and logout are also available to users. Users may go to localhost/port 5001/ to visit the homepage, or index. On the index, users may choose to login, register, or logout. To run through all of the features, user should first register an account. Once that is done, then go to login. After hitting submit on a successful login the user will be given a token. To visit the APIs, unlike project 6 you may not just use the links below. Use the links below, but at the end of the URL being used add: ?token='users token'. E.g: (http://localhost:5001/listAll/json?token=eyxc3_990dnjskfnwlwn_263746fbk) is a proper URL. User's login and register links may be found by using localhost:5001/api/login or api/register.


This program uses the same logic with the addition of REST APIs. You may view all APIs on port 5000 or visit individual APIs through port 5001.


## Supported Links:
* "http://<host:port>/listAll" return all open and close times in the database
* "http://<host:port>/listOpenOnly" return open times only
* "http://<host:port>/listCloseOnly" return close times only

* "http://<host:port>/listAll/csv" return all open and close times in CSV format
* "http://<host:port>/listOpenOnly/csv" return open times only in CSV format
* "http://<host:port>/listCloseOnly/csv" return close times only in CSV format

* "http://<host:port>/listAll/json" return all open and close times in JSON format
* "http://<host:port>/listOpenOnly/json" return open times only in JSON format
* "http://<host:port>/listCloseOnly/json" return close times only in JSON format

* "http://<host:port>/listOpenOnly/csv?top=3" return top 3 open times only (in ascending order) in CSV format 
* "http://<host:port>/listOpenOnly/json?top=5" return top 5 open times only (in ascending order) in JSON format
* "http://<host:port>/listCloseOnly/csv?top=6" return top 5 close times only (in ascending order) in CSV format
* "http://<host:port>/listCloseOnly/json?top=4" return top 4 close times only (in ascending order) in JSON format