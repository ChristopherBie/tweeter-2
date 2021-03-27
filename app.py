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
    changedRows = None
    
    if request.method == "POST":
        try:
            email = request.json.get("email")
            username = request.json.get("username")
            password = request.json.get("password")
            bio = request.json.get("bio")
            birthdate = request.json.get("birthdate")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, birthdate, bio, password) VALUES (?, ?, ?, ?, ?)", [username, email, birthdate, bio, password])
            conn.commit()
            userId = cursor.lastrowid
            loginToken = secrets.token_hex(16)
            cursor.execute("INSERT INTO user_sessions (userId, loginToken) VALUES (?, ?)", [userId, loginToken])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                returnedData = {
                    "userId": userId,
                    "email": email,
                    "username": username,
                    "bio": bio,
                    "birthdate": birthdate,
                    "loginToken": loginToken
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


    elif request.method == "GET":
        try:
            userId = request.args.get("userId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT userId, email, username, bio, birthdate FROM users WHERE userId = ?", [userId])
                tweet_rows = cursor.fetchall()
            else:
                cursor.execute("SELECT userId, email, username, bio, birthdate FROM users")
                tweet_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if tweet_rows != None:
                tweet_list = []
                for tweet_row in tweet_rows:
                    tweet_dictionary = {
                        "userId": tweet_row[0],
                        "email": tweet_row[1],
                        "username": tweet_row[2],
                        "bio": tweet_row[3],
                        "birthdate": tweet_row[4]
                    }
                    tweet_list.append(tweet_dictionary)
                return Response(
                    json.dumps(tweet_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the tweeters' profiles.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "PATCH":
        try:
            email = request.json.get("email")
            username = request.json.get("username")
            password = request.json.get("password")
            bio = request.json.get("bio")
            birthdate = request.json.get("birthdate")
            loginToken = request.json.get("loginToken")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            if email != None:
                cursor.execute("UPDATE users SET email = ? WHERE userId = ?", [email, userId])
                conn.commit()
            if username != None:
                cursor.execute("UPDATE users SET username = ? WHERE userId = ?", [username, userId])
                conn.commit()
            if password != None:
                cursor.execute("UPDATE users SET password = ? WHERE userId = ?", [password, userId])
                conn.commit()
            if bio != None:
                cursor.execute("UPDATE users SET bio = ? WHERE userId = ?", [bio, userId])
                conn.commit()
            if birthdate != None:
                cursor.execute("UPDATE users SET birthdate = ? WHERE userId = ?", [birthdate, userId])
                conn.commit()
            cursor.execute("SELECT userId, email, username, bio, birthdate FROM users WHERE userId = ?", [userId])
            userRow = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if userRow != None:
                returnedData = {
                    "userId": userId,
                    "email": userRow[0][1],
                    "username": userRow[0][2],
                    "bio": userRow[0][3],
                    "birthdate": userRow[0][4],
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not update your info.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":
        try:
            loginToken = request.json.get("loginToken")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()

            cursor.execute("DELETE userId, loginToken FROM user_sessions WHERE loginToken = ?", [loginToken])
            conn.commit()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM users WHERE userId = ?", [userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "You have deleted your account. Thank you for using Tweeter.", 
                    mimetype = "application/json", 
                    status = 204
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
    changedRows = None
    
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
            cursor.execute("SELECT userId, username, email, birthdate, bio, password FROM users WHERE email = ? AND password = ?", [email, password])
            row = cursor.fetchone()
            userId = row[0]
            if row != None:
                loginToken = secrets.token_hex(16)
                cursor.execute("INSERT INTO user_sessions (userId, loginToken) VALUES (?, ?)", [userId, loginToken])
                conn.commit()
                changedRows = cursor.rowcount
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
            if changedRows == 1:
                returnedData = {
                    "userId": row[0],
                    "username": row[1],
                    "email": row[2],
                    "birthdate": row[3],
                    "bio": row[4],
                    "loginToken": loginToken
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


    elif request.method == "DELETE":
        try:
            loginToken = request.json.get("loginToken")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("DELETE userId, loginToken FROM user_sessions WHERE loginToken = ?", [loginToken])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "You have signed out. Thank you for using Tweeter.", 
                    mimetype = "application/json", 
                    status = 204
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



@app.route("/api/tweets", methods = ["POST", "GET", "PATCH", "DELETE"])
def tweets():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "POST":
        try:
            loginToken = request.json.get("loginToken")
            content = request.json.get("content")
            creationTime = datetime.now()
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM users WHERE userId = ?", [userId])
            username = cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweets (userId, content, creationTime) VALUES (?, ?, ?)", [userId, content, creationTime])
            conn.commit()
            tweetId = cursor.lastrowid
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                returnedData = {
                    "tweetId": tweetId,
                    "userId": userId,
                    "username": username,
                    "content": content,
                    "creationTime": creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT")
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Your tweet could not be posted.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":
        try:
            userId = request.args.get("userId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT tweets.tweetId, tweets.userId, users.username, tweets.content, tweets.creationTime FROM tweets INNER JOIN users ON tweets.userId = users.userId WHERE tweets.userId = ?", [userId])
                tweet_rows = cursor.fetchall()
                rows = cursor.rowcount
                if rows == 0:
                    print("There are no tweets by this user.")
            else:
                cursor.execute("SELECT tweets.tweetId, tweets.userId, users.username, tweets.content, tweets.creationTime FROM tweets INNER JOIN users ON tweets.userId = users.userId")
                tweet_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if tweet_rows != None:
                tweet_list = []
                for tweet_row in tweet_rows:
                    tweet_dictionary = {
                        "tweetId": tweet_row[0],
                        "userId": tweet_row[1],
                        "username": tweet_row[2],
                        "content": tweet_row[3],
                        "creationTime": tweet_row[4]
                    }
                    tweet_list.append(tweet_dictionary)
                return Response(
                    json.dumps(tweet_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the tweets.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "PATCH":
        try:
            tweetId = request.json.get("tweetId")
            content = request.json.get("content")
            creationTime = datetime.now()
            loginToken = request.json.get("loginToken")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("UPDATE tweets SET content = ? WHERE tweetId = ? AND userId = ?", [content, tweetId, userId])
            conn.commit()
            cursor.execute("UPDATE tweets SET creationTime = ? WHERE tweetId = ? AND userId = ?", [creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT"), tweetId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                returnedData = {
                    "tweetId": tweetId,
                    "content": content, 
                    "creationTime": creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT")
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not update the tweet.",    #If the user is not the original author, the edit button should not appear
                    mimetype = "html/text", 
                    status = 400
                )  


    elif request.method == "DELETE":
        try:
            loginToken = request.json.get("loginToken")
            tweetId = request.json.get("tweetId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweets WHERE tweetId = ? AND userId = ?", [tweetId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "Tweet deleted.", 
                    mimetype = "application/json", 
                    status = 204
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



@app.route("/api/tweet-likes", methods = ["POST", "GET", "PATCH", "DELETE"])
def tweet_likes():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "POST":
        try:
            loginToken = request.json.get("loginToken")
            tweetId = request.json.get("tweetId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweet_likes (tweetId, userId) VALUES (?, ?)", [tweetId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                return Response(
                    "Tweet like registered.", 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Could not register your tweet like.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":
        try:
            userId = request.args.get("tweetId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if tweetId != None:
                cursor.execute("SELECT tweets.tweetId, tweets.userId, users.username FROM tweets INNER JOIN users ON tweets.userId = users.userId WHERE tweets.tweetId = ?", [tweetId])
                tweet_rows = cursor.fetchall()
            else:
                tweet_rows = None
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if tweet_rows != None:
                tweet_list = []
                for tweet_row in tweet_rows:
                    tweet_dictionary = {
                        "tweetId": tweet_row[0],
                        "userId": tweet_row[1],
                        "username": tweet_row[2],
                    }
                    tweet_list.append(tweet_dictionary)
                return Response(
                    json.dumps(tweet_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the tweet likes.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":    ##
        try:
            loginToken = request.json.get("loginToken")
            tweetId = request.json.get("tweetId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweet_likes WHERE userId = ? AND tweetId = ?", [userId, tweetId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "Your tweet like has been deleted.", 
                    mimetype = "application/json", 
                    status = 204
                )
            else:
                return Response(
                    "Could not delete your tweet like.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/comments", methods = ["POST", "GET", "PATCH", "DELETE"])
def comments():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "POST":
        try:
            loginToken = request.json.get("loginToken")
            tweetId = request.json.get("tweetId")
            content = request.json.get("content")
            creationTime = datetime.now()
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM users WHERE userId = ?", [userId])
            username = cursor.fetchone()[0]
            cursor.execute("INSERT INTO comments (tweetId, userId, content, creationTime) VALUES (?, ?, ?, ?)", [tweetId, userId, content, creationTime])
            conn.commit()
            commentId = cursor.lastrowid
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                returnedData = {
                    "commentId": commentId,
                    "tweetId": tweetId,
                    "userId": userId,
                    "username": username,
                    "content": content,
                    "creationTime": creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT")
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Your comment could not be posted.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":
        try:
            tweetId = request.args.get("tweetId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if tweetId != None:
                cursor.execute("SELECT comments.commentId, comments.tweetId, comments.userId, users.username, comments.content, comments.creationTime FROM comments INNER JOIN users ON comments.userId = users.userId WHERE comments.tweetId = ?", [tweetId])
                comment_rows = cursor.fetchall()
                rows = cursor.rowcount
                if rows == 0:
                    print("There are no comments for this tweet.")
            else:
                cursor.execute("SELECT comments.commentId, comments.tweetId, comments.userId, users.username, comments.content, comments.creationTime FROM comments INNER JOIN users ON comments.userId = users.userId")
                comment_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if comment_rows != None:
                comment_list = []
                for comment_row in comment_rows:
                    comment_dictionary = {
                        "commentId": comment_row[0],
                        "tweetId": comment_row[1],
                        "userId": comment_row[2],
                        "username": comment_row[3],
                        "content": comment_row[4],
                        "creationTime": comment_row[5]
                    }
                    comment_list.append(comment_dictionary)
                return Response(
                    json.dumps(comment_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the comments.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "PATCH":
        try:
            commentId = request.json.get("commentId")
            content = request.json.get("content")
            creationTime = datetime.now()
            loginToken = request.json.get("loginToken")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("UPDATE comments SET content = ? WHERE commentId = ? AND userId = ?", [content, commentId, userId])
            conn.commit()
            cursor.execute("UPDATE comments SET creationTime = ? WHERE commentId = ? AND userId = ?", [creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT"), commentId, userId])
            conn.commit()
            changedRows = cursor.rowcount
            if changedRows != 0:
                cursor.execute("SELECT tweetId FROM comments WHERE commentId = ?", [commentId])
                tweetId = cursor.fetchone()[0]
                cursor.execute("SELECT username FROM users WHERE userId = ?", [userId])
                username = cursor.fetchone()[0]
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                returnedData = {
                    "commentId": commentId,
                    "tweetId": tweetId,
                    "userId": userId,
                    "username": username,
                    "content": content, 
                    "creationTime": creationTime.strftime("%H:%M:%S, %d/%m/%Y GMT")
                }
                return Response(
                    json.dumps(returnedData, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not update the comment.",    #If the user is not the original author, the edit button should not appear
                    mimetype = "html/text", 
                    status = 400
                )    


    elif request.method == "DELETE":
        try:
            loginToken = request.json.get("loginToken")
            commentId = request.json.get("commentId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM comments WHERE commentId = ? AND userId = ?", [commentId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "Comment deleted.", 
                    mimetype = "application/json", 
                    status = 204
                )
            else:
                return Response(
                    "Could not delete this comment.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/comment-likes", methods = ["POST", "GET", "PATCH", "DELETE"])
def comment_likes():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "POST":
        try:
            loginToken = request.json.get("loginToken")
            commentId = request.json.get("commentId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("INSERT INTO comment_likes (commentId, userId) VALUES (?, ?)", [commentId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                return Response(
                    "Comment like registered.", 
                    mimetype = "application/json", 
                    status = 201
                )
            else:
                return Response(
                    "Could not register your comment like.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":
        try:
            userId = request.args.get("commentId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if commentId != None:
                cursor.execute("SELECT comments.commentId, comments.userId, users.username FROM comments INNER JOIN users ON comments.userId = users.userId WHERE comments.commentId = ?", [commentId])
                comment_rows = cursor.fetchall()
            else:
                comment_rows = None
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if comment_rows != None:
                comment_list = []
                for comment_row in comment_rows:
                    comment_dictionary = {
                        "commentId": comment_row[0],
                        "userId": comment_row[1],
                        "username": comment_row[2],
                    }
                    comment_list.append(comment_dictionary)
                return Response(
                    json.dumps(comment_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not retrieve the comment likes.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":    ##
        try:
            loginToken = request.json.get("loginToken")
            commentId = request.json.get("commentId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM comment_likes WHERE userId = ? AND commentId = ?", [userId, commentId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "Your comment like has been deleted.", 
                    mimetype = "application/json", 
                    status = 204
                )
            else:
                return Response(
                    "Could not delete your comment like.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/follows", methods = ["POST", "GET", "DELETE"])
def follows():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "POST":
        try:
            loginToken = request.json.get("loginToken")
            followedId = request.json.get("followedId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("INSERT INTO follows (followerId, followedId) VALUES (?, ?)", [userId, followedId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows == 1:
                return Response(
                    "You are now following this tweeter.", 
                    mimetype = "application/json", 
                    status = 201    #changed 204 to 201 so message appears
                )
            else:
                return Response(
                    "Could not register your following.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "GET":
        try:
            userId = request.args.get("userId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT follows.followedId, users.email, users.username, users.bio, users.birthdate FROM follows JOIN users ON follows.followedId = users.userId WHERE follows.followerId = ?", [userId])
                user_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if user_rows != None:
                user_list = []
                for user_row in user_rows:
                    user_dictionary = {
                        "userId": user_row[0],
                        "email": user_row[1],
                        "username": user_row[2],
                        "bio": user_row[3],
                        "birthdate": user_row[4]
                    }
                    user_list.append(user_dictionary)
                return Response(
                    json.dumps(user_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not check which tweeters you are following, or you are not following anyone.", 
                    mimetype = "html/text", 
                    status = 400
                )


    elif request.method == "DELETE":
        try:
            loginToken = request.json.get("loginToken")
            followedId = request.json.get("followedId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_sessions WHERE loginToken = ?", [loginToken])
            userId = cursor.fetchone()[0]
            cursor.execute("DELETE FROM follows WHERE followedId = ? AND userId = ?", [followedId, userId])
            conn.commit()
            changedRows = cursor.rowcount
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if changedRows != 0:
                return Response(
                    "You are no longer following this tweeter.", 
                    mimetype = "application/json", 
                    status = 204
                )
            else:
                return Response(
                    "Could not delete your following.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )



@app.route("/api/followers", methods = ["GET"])
def followers():
    conn = None
    cursor = None
    changedRows = None
    
    if request.method == "GET":
        try:
            userId = request.args.get("userId")
            conn = mariadb.connect(
                host = dbcreds.host, 
                port = dbcreds.port, 
                user = dbcreds.username, 
                password = dbcreds.password, 
                database = dbcreds.database
            )
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT follows.followerId, users.email, users.username, users.bio, users.birthdate FROM follows JOIN users ON follows.followerId = users.userId WHERE follows.followedId = ?", [userId])
                user_rows = cursor.fetchall()
        except Exception as error1:
            print("There was an error: " + error1)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if user_rows != None:
                user_list = []
                for user_row in user_rows:
                    user_dictionary = {
                        "userId": user_row[0],
                        "email": user_row[1],
                        "username": user_row[2],
                        "bio": user_row[3],
                        "birthdate": user_row[4]
                    }
                    user_list.append(user_dictionary)
                return Response(
                    json.dumps(user_list, default = str), 
                    mimetype = "application/json", 
                    status = 200
                )
            else:
                return Response(
                    "Could not check which tweeters are following you, or no one is following you.", 
                    mimetype = "html/text", 
                    status = 400
                )


    else:
        Response(
            "This method is not supported.", 
            mimetype = "text/html", 
            status = 501
        )