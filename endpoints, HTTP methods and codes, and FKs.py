endpoints and HTTP methods and codes
====================================
users
    POST 201 # ok
    GET 200 # ok
    PATCH 200 # ok
    DELETE 204 # ok
login
    POST 201 # ok
    # GET
    # PATCH
    DELETE 204 # ok
tasks
    POST 201 # ok
    GET 200 # ok
    PATCH 200 # ok
    DELETE 204 #


Foreign keys
============
id (in the users table)
–id in user_sessions
–userId in one_time_tasks

# -t-likes
# -comments
# -c-likes

# tweetId (tweets)
# -t-likes
# -comments

# commentId (comments)
# -c-likes