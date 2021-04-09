import dbcreds
import mariadb
from flask import Flask, request, Response
from flask_cors import CORS
import json
import secrets
from datetime import datetime

app = Flask(__name__)
CORS(app)




@app.route("/api/users", methods = ["POST", "GET", "PATCH", "DELETE"])
def users():
    conn = None
    cursor = None
    table_rows = None
    nr_of_rows = None
    
    if request.method == "POST":
        try:
            email = request.json.get("email")
            username = request.json.get("username")
            password = request.json.get("password")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", [email, username, password])
            conn.commit()
            userId = cursor.lastrowid
            login_token = secrets.token_hex(16)
            cursor.execute("INSERT INTO user_sessions (id, login_token) VALUES (?, ?)", [userId, login_token])
            conn.commit()
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:    #if there are no rows, cursor.rowcount returns -1
                returnedData = {
                    "userId": userId,
                    "email": email,
                    "username": username,
                    "login_token": login_token
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Your registration failed.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":    #users
        try:
            login_token = request.json.get("login_token")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            cursor.execute("SELECT email, username FROM users WHERE id = ?", [userId])
            table_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if table_rows != None:
                task_list = []
                for table_row in table_rows:
                    task_dictionary = {
                        "userId": userId,
                        "email": table_row[0],
                        "username": table_row[1]
                    }
                    task_list.append(task_dictionary)
                return Response(
                    json.dumps(task_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve your profile.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "PATCH":    #users
        try:
            email = request.json.get("email")
            username = request.json.get("username")
            password = request.json.get("password")
            login_token = request.json.get("login_token")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            if email != None:
                cursor.execute("UPDATE users SET email = ? WHERE id = ?", [email, userId])
                conn.commit()
            if username != None:
                cursor.execute("UPDATE users SET username = ? WHERE id = ?", [username, userId])
                conn.commit()
            if password != None:
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", [password, userId])
                conn.commit()
            nr_of_rows = cursor.rowcount
            if nr_of_rows > -1:
                cursor.execute("SELECT email, username FROM users WHERE id = ?", [userId])
                table_row = cursor.fetchone()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if table_row != None:
                returnedData = {
                    "userId": userId,
                    "email": table_row[0],
                    "username": table_row[1]
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Your info could not be updated.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":    #users
        try:
            login_token = request.json.get("login_token")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM user_sessions WHERE id = ?", [userId])
            conn.commit()
            cursor.execute("DELETE FROM users WHERE id = ?", [userId])
            conn.commit()
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                return Response(
                    "You have deleted your account. Thank you for using Task Manager.", 
                    mimetype = "html/text", 
                    status = 200
                )
            else:
                return Response(
                    "Could not delete your account.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/login", methods = ["POST", "DELETE"])
def login():
    conn = None
    cursor = None
    table_rows = None
    nr_of_rows = None

    if request.method == "POST":
        try:
            email = request.json.get("email")
            password = request.json.get("password")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, password FROM users WHERE email = ? AND password = ?", [email, password])
            table_row = cursor.fetchone()
            userId = table_row[0]
            if table_row != None:
                login_token = secrets.token_hex(16)
                cursor.execute("INSERT INTO user_sessions (id, login_token) VALUES (?, ?)", [userId, login_token])
                conn.commit()
                nr_of_rows = cursor.rowcount
            else:
                print("The email address or password is incorrect.")
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                returnedData = {
                    "userId": table_row[0],
                    "email": table_row[1],
                    "username": table_row[2],
                    "login_token": login_token
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Your login failed.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":    #login
        try:
            login_token = request.json.get("login_token")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE login_token = ?", [login_token])
            conn.commit()
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                return Response(
                    "You have signed out. Thank you for using Tweeter.", 
                    mimetype = "html/text", 
                    status = 200
                )
            else:
                return Response(
                    "Could not sign you out.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/one-time-tasks", methods = ["POST", "GET", "PATCH", "DELETE"])
def one_time_tasks():
    conn = None
    cursor = None
    table_rows = None
    nr_of_rows = None
    
    if request.method == "POST":
        try:
            login_token = request.json.get("login_token")
            content = request.json.get("content")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            cursor.execute("INSERT INTO one_time_tasks (userId, content) VALUES (?, ?)", [userId, content])
            conn.commit()
            taskId = cursor.lastrowid
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                returnedData = {
                    "taskId": taskId,
                    "userId": userId,
                    "content": content,
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Your task could not be posted.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":    #one-time
        try:
            login_token = request.json.get("login_token")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            if userId != None:
                cursor.execute("SELECT id, content FROM one_time_tasks WHERE userId = ?", [userId])
                table_rows = cursor.fetchall()
            if table_rows == None:
                print("You have no one-time tasks.")
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if table_rows != None:
                task_list = []
                for table_row in table_rows:
                    task_dictionary = {
                        "taskId": table_row[0],
                        "userId": userId,
                        "content": table_row[1]
                    }
                    task_list.append(task_dictionary)
                return Response(
                    json.dumps(task_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the tasks.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "PATCH":    #one-time
        try:
            taskId = request.json.get("taskId")    #each taskId corresponds to only one user
            content = request.json.get("content")
            # login_token = request.json.get("login_token")    #users can see and edit only their own tasks
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM one_time_tasks WHERE id = ?", [taskId])
            userId = cursor.fetchone()[0]
            cursor.execute("UPDATE one_time_tasks SET content = ? WHERE id = ?", [content, taskId])
            conn.commit()
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                returnedData = {
                    "taskId": taskId,
                    "content": content
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not update the tweet.",
                    mimetype = "html/text", 
                    status = 400
                )  


    elif request.method == "DELETE":    #tweets
        try:
            login_token = request.json.get("login_token")
            taskId = request.json.get("taskId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_sessions WHERE login_token = ?", [login_token])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweets WHERE id = ? AND userId = ?", [taskId, userId])
            conn.commit()
            nr_of_rows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if nr_of_rows != None and nr_of_rows != -1:
                return Response(
                    "Tweet deleted.", 
                    mimetype = "html/text", 
                    status = 200
                )
            else:
                return Response(
                    "Could not delete this tweet.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )