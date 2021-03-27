endpoints and HTTP methods and codes
====================================
# users
#     # POST 201 # ok
#     # GET 200 ok
#     PATCH 200 #
#     DELETE 204 #
# login
#     POST 201 # ok
#     # GET
#     # PATCH
#     DELETE 204 # ok
# follows
#     # POST 204 # ok
#     # GET 200 ok
#     # PATCH
#     DELETE 204 #
# followers
    #POST
    # GET 200 ok
    #PATCH
    #DELETE
tweets
    # POST 201 # ok
    # GET 200 ok
    PATCH 200
    DELETE 204 #
# tweet-likes
#     # POST 201 # ok
#     GET 200 #
#     #PATCH
#     DELETE 204 #
# comments
#     # POST 201 # ok
#     GET 200 #
#     PATCH 200 #
#     DELETE 204 #
# comment-likes
#     # POST 201 # ok
#     GET 200 #
#     #PATCH
#     DELETE 204 #



FKs
===
userId (users)
–user_sessions
-follows (followers & followed)
–tweets
-t-likes
-comments
-c-likes

tweetId (tweets)
-t-likes
-comments

commentId (comments)
-c-likes