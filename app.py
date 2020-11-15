import flask
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
import random
import string
import requests
import json
from pyfcm import FCMNotification

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#code to convert the number format
def number_format(num):
  num = float('{:.3g}'.format(num))
  magnitude = 0
  while abs(num) >= 1000:
    magnitude += 1
    num /= 1000.0
  return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

#code to generate a random id
def get_random_string(txt,length):
    result_str = txt +''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return result_str

# Obtain connection string information from the portal
config = {
  'host':'selfilmindia.mysql.database.azure.com',
  'user':'selfilmadmin@selfilmindia',
  'password':'accelstack@#123',
  'database':'selfilm',
}


# # Construct connection string
# try:
#    conn = mysql.connector.connect(**config)
#    print("Connection established")
# except mysql.connector.Error as err:
#   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#     print("Something is wrong with the user name or password")
#   elif err.errno == errorcode.ER_BAD_DB_ERROR:
#     print("Database does not exist")
#   else:
#     print(err)


@app.route('/createorlogin', methods=['POST'])
def insertusers():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Full_Name = data.get('Full_Name', '')
    Bio = data.get('Bio', '')
    User_Name = data.get('User_Name', '')
    Email = data.get('Email', '')
    Profile_Picture = data.get('Profile_Picture', '')
    Device_Token = data.get('Device_Token', '')
    Device = data.get('Device', '')
    Total_Likes = data.get('Total_Likes', '')
    Verified = data.get('Verified', '')
    Blocked = data.get('Blocked', '')
    Version = data.get('Version', '')
    Signup_Type = data.get('Signup_Type', '')
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    a = User_Name.split('@')
    User_Name = a[0]

    sql_searchuser_query = """select * from users where uid = %s"""
    mycursor.execute(sql_searchuser_query, (Uid,))
    usersList = mycursor.fetchall()

    user_len = len(usersList)

    if user_len == 0:
        # Preparing SQL query to INSERT a record into the database.
        insert_stmt = (
            "INSERT INTO users(uid, fullname, bio, username, email, profile_pic, device, tokon, block, verified, version, signup_type, total_likes, created)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        insertdata = (
        Uid, Full_Name, Bio, User_Name, Email, Profile_Picture, Device, Device_Token, Blocked, Verified, Version,
        Signup_Type, Total_Likes, Created_Date)
        try:
            # Executing the SQL command
            mycursor.execute(insert_stmt, insertdata)
            # Commit your changes in the database
            conn.commit()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


    else:
        sql_update_device_token = """Update users set tokon = %s where uid = %s"""
        insertdata = (Device_Token, Uid)
        try:
            mycursor.execute(sql_update_device_token, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))



    sql_select_query = """select * from users where UID = %s"""
    mycursor.execute(sql_select_query, (Uid,))
    record = mycursor.fetchall()

    sql_selectfollowings_query = """select * from follow_users where uid = %s"""
    mycursor.execute(sql_selectfollowings_query, (Uid,))
    followingList = mycursor.fetchall()
    following_len = len(followingList)
    following_len = number_format(following_len)

    sql_selectfollowings_query = """select * from follow_users where followed_uid = %s"""
    mycursor.execute(sql_selectfollowings_query, (Uid,))
    followersList = mycursor.fetchall()
    follower_len = len(followersList)
    follower_len = number_format(follower_len)
    conn.commit()
    mycursor.close()
    for row in record:
        return jsonify({
            "Uid": row[1],
            "Full_Name": row[4],
            "Bio": row[5],
            "User_Name": row[2],
            "Email": row[14],
            "Profile_Pic": row[6],
            "Blocked": row[7],
            "Verified": row[3],
            "Created": row[12],
            "Following": following_len,
            "Follower": follower_len,
            "Total_Likes": row[13]})


@app.route('/getuserprofile', methods=['POST'])
def getprofiledetails():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    data = request.get_json()
    My_Uid = data.get('My_Uid', '')
    Uid = data.get('Uid', '')
    sql_select_query = """select * from users where UID = %s"""
    cursor.execute(sql_select_query, (Uid,))
    record = cursor.fetchall()

    sql_selectfollowings_query = """select * from follow_users where uid = %s"""
    cursor.execute(sql_selectfollowings_query, (Uid,))
    followingList = cursor.fetchall()
    following_len = len(followingList)
    following_len = number_format(following_len)

    sql_selectfollowings_query = """select * from follow_users where followed_uid = %s"""
    cursor.execute(sql_selectfollowings_query, (Uid,))
    followersList = cursor.fetchall()
    follower_len = len(followersList)
    follower_len = number_format(follower_len)
    follow_status = ""

    sql_selectfollowings_status_query = """select * from follow_users where uid = %s and followed_uid = %s """
    cursor.execute(sql_selectfollowings_status_query, (My_Uid,Uid))
    followingstatus = cursor.fetchall()
    following_status = len(followingstatus)
    if following_status == 0:
        follow_status = "false"
    else:
        follow_status = "true"

    conn.commit()
    cursor.close()
    for row in record:
        return jsonify({
            "Uid":row[1],
            "Full_Name":row[4],
            "Bio":row[5],
            "User_Name":row[2],
            "Email":row[14],
            "Profile_Pic":row[6],
            "Blocked":row[7],
            "Verified":row[3],
            "Created":row[12],
            "Following":following_len,
            "Follower":follower_len,
            "Total_Likes":row[13],
            "Follow_Status": follow_status
        })


@app.route('/addvideoposts', methods=['POST'])
def insertvideospost():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Video_Id = data.get('Video_Id', '')
    UID = data.get('UID', '')
    Description = data.get('Description', '')
    Sound_Id = data.get('Sound_Id', '')
    Video_Thum = data.get('Video_Thum', '')
    Video_Url = data.get('Video_Url', '')
    Views = 0
    Total_Likes = 0
    Privacy_Type = data.get('Privacy_Type', '')
    Allow_Comment = data.get('Allow_Comment', '')
    Allow_Duet = data.get('Allow_Duet', '')
    Sound_Name = data.get('Sound_Name', '')
    Sound_Description = data.get('Sound_Description', '')
    Sound_Thum = data.get('Sound_Thum', '')
    Sound_Section = ""
    Sound_Url = data.get('Sound_Url', '')
    Uploaded_By = "user"
    Video_Reports = 0
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    hashtag_list = []
    for word in Description.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    Sections = ','.join(hashtag_list)

    # Preparing SQL query to INSERT a record into the database.
    insert_video = (
        "INSERT INTO videos(uid,video_id, description, sound_id, section, thum, video, privacy_type, allow_comments, allow_duet,view,created,total_likes,uploaded_by,video_reports)"
        "VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s, %s)"
    )
    insertdata = (UID, Video_Id, Description, Sound_Id, Sections, Video_Thum, Video_Url, Privacy_Type, Allow_Comment, Allow_Duet,Views,Created_Date,Total_Likes,Uploaded_By,Video_Reports)

    try:
        mycursor.execute(insert_video, insertdata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    hastag_len = len(hashtag_list)
    for i in range(0, hastag_len):
        tag = hashtag_list[i]
        hastag = tag.lower()

        sql_searchsound_query = """select * from discover_section where section_name = %s"""
        mycursor.execute(sql_searchsound_query, (hastag,))
        sectiondata = mycursor.fetchall()
        section_len = len(sectiondata)
        if section_len == 0:
            Section_Id = get_random_string("D_SECTION_", 10)
            insert_dsection = (
                "INSERT INTO discover_section(section_name,created,section_id,videos)"
                "VALUES (%s, %s, %s, %s)"
            )
            insertdata = (tag, Created_Date, Section_Id, Video_Id)

            try:
                mycursor.execute(insert_dsection, insertdata)
                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))


        else:
            for videos in sectiondata:
                total_videos = videos[4]
                total_videos = total_videos+","+Video_Id
                sql_update_secvideos = """Update discover_section set videos = %s where section_name = %s"""
                insertdata = (total_videos, hastag)
                try:
                    mycursor.execute(sql_update_secvideos, insertdata)
                    conn.commit()

                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))


    sql_searchsound_query = """select * from sound where sound_id = %s"""
    mycursor.execute(sql_searchsound_query, (Sound_Id,))
    soundList = mycursor.fetchall()

    sound_len = len(soundList)

    if sound_len == 0:
        insert_sound = (
            "INSERT INTO sound(sound_id,sound_name, description, thum, section, uploaded_by, created,sound_url)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        insertdata = (
        Sound_Id,Sound_Name,Sound_Description, Sound_Thum,Sound_Section,Uploaded_By, Created_Date, Sound_Url)

        try:
            # Executing the SQL command
            mycursor.execute(insert_sound, insertdata)

            # Commit your changes in the database
            conn.commit()


        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

    conn.commit()
    mycursor.close()
    return jsonify({
        "code": 200,
        "status": "success uploading video"
    })


@app.route('/editprofile', methods=['POST'])
def editprofile():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Full_Name = data.get('Full_Name', '')
    Bio = data.get('Bio', '')
    User_Name = data.get('User_Name', '')
    Email = data.get('Email', '')
    Profile_Picture = data.get('Profile_Picture', '')

    sql_update_profile = """Update users set fullname = %s, bio = %s, username = %s, email = %s, profile_pic = %s where uid = %s"""

    insertdata = (Full_Name,Bio,User_Name,Email,Profile_Picture,Uid)

    try:
        # Executing the SQL command
        mycursor.execute(sql_update_profile, insertdata)

        # Commit your changes in the database
        conn.commit()


    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    mydb = mysql.connector.connect(
        host="34.67.36.162",
        user="root",
        password="",
        database="selfilm"
    )
    mycursor = mydb.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Full_Name = data.get('Full_Name', '')
    Bio = data.get('Bio', '')
    User_Name = data.get('User_Name', '')
    Email = data.get('Email', '')
    Profile_Picture = data.get('Profile_Picture', '')

    sql_update_profile = """Update users set fullname = %s, bio = %s, username = %s, email = %s, profile_pic = %s where uid = %s"""

    insertdata = (Full_Name, Bio, User_Name, Email, Profile_Picture, Uid)

    try:
        # Executing the SQL command
        mycursor.execute(sql_update_profile, insertdata)

        # Commit your changes in the database
        conn.commit()


    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

    sql_select_query = """select * from users where UID = %s"""
    mycursor.execute(sql_select_query, (Uid,))
    record = mycursor.fetchall()

    sql_selectfollowings_query = """select * from follow_users where uid = %s"""
    mycursor.execute(sql_selectfollowings_query, (Uid,))
    followingList = mycursor.fetchall()
    following_len = len(followingList)
    following_len = number_format(following_len)

    sql_selectfollowings_query = """select * from follow_users where followed_uid = %s"""
    mycursor.execute(sql_selectfollowings_query, (Uid,))
    followersList = mycursor.fetchall()
    follower_len = len(followersList)
    follower_len = number_format(follower_len)
    conn.commit()
    mycursor.close()
    for row in record:
        return jsonify({
            "Uid": row[1],
            "Full_Name": row[4],
            "Bio": row[5],
            "User_Name": row[2],
            "Email": row[14],
            "Profile_Pic": row[6],
            "Blocked": row[7],
            "Verified": row[3],
            "Created": row[12],
            "Following": following_len,
            "Follower": follower_len,
            "Total_Likes": row[13]})

@app.route('/like_dislike_videos', methods=['POST'])
def likevideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    Action = data.get('Action', '')
    Action = int(Action)
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")


    if Action == 1:

        sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
        mycursor.execute(sql_liked_query, (Video_Id, Uid))
        liked_status = mycursor.fetchall()

        status = len(liked_status)

        if status == 0:
            insert_like = (
                "INSERT INTO video_like_dislike(uid,video_id, action, created)"
                "VALUES (%s, %s, %s, %s)"
            )
            insertdata = (Uid, Video_Id, Action, Created_Date)

            try:
                mycursor.execute(insert_like, insertdata)

                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))


            # update like in profile table
            sql_select_query = """select * from videos where video_id = %s"""
            mycursor.execute(sql_select_query, (Video_Id,))
            uid = mycursor.fetchall()
            post_uid = ""
            for value in uid:
                post_uid = value[1]
            sql_select_query = """select * from users where UID = %s"""
            mycursor.execute(sql_select_query, (post_uid,))
            likes = mycursor.fetchall()
            reciever = ""
            device_token = ""
            for count in likes:
                reciever =  count[2]
                total_count = count[13]
                device_token = count[11]
                total_count = int(total_count) + 1
                sql_update_profile = """Update users set total_likes = %s where uid = %s"""
                insertdata = (total_count, post_uid)
                try:
                    mycursor.execute(sql_update_profile, insertdata)
                    conn.commit()

                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))


            sql_liker_query = """select * from users where UID = %s"""
            mycursor.execute(sql_liker_query, (Uid,))
            liker = mycursor.fetchall()
            name = ""
            for liked_by in liker:
                name = liked_by[2]

            #send notification
            message_title1 = reciever
            message_body1 = name + "has liked your video"

            push_service = FCMNotification(
                api_key="AAAAWfx9J-U:APA91bGN1WHX3nNfLpASY6JFN09tc4CQ0oUynpRuf82yZsYyFvqSKknX7kWL2fbPZArF2hXLSsfnDgzLzmrfncG8EP1stw5P8Voou48VLtFvkFGLtJSSPV_Ehm5a8sDPDimSuU7GRnFe")

            registration_id = device_token
            message_title = message_title1
            message_body = message_body1
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                       message_body=message_body)

            # add to notification table
            insert_notification = (
                "INSERT INTO notification(my_uid,effected_uid,type,value,created)"
                "VALUES (%s, %s, %s, %s, %s)"
            )
            insertdata = (Uid, post_uid, "like", Video_Id, Created_Date)

            try:
                mycursor.execute(insert_notification, insertdata)
                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))


            conn.commit()
            mycursor.close()
            return "Video Liked"
        else:
            return "already liked"

    else:
        delete_like = (
            "DELETE FROM video_like_dislike WHERE uid = %s AND video_id = %s"
        )
        insertdata = (Uid, Video_Id)

        try:
            mycursor.execute(delete_like, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        # update like in profile table
        sql_select_query = """select * from videos where video_id = %s"""
        mycursor.execute(sql_select_query, (Video_Id,))
        uid = mycursor.fetchall()
        for value in uid:
            post_uid = value[1]
        sql_select_query = """select * from users where UID = %s"""
        mycursor.execute(sql_select_query, (post_uid,))
        likes = mycursor.fetchall()
        for count in likes:
            total_count = count[13]
            total_count = int(total_count) - 1
            sql_update_profile = """Update users set total_likes = %s where uid = %s"""
            insertdata = (total_count, post_uid)
            try:
                mycursor.execute(sql_update_profile, insertdata)
                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))

        return "Video disliked"


@app.route('/post_comment', methods=['POST'])
def commentvideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    # Comment = data.get('Comment', '')
    Comment = {
        "hero":"santhosh",
        "heroin":"radhika pandit",
        "producer":"rakesh gowrav",
        "director":"nishanth naik"
    }
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    insert_comment = (
        "INSERT INTO video_comment(uid,video_id, comments, created)"
        "VALUES (%s, %s, %s, %s)"
    )
    insertdata = (Uid, Video_Id, Comment, Created_Date)

    try:
        cursor.execute(insert_comment, insertdata)

        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

    sql_select_query = """SELECT * FROM video_comment WHERE video_id = %s"""
    cursor.execute(sql_select_query, (Video_Id,))
    comments = cursor.fetchall()
    comment_data = []
    for cmnt in comments:
        uid = str(cmnt[2])

        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (uid,))
        user_prof = cursor.fetchall()

        for userdata in user_prof:
            a = {
                "Comment": cmnt[3],
                "Created": cmnt[4],
                "Uid": cmnt[2],
                "user_info" : {
                "Full_Name": userdata[4],
                "User_Name": userdata[2],
                "Profile_Pic": userdata[6],
                "Verified": userdata[3]
                }
            }
            comment_data.append(a)

    sorteddata = sorted(
        comment_data,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )

    # notification sender
    sql_select_query = """select * from users where UID = %s"""
    cursor.execute(sql_select_query, (Uid,))
    liker = cursor.fetchall()
    sender = ""
    for count in liker:
        sender = count[2]

    # reciever uid
    sql_select_query = """select * from videos where video_id = %s"""
    cursor.execute(sql_select_query, (Video_Id,))
    uid = cursor.fetchall()
    post_uid = ""
    for value in uid:
        post_uid = value[1]

    # notification reciever
    sql_liker_query = """select * from users where UID = %s"""
    cursor.execute(sql_liker_query, (post_uid,))
    likedfor = cursor.fetchall()
    reciever = ""
    device_token = ""
    for liked_by in likedfor:
        reciever = liked_by[2]
        device_token = liked_by[11]

    # send notification
    message_title1 = reciever
    message_body1 = sender + " has commented on your video"

    push_service = FCMNotification(
        api_key="AAAAWfx9J-U:APA91bGN1WHX3nNfLpASY6JFN09tc4CQ0oUynpRuf82yZsYyFvqSKknX7kWL2fbPZArF2hXLSsfnDgzLzmrfncG8EP1stw5P8Voou48VLtFvkFGLtJSSPV_Ehm5a8sDPDimSuU7GRnFe")

    registration_id = device_token
    message_title = message_title1
    message_body = message_body1
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               message_body=message_body)

    # add to notification table
    insert_notification = (
        "INSERT INTO notification(my_uid,effected_uid,type,value,created)"
        "VALUES (%s, %s, %s, %s, %s)"
    )
    insertdata = (Uid, post_uid, "comment", Video_Id, Created_Date)

    try:
        cursor.execute(insert_notification, insertdata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

    conn.commit()
    cursor.close()
    return jsonify({
        "msg" : sorteddata
    })


@app.route('/follow_users', methods=['POST'])
def followusers():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Followed_Uid = data.get('Followed_Uid', '')
    Action = data.get('Action', '')
    status = int(Action)
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    if status == 1:
        follow_users = (
            "INSERT INTO follow_users(uid,followed_uid, created)"
            "VALUES (%s, %s, %s)"
        )
        insertdata = (Uid, Followed_Uid, Created_Date)

        try:
            mycursor.execute(follow_users, insertdata)

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        # notification sender
        sql_select_query = """select * from users where UID = %s"""
        mycursor.execute(sql_select_query, (Uid,))
        follower = mycursor.fetchall()
        sender = ""
        for count in follower:
            sender = count[2]

        # notification reciever
        sql_liker_query = """select * from users where UID = %s"""
        mycursor.execute(sql_liker_query, (Followed_Uid,))
        followed = mycursor.fetchall()
        reciever = ""
        device_token = ""
        for liked_by in followed:
            reciever = liked_by[2]
            device_token = liked_by[11]

        # send notification
        message_title1 = reciever
        message_body1 = sender + " has started following you"

        push_service = FCMNotification(
            api_key="AAAAWfx9J-U:APA91bGN1WHX3nNfLpASY6JFN09tc4CQ0oUynpRuf82yZsYyFvqSKknX7kWL2fbPZArF2hXLSsfnDgzLzmrfncG8EP1stw5P8Voou48VLtFvkFGLtJSSPV_Ehm5a8sDPDimSuU7GRnFe")

        registration_id = device_token
        message_title = message_title1
        message_body = message_body1
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)

        # add to notification table
        insert_notification = (
            "INSERT INTO notification(my_uid,effected_uid,type,value,created)"
            "VALUES (%s, %s, %s, %s, %s)"
        )
        insertdata = (Uid, Followed_Uid, "follow", "0", Created_Date)

        try:
            mycursor.execute(insert_notification, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        conn.commit()
        mycursor.close()
        return "user followed"



    else:
        unfollow_users = (
            "DELETE FROM follow_users WHERE uid = %s AND followed_uid = %s"
        )
        removedata = (Uid, Followed_Uid)

        try:
            mycursor.execute(unfollow_users, removedata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        conn.commit()
        cursor.close()

        return "user unfollowed"


@app.route('/getallvideos', methods=['POST'])
def getrelatedvideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    videotype = data.get('vtype', '')
    privacy_type = "public"
    uploaded_by = "user"

    x = datetime.now()
    y = datetime.now() - timedelta(days=20)

    end = x.strftime("%d:%m:%Y")
    start = y.strftime("%d:%m:%Y")


    #admin added ads
    sql_selectVideo_query = """select * from videos where Privacy_Type = %s and uploaded_by = %s"""
    cursor.execute(sql_selectVideo_query, (privacy_type, "admin"))
    videosList = cursor.fetchall()

    videos_len = len(videosList)
    if videos_len == 0:
        sorted_ads = []
    else:
        ads = []
        for row in videosList:
            UID = row[1]
            Video_Id = row[12]
            Sound_Id = row[7]
            sql_select_query = """select * from users where uid = %s"""
            cursor.execute(sql_select_query, (UID,))
            user_prof = cursor.fetchall()

            sql_like_query = """select * from video_like_dislike where video_id = %s"""
            cursor.execute(sql_like_query, (Video_Id,))
            likes = cursor.fetchall()
            like_count = len(likes)
            like_count = number_format(like_count)

            sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
            cursor.execute(sql_liked_query, (Video_Id, Uid))
            like_status = cursor.fetchall()
            likeds = len(like_status)
            if likeds == 0:
                liked = False
            else:
                liked = True

            sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
            cursor.execute(sql_saved_query, (Video_Id, Uid))
            saved_status = cursor.fetchall()
            saved = len(saved_status)
            if saved == 0:
                Saved = False
            else:
                Saved = True

            sql_cmnt_query = """select * from video_comment where video_id = %s"""
            cursor.execute(sql_cmnt_query, (Video_Id,))
            cmnts = cursor.fetchall()
            cmnts_count = len(cmnts)
            cmnts_count = number_format(cmnts_count)

            sql_sound_query = """select * from sound where sound_id = %s"""
            cursor.execute(sql_sound_query, (Sound_Id,))
            sound_info = cursor.fetchall()

            for sound in sound_info:
                mp3 = sound[8]
                Sound_Name = sound[1]
                Description = sound[2]
                Thum = sound[3]
                Created = sound[6]

            for userdata in user_prof:
                user_info = {
                    "Full_Name": userdata[4],
                    "User_Name": userdata[2],
                    "Profile_Pic": userdata[6],
                    "Blocked": userdata[7],
                    "Verified": userdata[3]
                }

                a = {
                    "UID": row[1],
                    "User_Info": user_info,
                    "count": {
                        "like_count": like_count,
                        "video_comment_count": cmnts_count
                    },
                    "sound": {
                        "id": Sound_Id,
                        "audio_path": {
                            "mp3": mp3
                        },
                        "sound_name": Sound_Name,
                        "description": Description,
                        "thum": Thum,
                        "sound_created": Created
                    },
                    "Liked": liked,
                    "Saved": Saved,
                    "Video_Id": row[12],
                    "Description": row[2],
                    "Sound_Id": row[7],
                    "Sections": row[6],
                    "Video_Thum": row[4],
                    "Video_Url": row[3],
                    "Privacy_Type": row[8],
                    "Allow_Comment": row[9],
                    "Allow_Duet": row[10],
                    "Views": row[5],
                    "Created": row[11]
                }
                ads.append(a)

        sorted_ads = sorted(
            ads,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )
        random.shuffle(sorted_ads)

    #related videos for home screen
    if videotype == "related":
        sql_selectVideo_query = """SELECT * FROM videos WHERE Privacy_Type = %s AND uploaded_by = %s"""
        cursor.execute(sql_selectVideo_query, (privacy_type,uploaded_by))
        videosList = cursor.fetchall()

        videos_len = len(videosList)
        if videos_len == 0:
            return jsonify({
                "msg":[]
            })
        else:
            output = []
            for row in videosList:
                UID = row[1]
                Video_Id = row[12]
                Sound_Id = row[7]

                sql_select_query = """select * from offtable where uid = %s and video_id = %s"""
                cursor.execute(sql_select_query, (Uid,Video_Id))
                off_data = cursor.fetchall()
                if len(off_data) == 0:
                    sql_select_query = """select * from users where uid = %s"""
                    cursor.execute(sql_select_query, (UID,))
                    user_prof = cursor.fetchall()

                    sql_like_query = """select * from video_like_dislike where video_id = %s"""
                    cursor.execute(sql_like_query, (Video_Id,))
                    likes = cursor.fetchall()
                    like_count = len(likes)
                    like_count = number_format(like_count)

                    sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                    cursor.execute(sql_liked_query, (Video_Id, Uid))
                    like_status = cursor.fetchall()
                    likeds = len(like_status)
                    if likeds == 0:
                        liked = False
                    else:
                        liked = True

                    sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                    cursor.execute(sql_saved_query, (Video_Id, Uid))
                    saved_status = cursor.fetchall()
                    saved = len(saved_status)
                    if saved == 0:
                        Saved = False
                    else:
                        Saved = True

                    sql_cmnt_query = """select * from video_comment where video_id = %s"""
                    cursor.execute(sql_cmnt_query, (Video_Id,))
                    cmnts = cursor.fetchall()
                    cmnts_count = len(cmnts)
                    cmnts_count = number_format(cmnts_count)

                    sql_sound_query = """select * from sound where sound_id = %s"""
                    cursor.execute(sql_sound_query, (Sound_Id,))
                    sound_info = cursor.fetchall()

                    for sound in sound_info:
                        mp3 = sound[8]
                        Sound_Name= sound[1]
                        Description = sound[2]
                        Thum = sound[3]
                        Created = sound[6]


                    for userdata in user_prof:
                        user_info = {
                            "Full_Name": userdata[4],
                            "User_Name": userdata[2],
                            "Profile_Pic": userdata[6],
                            "Blocked": userdata[7],
                            "Verified": userdata[3]
                        }

                        a = {
                            "UID": row[1],
                            "User_Info":user_info,
                            "count": {
                                "like_count": like_count,
                                "video_comment_count": cmnts_count
                            },
                            "sound":{
                                "id": Sound_Id,
                                "audio_path": {
                                    "mp3": mp3
                                },
                                "sound_name": Sound_Name,
                                "description": Description,
                                "thum": Thum,
                                "sound_created": Created
                            },
                            "Liked": liked,
                            "Saved": Saved,
                            "Video_Id": row[12],
                            "Description": row[2],
                            "Sound_Id": row[7],
                            "Sections": row[6],
                            "Video_Thum": row[4],
                            "Video_Url": row[3],
                            "Privacy_Type": row[8],
                            "Allow_Comment": row[9],
                            "Allow_Duet": row[10],
                            "Views":row[5],
                            "Created":row[11]
                        }
                        output.append(a)

            sorteddata = sorted(
                output,
                key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
            )

            i = 5
            j = 0
            while i < len(sorteddata) and j < len(sorted_ads):
                sorteddata.insert(i, sorted_ads[j])
                i = i + (5 + 1)
                j = j + 1

            conn.commit()
            cursor.close()
            return jsonify({
                "msg":sorteddata[:200]
            })
    else:
        sortefollowvideos = []
        sql_selectfollowings_query = """select * from follow_users where uid = %s"""
        cursor.execute(sql_selectfollowings_query, (Uid,))
        followingList = cursor.fetchall()
        following_len = len(followingList)
        if following_len == 0:
            return jsonify({
                "msg":[]
            })
        else:
            for user in followingList:
                UID = user[2]
                sql_selectVideo_query = """SELECT * FROM videos WHERE uid = %s AND Privacy_Type = %s"""
                cursor.execute(sql_selectVideo_query, (UID,privacy_type))
                videosList = cursor.fetchall()

                videos_len = len(videosList)
                if videos_len == 0:
                    sortefollowvideos = []
                else:
                    output = []
                    for row in videosList:
                        UID = row[1]
                        Video_Id = row[12]
                        Sound_Id = row[7]
                        sql_select_query = """select * from users where uid = %s"""
                        cursor.execute(sql_select_query, (UID,))
                        user_prof = cursor.fetchall()

                        sql_like_query = """select * from video_like_dislike where video_id = %s"""
                        cursor.execute(sql_like_query, (Video_Id,))
                        likes = cursor.fetchall()
                        like_count = len(likes)
                        like_count = number_format(like_count)

                        sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                        cursor.execute(sql_liked_query, (Video_Id, Uid))
                        like_status = cursor.fetchall()

                        if len(like_status) == 0:
                            liked = False
                        else:
                            liked = True

                        sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                        cursor.execute(sql_saved_query, (Video_Id, Uid))
                        saved_status = cursor.fetchall()

                        if len(saved_status) == 0:
                            Saved = False
                        else:
                            Saved = True

                        sql_cmnt_query = """select * from video_comment where video_id = %s"""
                        cursor.execute(sql_cmnt_query, (Video_Id,))
                        cmnts = cursor.fetchall()
                        cmnts_count = len(cmnts)
                        cmnts_count = number_format(cmnts_count)

                        sql_sound_query = """select * from sound where sound_id = %s"""
                        cursor.execute(sql_sound_query, (Sound_Id,))
                        sound_info = cursor.fetchall()
                        global f_mp3
                        global f_Sound_Name
                        global f_Description
                        global f_Thum
                        global f_Created
                        for sound in sound_info:
                            f_mp3 = sound[8]
                            f_Sound_Name = sound[1]
                            f_Description = sound[2]
                            f_Thum = sound[3]
                            f_Created = sound[6]

                        for userdata in user_prof:
                            user_info = {
                                "Full_Name": userdata[4],
                                "User_Name": userdata[2],
                                "Profile_Pic": userdata[6],
                                "Blocked": userdata[7],
                                "Verified": userdata[3]
                            }

                            a = {
                                "UID": row[1],
                                "User_Info": user_info,
                                "count": {
                                    "like_count": like_count,
                                    "video_comment_count": cmnts_count
                                },
                                "sound": {
                                    "id": Sound_Id,
                                    "audio_path": {
                                        "mp3": f_mp3
                                    },
                                    "sound_name": f_Sound_Name,
                                    "description": f_Description,
                                    "thum": f_Thum,
                                    "sound_created": f_Created
                                },
                                "Liked": liked,
                                "Saved": Saved,
                                "Video_Id": row[12],
                                "Description": row[2],
                                "Sound_Id": row[7],
                                "Sections": row[6],
                                "Video_Thum": row[4],
                                "Video_Url": row[3],
                                "Privacy_Type": row[8],
                                "Allow_Comment": row[9],
                                "Allow_Duet": row[10],
                                "Views": row[5],
                                "Created": row[11]
                            }
                            output.append(a)
                    sortefollowvideos
                    sortefollowvideos = sorted(
                        output,
                        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
                    )
            conn.commit()
            cursor.close()
            return jsonify({
                "msg":sortefollowvideos[:200]
            })


@app.route('/getmyallvideos', methods=['POST'])
def getmyvideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    My_Uid = data.get('My_Uid', '')
    privacy_type = "public"

    sql_select_query = """select * from users where UID = %s"""
    cursor.execute(sql_select_query, (Uid,))
    record = cursor.fetchall()

    sql_selectfollowings_query = """select * from follow_users where uid = %s"""
    cursor.execute(sql_selectfollowings_query, (Uid,))
    followingList = cursor.fetchall()
    following_len = len(followingList)
    following_len = number_format(following_len)

    sql_selectfollowings_query = """select * from follow_users where followed_uid = %s"""
    cursor.execute(sql_selectfollowings_query, (Uid,))
    followersList = cursor.fetchall()
    follower_len = len(followersList)
    follower_len = number_format(follower_len)

    sql_selectfollowings_status_query = """select * from follow_users where uid = %s and followed_uid = %s """
    cursor.execute(sql_selectfollowings_status_query, (My_Uid, Uid))
    followingstatus = cursor.fetchall()
    following_status = len(followingstatus)
    if following_status == 0:
        follow_status = "follow"
    else:
        follow_status = "following"

    user_data = []
    for row in record:
        user_data  = {
            "Uid": row[1],
            "Full_Name": row[4],
            "Bio": row[5],
            "User_Name": row[2],
            "Email": row[14],
            "Profile_Pic": row[6],
            "Blocked": row[7],
            "Verified": row[3],
            "Created": row[12],
            "Following": following_len,
            "Follower": follower_len,
            "Total_Likes": row[13],
            "Follow_Status": follow_status
        }

    sql_selectVideo_query = """select * from videos where uid = %s"""
    cursor.execute(sql_selectVideo_query, (Uid,))
    videosList = cursor.fetchall()

    videos_len = len(videosList)
    if videos_len == 0:
        sortedmyvideos = []
    else:
        output = []
        for row in videosList:
            UID = row[1]
            Video_Id = row[12]
            Sound_Id = row[7]
            sql_select_query = """select * from users where uid = %s"""
            cursor.execute(sql_select_query, (UID,))
            user_prof = cursor.fetchall()

            sql_like_query = """select * from video_like_dislike where video_id = %s"""
            cursor.execute(sql_like_query, (Video_Id,))
            likes = cursor.fetchall()
            like_count = len(likes)
            like_count = number_format(like_count)

            sql_cmnt_query = """select * from video_comment where video_id = %s"""
            cursor.execute(sql_cmnt_query, (Video_Id,))
            cmnts = cursor.fetchall()
            cmnts_count = len(cmnts)
            cmnts_count = number_format(cmnts_count)

            sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
            cursor.execute(sql_liked_query, (Video_Id, My_Uid))
            like_status = cursor.fetchall()
            likeds = len(like_status)
            if likeds == 0:
                liked = False
            else:
                liked = True

            sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
            cursor.execute(sql_saved_query, (Video_Id, My_Uid))
            saved_status = cursor.fetchall()
            saved = len(saved_status)
            if saved == 0:
                Saved = False
            else:
                Saved = True

            sql_sound_query = """select * from sound where sound_id = %s"""
            cursor.execute(sql_sound_query, (Sound_Id,))
            sound_info = cursor.fetchall()

            for sound in sound_info:
                mp3 = sound[8]
                Sound_Name= sound[1]
                Description = sound[2]
                Thum = sound[3]
                Created = sound[6]


            for userdata in user_prof:
                user_info = {
                    "Full_Name": userdata[4],
                    "User_Name": userdata[2],
                    "Profile_Pic": userdata[6],
                    "Blocked": userdata[7],
                    "Verified": userdata[3]
                }

                a = {
                    "UID": row[1],
                    "User_Info":user_info,
                    "count": {
                        "Total_View":row[5],
                        "like_count": like_count,
                        "video_comment_count": cmnts_count
                    },
                    "sound":{
                        "id": Sound_Id,
                        "audio_path": {
                            "mp3": mp3
                        },
                        "sound_name": Sound_Name,
                        "description": Description,
                        "thum": Thum,
                        "sound_created": Created
                    },
                    "Liked": liked,
                    "Saved": Saved,
                    "Video_Id": row[12],
                    "Description": row[2],
                    "Sound_Id": row[7],
                    "Sections": row[6],
                    "Video_Thum": row[4],
                    "Video_Url": row[3],
                    "Privacy_Type": row[8],
                    "Allow_Comment": row[9],
                    "Allow_Duet": row[10],
                    "Views":row[5],
                    "Created":row[11]
                }
                output.append(a)

        sortedmyvideos = sorted(
            output,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    # liked videos
    sql_selectlikedVideo_query = """select * from video_like_dislike where uid = %s"""
    cursor.execute(sql_selectlikedVideo_query, (Uid,))
    likedvideosList = cursor.fetchall()

    liked_videos_len = len(likedvideosList)
    if liked_videos_len == 0:
        sortedlikedvideos = []
    else:
        output1 = []
        for row in likedvideosList:
            Video_Id = row[1]

            sql_selectVideo_query = """select * from videos where video_id = %s"""
            cursor.execute(sql_selectVideo_query, (Video_Id,))
            videosListLiked = cursor.fetchall()

            videos_len = len(videosListLiked)
            if videos_len == 0:
                sortedlikedvideos = []
            else:
                for row in videosListLiked:
                    UID = row[1]
                    Video_Id = row[12]
                    Sound_Id = row[7]
                    sql_select_query = """select * from users where uid = %s"""
                    cursor.execute(sql_select_query, (UID,))
                    user_prof = cursor.fetchall()

                    sql_like_query = """select * from video_like_dislike where video_id = %s"""
                    cursor.execute(sql_like_query, (Video_Id,))
                    likes = cursor.fetchall()
                    like_count = len(likes)
                    like_count = number_format(like_count)

                    sql_cmnt_query = """select * from video_comment where video_id = %s"""
                    cursor.execute(sql_cmnt_query, (Video_Id,))
                    cmnts = cursor.fetchall()
                    cmnts_count = len(cmnts)
                    cmnts_count = number_format(cmnts_count)

                    sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                    cursor.execute(sql_liked_query, (Video_Id, My_Uid))
                    like_status = cursor.fetchall()
                    likeds = len(like_status)
                    if likeds == 0:
                        liked = False
                    else:
                        liked = True

                    sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                    cursor.execute(sql_saved_query, (Video_Id, My_Uid))
                    saved_status = cursor.fetchall()
                    saved = len(saved_status)
                    if saved == 0:
                        Saved = False
                    else:
                        Saved = True

                    sql_sound_query = """select * from sound where sound_id = %s"""
                    cursor.execute(sql_sound_query, (Sound_Id,))
                    sound_info = cursor.fetchall()

                    for sound in sound_info:
                        mp3 = sound[8]
                        Sound_Name = sound[1]
                        Description = sound[2]
                        Thum = sound[3]
                        Created = sound[6]

                    for userdata in user_prof:
                        user_info = {
                            "Full_Name": userdata[4],
                            "User_Name": userdata[2],
                            "Profile_Pic": userdata[6],
                            "Blocked": userdata[7],
                            "Verified": userdata[3]
                        }

                        a = {
                            "UID": row[1],
                            "User_Info": user_info,
                            "count": {
                                "Total_View": row[5],
                                "like_count": like_count,
                                "video_comment_count": cmnts_count
                            },
                            "sound": {
                                "id": Sound_Id,
                                "audio_path": {
                                    "mp3": mp3
                                },
                                "sound_name": Sound_Name,
                                "description": Description,
                                "thum": Thum,
                                "sound_created": Created
                            },
                            "Liked": liked,
                            "Saved": Saved,
                            "Video_Id": row[12],
                            "Description": row[2],
                            "Sound_Id": row[7],
                            "Sections": row[6],
                            "Video_Thum": row[4],
                            "Video_Url": row[3],
                            "Privacy_Type": row[8],
                            "Allow_Comment": row[9],
                            "Allow_Duet": row[10],
                            "Views": row[5],
                            "Created": row[11]
                        }
                        output1.append(a)

        sortedlikedvideos = sorted(
            output1,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    # saved videos
    sql_selectlikedVideo_query = """select * from saved_videos where uid = %s"""
    cursor.execute(sql_selectlikedVideo_query, (Uid,))
    savedvideosList = cursor.fetchall()

    liked_videos_len = len(savedvideosList)
    if liked_videos_len == 0:
        sortedsavedvideos = []
    else:
        output1 = []
        for row in savedvideosList:
            Video_Id = row[2]

            sql_selectVideo_query = """select * from videos where video_id = %s"""
            cursor.execute(sql_selectVideo_query, (Video_Id,))
            videosListLiked = cursor.fetchall()

            videos_len = len(videosListLiked)
            if videos_len == 0:
                sortedsavedvideos = []
            else:
                for row in videosListLiked:
                    UID = row[1]
                    Video_Id = row[12]
                    Sound_Id = row[7]
                    sql_select_query = """select * from users where uid = %s"""
                    cursor.execute(sql_select_query, (UID,))
                    user_prof = cursor.fetchall()

                    sql_like_query = """select * from video_like_dislike where video_id = %s"""
                    cursor.execute(sql_like_query, (Video_Id,))
                    likes = cursor.fetchall()
                    like_count = len(likes)
                    like_count = number_format(like_count)

                    sql_cmnt_query = """select * from video_comment where video_id = %s"""
                    cursor.execute(sql_cmnt_query, (Video_Id,))
                    cmnts = cursor.fetchall()
                    cmnts_count = len(cmnts)
                    cmnts_count = number_format(cmnts_count)

                    sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                    cursor.execute(sql_liked_query, (Video_Id, My_Uid))
                    like_status = cursor.fetchall()
                    likeds = len(like_status)
                    if likeds == 0:
                        liked = False
                    else:
                        liked = True

                    sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                    cursor.execute(sql_saved_query, (Video_Id, My_Uid))
                    saved_status = cursor.fetchall()
                    saved = len(saved_status)
                    if saved == 0:
                        Saved = False
                    else:
                        Saved = True

                    sql_sound_query = """select * from sound where sound_id = %s"""
                    cursor.execute(sql_sound_query, (Sound_Id,))
                    sound_info = cursor.fetchall()

                    for sound in sound_info:
                        mp3 = sound[8]
                        Sound_Name = sound[1]
                        Description = sound[2]
                        Thum = sound[3]
                        Created = sound[6]

                    for userdata in user_prof:
                        user_info = {
                            "Full_Name": userdata[4],
                            "User_Name": userdata[2],
                            "Profile_Pic": userdata[6],
                            "Blocked": userdata[7],
                            "Verified": userdata[3]
                        }

                        a = {
                            "UID": row[1],
                            "User_Info": user_info,
                            "count": {
                                "Total_View": row[5],
                                "like_count": like_count,
                                "video_comment_count": cmnts_count
                            },
                            "sound": {
                                "id": Sound_Id,
                                "audio_path": {
                                    "mp3": mp3
                                },
                                "sound_name": Sound_Name,
                                "description": Description,
                                "thum": Thum,
                                "sound_created": Created
                            },
                            "Liked": liked,
                            "Saved": Saved,
                            "Video_Id": row[12],
                            "Description": row[2],
                            "Sound_Id": row[7],
                            "Sections": row[6],
                            "Video_Thum": row[4],
                            "Video_Url": row[3],
                            "Privacy_Type": row[8],
                            "Allow_Comment": row[9],
                            "Allow_Duet": row[10],
                            "Views": row[5],
                            "Created": row[11]
                        }
                        output1.append(a)

        sortedsavedvideos = sorted(
            output1,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    conn.commit()
    cursor.close()
    return jsonify({
        "Saved_Videos": sortedsavedvideos,
        "User_data": user_data,
        "My_Videos": sortedmyvideos,
        "Liked_Videos": sortedlikedvideos
    })

@app.route('/discoversection', methods=['POST'])
def getdiscoversection():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')

    sql_discoverysection_query = """select * from discover_section"""
    cursor.execute(sql_discoverysection_query,)
    discoveryList = cursor.fetchall()

    hastagList = []
    for row in discoveryList:
        a = {
            "hastag":row[1],
            "created":row[2],
            "section_id":row[3],
            "videos_id":row[4]
        }
        hastagList.append(a)

    sortedhastags = sorted(
        hastagList,
        key=lambda x: datetime.strptime(x['created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )

    hastag_len = len(sortedhastags)
    if hastag_len > 20:
        hastag_len = 20

    hastags = [ sub['hastag'] for sub in sortedhastags ]
    output = []

    sorted_disc_videos = [
        {
            "banner_images": [
                "https://cdn4.singleinterface.com/files/outlet/outlet_facebook_images/outlet_cover_photo/34404/Ultimate_Savings_Banner_851x315px_compressor_png.png",
                "https://indiadesire.com/images/websitetopbanner-108042015.jpg",
                "https://cdn4.singleinterface.com/files/outlet/outlet_facebook_images/outlet_cover_photo/34404/Ultimate_Savings_Banner_851x315px_compressor_png.png",
                "https://indiadesire.com/images/websitetopbanner-108042015.jpg"
            ]
        }
    ]
    for i in range (0, hastag_len):
        hastag = hastags[i]
        sql_sectionVideo_query = """SELECT * FROM discover_section WHERE section_name = %s"""
        cursor.execute(sql_sectionVideo_query, (hastag,))
        videosList = cursor.fetchall()
        for sectionsvid in videosList:
            videosid = sectionsvid[4]
            x = videosid.split(",")
            for i in range(0, len(x)):
                vid = x[i]
                sql_selectVideo_query = """select * from videos where video_id = %s"""
                cursor.execute(sql_selectVideo_query, (vid,))
                videosList = cursor.fetchall()

                videos_len = len(videosList)
                if videos_len == 0:
                    sorteddata = []
                else:
                    for row in videosList:
                        UID = row[1]
                        Video_Id = row[12]
                        Sound_Id = row[7]
                        sql_select_query = """select * from users where uid = %s"""
                        cursor.execute(sql_select_query, (UID,))
                        user_prof = cursor.fetchall()

                        sql_like_query = """select * from video_like_dislike where video_id = %s"""
                        cursor.execute(sql_like_query, (Video_Id,))
                        likes = cursor.fetchall()
                        like_count = len(likes)
                        like_count = number_format(like_count)

                        sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                        cursor.execute(sql_liked_query, (Video_Id, Uid))
                        like_status = cursor.fetchall()
                        likeds = len(like_status)
                        if likeds == 0:
                            liked = False
                        else:
                            liked = True

                        sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                        cursor.execute(sql_saved_query, (Video_Id, Uid))
                        saved_status = cursor.fetchall()
                        saved = len(saved_status)
                        if saved == 0:
                            Saved = False
                        else:
                            Saved = True

                        sql_cmnt_query = """select * from video_comment where video_id = %s"""
                        cursor.execute(sql_cmnt_query, (Video_Id,))
                        cmnts = cursor.fetchall()
                        cmnts_count = len(cmnts)
                        cmnts_count = number_format(cmnts_count)

                        sql_sound_query = """select * from sound where sound_id = %s"""
                        cursor.execute(sql_sound_query, (Sound_Id,))
                        sound_info = cursor.fetchall()
                        for sound in sound_info:
                            mp3 = sound[8]
                            Sound_Name = sound[1]
                            Description = sound[2]
                            Thum = sound[3]
                            Created = sound[6]

                        for userdata in user_prof:
                            user_info = {
                                "Full_Name": userdata[4],
                                "User_Name": userdata[2],
                                "Profile_Pic": userdata[6],
                                "Blocked": userdata[7],
                                "Verified": userdata[3]
                            }

                            a = {
                                "UID": row[1],
                                "User_Info": user_info,
                                "count": {
                                    "like_count": like_count,
                                    "video_comment_count": cmnts_count
                                },
                                "sound": {
                                    "id": Sound_Id,
                                    "audio_path": {
                                        "mp3": mp3
                                    },
                                    "sound_name": Sound_Name,
                                    "description": Description,
                                    "thum": Thum,
                                    "sound_created": Created
                                },
                                "Liked": liked,
                                "Saved": Saved,
                                "Video_Id": row[12],
                                "Description": row[2],
                                "Sound_Id": row[7],
                                "Sections": row[6],
                                "Video_Thum": row[4],
                                "Video_Url": row[3],
                                "Privacy_Type": row[8],
                                "Allow_Comment": row[9],
                                "Allow_Duet": row[10],
                                "Views": row[5],
                                "Created": row[11]
                            }
                            output.append(a)

        sorteddata = sorted(
            output,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )
        output = []
        if len(sorteddata) > 0:
            b = {
                "section_name":hastag,
                "section_videos":sorteddata
            }
            sorteddata = []
            sorted_disc_videos.append(b)

    return jsonify({
        "msg":sorted_disc_videos
    })

@app.route('/search', methods=['POST'])
def getsearchuserresult():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Text = data.get('Text', '')
    Text = "%"+Text+"%"
    userlist=[]
    sql_discoverysection_query = """SELECT * FROM users WHERE username LIKE %s OR fullname LIKE %s"""
    cursor.execute(sql_discoverysection_query,(Text,Text))
    search_user_List = cursor.fetchall()
    userlen = len(search_user_List)
    if userlen == 0:
        userlist = []
    else:
        for userdata in search_user_List:
            a = {
                "Full_Name": userdata[4],
                "User_Name": userdata[2],
                "Profile_Pic": userdata[6],
                "Blocked": userdata[7],
                "Verified": userdata[3],
                "Uid": userdata[1]
            }
            userlist.append(a)

    videosList = []
    sql_discoverysection_query = """SELECT * FROM videos WHERE description LIKE %s OR section LIKE %s"""
    cursor.execute(sql_discoverysection_query, (Text, Text))
    search_video_List = cursor.fetchall()
    videolen = len(search_video_List)
    output = []
    if videolen == 0:
        videolist = []
    else:
        for videodata in search_video_List:
            vid = videodata[12]
            sql_selectVideo_query = """select * from videos where video_id = %s"""
            cursor.execute(sql_selectVideo_query, (vid,))
            videosList = cursor.fetchall()

            for row in videosList:
                UID = row[1]
                Video_Id = row[12]
                Sound_Id = row[7]
                sql_select_query = """select * from users where uid = %s"""
                cursor.execute(sql_select_query, (UID,))
                user_prof = cursor.fetchall()

                sql_like_query = """select * from video_like_dislike where video_id = %s"""
                cursor.execute(sql_like_query, (Video_Id,))
                likes = cursor.fetchall()
                like_count = len(likes)
                like_count = number_format(like_count)

                sql_cmnt_query = """select * from video_comment where video_id = %s"""
                cursor.execute(sql_cmnt_query, (Video_Id,))
                cmnts = cursor.fetchall()
                cmnts_count = len(cmnts)
                cmnts_count = number_format(cmnts_count)

                sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
                cursor.execute(sql_liked_query, (Video_Id, Uid))
                like_status = cursor.fetchall()
                likeds = len(like_status)
                if likeds == 0:
                    liked = False
                else:
                    liked = True

                sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
                cursor.execute(sql_saved_query, (Video_Id, Uid))
                saved_status = cursor.fetchall()
                saved = len(saved_status)
                if saved == 0:
                    Saved = False
                else:
                    Saved = True

                sql_sound_query = """select * from sound where sound_id = %s"""
                cursor.execute(sql_sound_query, (Sound_Id,))
                sound_info = cursor.fetchall()

                for sound in sound_info:
                    mp3 = sound[8]
                    Sound_Name = sound[1]
                    Description = sound[2]
                    Thum = sound[3]
                    Created = sound[6]

                for userdata in user_prof:
                    user_info = {
                        "Full_Name": userdata[4],
                        "User_Name": userdata[2],
                        "Profile_Pic": userdata[6],
                        "Blocked": userdata[7],
                        "Verified": userdata[3]
                    }

                    a = {
                        "UID": row[1],
                        "User_Info": user_info,
                        "count": {
                            "like_count": like_count,
                            "video_comment_count": cmnts_count
                        },
                        "sound": {
                            "id": Sound_Id,
                            "audio_path": {
                                "mp3": mp3
                            },
                            "sound_name": Sound_Name,
                            "description": Description,
                            "thum": Thum,
                            "sound_created": Created
                        },
                        "Liked": liked,
                        "Saved": Saved,
                        "Video_Id": row[12],
                        "Description": row[2],
                        "Sound_Id": row[7],
                        "Sections": row[6],
                        "Video_Thum": row[4],
                        "Video_Url": row[3],
                        "Privacy_Type": row[8],
                        "Allow_Comment": row[9],
                        "Allow_Duet": row[10],
                        "Views": row[5],
                        "Created": row[11]
                    }
                    output.append(a)

            videosList = sorted(
                output,
                key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
            )
    conn.commit()
    cursor.close()
    return jsonify({
        "users": userlist,
        "videos":videosList
    })


@app.route('/viewupdate', methods=['POST'])
def updateviews():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')

    sql_selectVideo_query = """select * from videos where video_id = %s"""
    cursor.execute(sql_selectVideo_query, (Video_Id,))
    videodata = cursor.fetchall()
    for tview in videodata:
        view = tview[5]
        updated_view = int(view) + 1

        sql_update_view = """Update videos set view = %s where video_id = %s"""
        insertdata = (updated_view, Video_Id)
        try:
            cursor.execute(sql_update_view, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


    conn.commit()
    cursor.close()
    return "view update succesfully"


@app.route('/getcomments', methods=['POST'])
def getcomments():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    sql_select_query = """SELECT * FROM video_comment WHERE video_id = %s"""
    cursor.execute(sql_select_query, (Video_Id,))
    comments = cursor.fetchall()
    comment_data = []
    for cmnt in comments:
        uid = str(cmnt[2])

        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (uid,))
        user_prof = cursor.fetchall()

        for userdata in user_prof:
            a = {
                "Comment": cmnt[3],
                "Created": cmnt[4],
                "Uid": cmnt[2],
                "user_info" : {
                "Full_Name": userdata[4],
                "User_Name": userdata[2],
                "Profile_Pic": userdata[6],
                "Verified": userdata[3]
                }
            }
            comment_data.append(a)

    sorteddata = sorted(
        comment_data,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )
    conn.commit()
    cursor.close()
    return jsonify({
        "msg" : sorteddata
    })


@app.route('/getfollowers', methods=['POST'])
def getfollowers():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    data = request.get_json()
    Uid = data.get('Uid', '')
    My_Uid = data.get('My_Uid', '')
    cursor = conn.cursor()
    sql_select_followers = """SELECT * FROM follow_users WHERE followed_uid = %s"""
    cursor.execute(sql_select_followers, (Uid,))
    followers = cursor.fetchall()

    followers_list = []
    for follower_uid in followers:
        uid = follower_uid[1]
        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (uid,))
        user_prof = cursor.fetchall()

        sql_follow_back_query = """select * from follow_users where uid = %s and followed_uid = %s"""
        cursor.execute(sql_follow_back_query, (My_Uid,uid))
        fback_status = cursor.fetchall()
        status = len(fback_status)
        if status == 0:
            following = False
        else:
            following = True

        for userdata in user_prof:
            a = {
                "Created": follower_uid[3],
                "user_info": {
                    "Full_Name": userdata[4],
                    "User_Name": userdata[2],
                    "Profile_Pic": userdata[6],
                    "Verified": userdata[3],
                    "Uid":userdata[1],
                    "following_status":following
                }
            }
            followers_list.append(a)

    sorteddata = sorted(
        followers_list,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )
    conn.commit()
    cursor.close()
    return jsonify({
        "msg": sorteddata
    })


@app.route('/getfollowing', methods=['POST'])
def getfollowings():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    data = request.get_json()
    Uid = data.get('Uid', '')
    My_Uid = data.get('My_Uid', '')
    cursor = conn.cursor()
    sql_select_followers = """SELECT * FROM follow_users WHERE uid = %s"""
    cursor.execute(sql_select_followers, (Uid,))
    following = cursor.fetchall()

    followings_list = []
    for following_uid in following:
        uid = following_uid[2]
        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (uid,))
        user_prof = cursor.fetchall()

        sql_follow_back_query = """select * from follow_users where uid = %s and followed_uid = %s"""
        cursor.execute(sql_follow_back_query, (My_Uid, uid))
        fback_status = cursor.fetchall()
        status = len(fback_status)
        if status == 0:
            following = False
        else:
            following = True

        for userdata in user_prof:
            a = {
                "Created": following_uid[3],
                "user_info": {
                    "Full_Name": userdata[4],
                    "User_Name": userdata[2],
                    "Profile_Pic": userdata[6],
                    "Verified": userdata[3],
                    "Uid":userdata[1],
                    "following_status":following
                }
            }
            followings_list.append(a)

    sorteddata = sorted(
        followings_list,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )
    conn.commit()
    cursor.close()
    return jsonify({
        "msg": sorteddata
    })



@app.route('/save_videos', methods=['POST'])
def savevideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    Action = data.get('Action', '')
    status = int(Action)
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    if status == 1:
        sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
        mycursor.execute(sql_saved_query, (Video_Id, Uid))
        saved_status = mycursor.fetchall()

        status = len(saved_status)
        if status == 0:
            save_video = (
                "INSERT INTO saved_videos(uid,video_id, created, action)"
                "VALUES (%s, %s, %s, %s)"
            )
            insertdata = (Uid, Video_Id, Created_Date, Action)

            try:
                mycursor.execute(save_video, insertdata)

                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))

            conn.commit()
            mycursor.close()
            return "video saved"
        else:
            return "already saved"

    else:
        unsave_video = (
            "DELETE FROM saved_videos WHERE uid = %s AND video_id = %s"
        )
        removedata = (Uid, Video_Id)

        try:
            mycursor.execute(unsave_video, removedata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        conn.commit()
        mycursor.close()

        return "video unsaved"


@app.route('/Add_Message', methods=['POST'])
def addmessage():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Reciever_Uid = data.get('Reciever_Uid', '')
    Msg = data.get('Msg', '')
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    sql_select_query = """select * from chat_table where my_uid = %s and reciever_uid = %s"""
    mycursor.execute(sql_select_query, (Uid,Reciever_Uid))
    status = mycursor.fetchall()

    if len(status) == 0:
        insert_notification = (
            "INSERT INTO chat_table(my_uid,reciever_uid,created,latest_message)"
            "VALUES (%s, %s, %s, %s)"
        )
        insertdata = (Uid, Reciever_Uid, Created_Date, Msg)

        try:
            mycursor.execute(insert_notification, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        insert_notification = (
            "INSERT INTO chat_table(my_uid,reciever_uid,created,latest_message)"
            "VALUES (%s, %s, %s, %s)"
        )
        insertdata = (Reciever_Uid, Uid, Created_Date, Msg)

        try:
            mycursor.execute(insert_notification, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        sql_get_msg = """select * from chat_table where my_uid = %s """
        mycursor.execute(sql_get_msg, (Uid,))
        msg_list = mycursor.fetchall()
        msglist = []
        for msg in msg_list:
            user_info = msg[2]

            sql_get_usrinfo = """select * from users where UID = %s"""
            mycursor.execute(sql_get_usrinfo, (user_info,))
            userdata = mycursor.fetchall()
            for userdetail in userdata:
                a = {
                    "User_Name":userdetail[2],
                    "Profile_Pic":userdetail[6],
                    "Latest_MSg":msg[4],
                    "Effected_Uid":userdetail[1],
                    "Created": msg[3]
                }
                msglist.append(a)
        sortedmstlist = sorted(
            msglist,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

        conn.commit()
        cursor.close()
        return jsonify({
            "msg":sortedmstlist
        })


    else:
        sql_update_msg = """Update chat_table set created = %s, latest_message = %s where my_uid = %s and reciever_uid = %s"""
        insertdata = (Created_Date, Msg, Uid , Reciever_Uid)
        try:
            mycursor.execute(sql_update_msg, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        sql_update_msg = """Update chat_table set created = %s, latest_message = %s where my_uid = %s and reciever_uid = %s"""
        insertdata = (Created_Date, Msg, Reciever_Uid, Uid)
        try:
            mycursor.execute(sql_update_msg, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        sql_get_msg = """select * from chat_table where my_uid = %s """
        mycursor.execute(sql_get_msg, (Uid,))
        msg_list = mycursor.fetchall()
        msglist = []
        for msg in msg_list:
            user_info = msg[2]

            sql_get_usrinfo = """select * from users where UID = %s"""
            mycursor.execute(sql_get_usrinfo, (user_info,))
            userdata = mycursor.fetchall()
            for userdetail in userdata:
                a = {
                    "User_Name": userdetail[2],
                    "Profile_Pic": userdetail[6],
                    "Latest_MSg": msg[4],
                    "Effected_Uid": userdetail[1],
                    "Created": msg[3]
                }
                msglist.append(a)
        sortedmstlist = sorted(
            msglist,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

        conn.commit()
        mycursor.close()
        return jsonify({
            "msg":sortedmstlist
        })



@app.route('/get_notifications', methods=['POST'])
def getnotifications():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    x = datetime.now()

    noti_list = []
    sql_get_msg = """SELECT * FROM notification WHERE effected_uid = %s"""
    mycursor.execute(sql_get_msg, (Uid,))
    notifications_list = mycursor.fetchall()
    for noti in notifications_list:
        sender_uid = noti[1]
        type = noti[3]
        video_id = noti[4]

        sql_get_senderinfo = """select * from users where UID = %s"""
        mycursor.execute(sql_get_senderinfo, (sender_uid,))
        senderdata = mycursor.fetchall()

        for senderdetail in senderdata:
            sql_get_myinfo = """select * from users where UID = %s"""
            mycursor.execute(sql_get_myinfo, (Uid,))
            recieverdata = mycursor.fetchall()

            for recieverdetail in recieverdata:
                sql_get_video_info = """select * from videos where video_id = %s"""
                mycursor.execute(sql_get_video_info, (video_id,))
                video_data = mycursor.fetchall()
                video_url = ""
                video_thum =""
                for video in video_data:
                    video_url = video[3]
                    video_thum = video[4]
                a = {
                    "My_User_Name": recieverdetail[2],
                    "My_Profile_Pic": senderdetail[6],
                    "My_Uid": recieverdetail[1],
                    "User_Name": senderdetail[2],
                    "Full_Name": senderdetail[4],
                    "Profile_Pic": recieverdetail[6],
                    "Uid": senderdetail[1],
                    "Created": noti[5],
                    "Type":type,
                    "Video_Id":video_id,
                    "Video_Url":video_url,
                    "Video_Thum": video_thum
                }
                noti_list.append(a)

    sorted_noti_list = sorted(
        noti_list,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )

    sql_get_msg = """select * from chat_table where my_uid = %s """
    mycursor.execute(sql_get_msg, (Uid,))
    msg_list = mycursor.fetchall()
    msglist = []
    for msg in msg_list:
        user_info = msg[2]

        sql_get_usrinfo = """select * from users where UID = %s"""
        mycursor.execute(sql_get_usrinfo, (user_info,))
        userdata = mycursor.fetchall()
        for userdetail in userdata:
            a = {
                "Full_Name": userdetail[4],
                "User_Name": userdetail[2],
                "Profile_Pic": userdetail[6],
                "Latest_MSg": msg[4],
                "Effected_Uid": userdetail[1],
                "Created": msg[3]
            }
            msglist.append(a)
    sortedmstlist = sorted(
        msglist,
        key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
    )

    conn.commit()
    mycursor.close()
    return jsonify({
        "notification": sorted_noti_list[:100],
        "message":sortedmstlist
    })


@app.route('/add_reports', methods=['POST'])
def addreports():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    x = datetime.now()

    sql_video_query = """select * from videos where video_id = %s"""
    mycursor.execute(sql_video_query, (Video_Id,))
    video_info = mycursor.fetchall()
    for video in video_info:
        reports = video[15]
        total_report = int(reports)+1
        sql_update_profile = """Update videos set video_reports = %s where video_id = %s"""
        insertdata = (total_report, Video_Id)
        try:
            mycursor.execute(sql_update_profile, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


    conn.commit()
    mycursor.close()
    return jsonify({
        "status":200,
        "msg":"success"
    })


@app.route('/single_video', methods=['POST'])
def singlevideo():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')

    sql_selectVideo_query = """select * from videos where video_id = %s"""
    cursor.execute(sql_selectVideo_query, (Video_Id,))
    videosList = cursor.fetchall()

    for row in videosList:
        UID = row[1]
        Video_Id = row[12]
        Sound_Id = row[7]
        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (UID,))
        user_prof = cursor.fetchall()

        sql_like_query = """select * from video_like_dislike where video_id = %s"""
        cursor.execute(sql_like_query, (Video_Id,))
        likes = cursor.fetchall()
        like_count = len(likes)
        like_count = number_format(like_count)

        sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
        cursor.execute(sql_liked_query, (Video_Id, Uid))
        like_status = cursor.fetchall()
        likeds = len(like_status)
        if likeds == 0:
            liked = False
        else:
            liked = True

        sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
        cursor.execute(sql_saved_query, (Video_Id, Uid))
        saved_status = cursor.fetchall()
        saved = len(saved_status)
        if saved == 0:
            Saved = False
        else:
            Saved = True

        sql_cmnt_query = """select * from video_comment where video_id = %s"""
        cursor.execute(sql_cmnt_query, (Video_Id,))
        cmnts = cursor.fetchall()
        cmnts_count = len(cmnts)
        cmnts_count = number_format(cmnts_count)

        sql_sound_query = """select * from sound where sound_id = %s"""
        cursor.execute(sql_sound_query, (Sound_Id,))
        sound_info = cursor.fetchall()

        for sound in sound_info:
            mp3 = sound[8]
            Sound_Name = sound[1]
            Description = sound[2]
            Thum = sound[3]
            Created = sound[6]

        for userdata in user_prof:
            user_info = {
                "Full_Name": userdata[4],
                "User_Name": userdata[2],
                "Profile_Pic": userdata[6],
                "Blocked": userdata[7],
                "Verified": userdata[3]
            }

            return jsonify({
                "UID": row[1],
                "User_Info": user_info,
                "count": {
                    "like_count": like_count,
                    "video_comment_count": cmnts_count
                },
                "sound": {
                    "id": Sound_Id,
                    "audio_path": {
                        "mp3": mp3
                    },
                    "sound_name": Sound_Name,
                    "description": Description,
                    "thum": Thum,
                    "sound_created": Created
                },
                "Liked": liked,
                "Saved": Saved,
                "Video_Id": row[12],
                "Description": row[2],
                "Sound_Id": row[7],
                "Sections": row[6],
                "Video_Thum": row[4],
                "Video_Url": row[3],
                "Privacy_Type": row[8],
                "Allow_Comment": row[9],
                "Allow_Duet": row[10],
                "Views": row[5],
                "Created": row[11]
            })
    conn.commit()
    cursor.close()


@app.route('/user_sound', methods=['POST'])
def usersound():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Sound_Id = data.get('Sound_Id', '')

    sql_sound_query = """select * from sound where sound_id = %s"""
    cursor.execute(sql_sound_query, (Sound_Id,))
    sound_info = cursor.fetchall()
    sound_data = {}
    for sound in sound_info:
        sound_data = {
            "mp3" : sound[8],
            "Sound_Name" : sound[1],
            "Description" : sound[2],
            "Thum" : sound[3],
            "Created" : sound[6]
        }

    sql_selectVideo_query = """select * from videos where sound_id = %s"""
    cursor.execute(sql_selectVideo_query, (Sound_Id,))
    videosList = cursor.fetchall()

    videos =[]
    sorted_videos = []
    for row in videosList:
        UID = row[1]
        Video_Id = row[12]
        Sound_Id = row[7]
        sql_select_query = """select * from users where uid = %s"""
        cursor.execute(sql_select_query, (UID,))
        user_prof = cursor.fetchall()

        sql_like_query = """select * from video_like_dislike where video_id = %s"""
        cursor.execute(sql_like_query, (Video_Id,))
        likes = cursor.fetchall()
        like_count = len(likes)
        like_count = number_format(like_count)

        sql_liked_query = """select * from video_like_dislike where video_id = %s and uid = %s"""
        cursor.execute(sql_liked_query, (Video_Id, Uid))
        like_status = cursor.fetchall()
        likeds = len(like_status)
        if likeds == 0:
            liked = False
        else:
            liked = True

        sql_saved_query = """select * from saved_videos where video_id = %s and uid = %s"""
        cursor.execute(sql_saved_query, (Video_Id, Uid))
        saved_status = cursor.fetchall()
        saved = len(saved_status)
        if saved == 0:
            Saved = False
        else:
            Saved = True

        sql_cmnt_query = """select * from video_comment where video_id = %s"""
        cursor.execute(sql_cmnt_query, (Video_Id,))
        cmnts = cursor.fetchall()
        cmnts_count = len(cmnts)
        cmnts_count = number_format(cmnts_count)

        sql_sound_query = """select * from sound where sound_id = %s"""
        cursor.execute(sql_sound_query, (Sound_Id,))
        sound_info = cursor.fetchall()

        for sound in sound_info:
            mp3 = sound[8]
            Sound_Name = sound[1]
            Description = sound[2]
            Thum = sound[3]
            Created = sound[6]

        for userdata in user_prof:
            user_info = {
                "Full_Name": userdata[4],
                "User_Name": userdata[2],
                "Profile_Pic": userdata[6],
                "Blocked": userdata[7],
                "Verified": userdata[3]
            }

            a = {
                "UID": row[1],
                "User_Info": user_info,
                "count": {
                    "like_count": like_count,
                    "video_comment_count": cmnts_count
                },
                "sound": {
                    "id": Sound_Id,
                    "audio_path": {
                        "mp3": mp3
                    },
                    "sound_name": Sound_Name,
                    "description": Description,
                    "thum": Thum,
                    "sound_created": Created
                },
                "Liked": liked,
                "Saved": Saved,
                "Video_Id": row[12],
                "Description": row[2],
                "Sound_Id": row[7],
                "Sections": row[6],
                "Video_Thum": row[4],
                "Video_Url": row[3],
                "Privacy_Type": row[8],
                "Allow_Comment": row[9],
                "Allow_Duet": row[10],
                "Views": row[5],
                "Created": row[11]
            }
            videos.append(a)

        sorted_videos = sorted(
            videos,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    Final_list ={
        "sound_info":sound_data,
        "Sound_videos":sorted_videos[:200]
    }

    conn.commit()
    cursor.close()
    return jsonify({
        "msg":Final_list
    })


@app.route('/off_video_post', methods=['POST'])
def offvideos():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    x = datetime.now()
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    off_video = (
        "INSERT INTO offtable(uid,video_id, created)"
        "VALUES (%s, %s, %s)"
    )
    insertdata = (Uid, Video_Id, Created_Date)

    try:
        mycursor.execute(off_video, insertdata)

        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    conn.commit()
    mycursor.close()
    return "off successfull"


@app.route('/add_admin_sound', methods=['POST'])
def addadminsound():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    x = datetime.now()
    mycursor = conn.cursor()
    data = request.get_json()
    Sound_Id = data.get('Sound_Id', '')
    Sound_Name = data.get('Sound_Name', '')
    Sound_Description = data.get('Sound_Description', '')
    Sound_Thum = data.get('Sound_Thum', '')
    Sound_Section = data.get('Sound_Section', '')
    Sound_Url = data.get('Sound_Url', '')
    Section_Name = data.get('Section_Name', '')
    Uploaded_By = "admin"
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    sql_searchsound_query = """select * from sound where sound_id = %s"""
    mycursor.execute(sql_searchsound_query, (Sound_Id,))
    soundList = mycursor.fetchall()

    sound_len = len(soundList)

    if sound_len == 0:
        insert_sound = (
            "INSERT INTO sound(sound_id,sound_name, description, thum, section, uploaded_by, created,sound_url)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        insertdata = (
            Sound_Id, Sound_Name, Sound_Description, Sound_Thum, Sound_Section, Uploaded_By, Created_Date, Sound_Url)

        try:
            # Executing the SQL command
            mycursor.execute(insert_sound, insertdata)

            # Commit your changes in the database
            conn.commit()


        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        sql_searchsection_query = """select * from sound_section where section_id = %s"""
        mycursor.execute(sql_searchsection_query, (Sound_Section,))
        sectionList = mycursor.fetchall()

        section_len = len(sectionList)

        if section_len == 0:
            insert_sound_section = (
                "INSERT INTO sound_section(section_name,created, section_id)"
                "VALUES (%s, %s, %s)"
            )
            insertdata = (
                Section_Name, Created_Date, Sound_Section)

            try:
                mycursor.execute(insert_sound_section, insertdata)
                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))


        conn.commit()
        mycursor.close()
        return "added successfull"

    else:
        conn.commit()
        mycursor.close()
        return "sound present"



@app.route('/get_admin_sound', methods=['POST'])
def adminsongs():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')

    songs = []
    final_sound_list = []
    sql_sound_sec_query = """select * from sound_section"""
    mycursor.execute(sql_sound_sec_query,)
    section_list = mycursor.fetchall()
    for seclist in section_list:
        section_name = seclist[1]
        section_id = seclist[3]

        sql_sound_sec_query = """select * from sound where section = %s and uploaded_by = %s"""
        mycursor.execute(sql_sound_sec_query, (section_id,"admin"))
        sound_list = mycursor.fetchall()
        if len(sound_list) == 0:
            print("do nothing")
        else:
            for sound in sound_list:
                sound_id = sound[7]
                sql_sound_sec_query = """select * from fav_sound where uid = %s and sound_id = %s"""
                mycursor.execute(sql_sound_sec_query, (Uid,sound_id))
                fav_list = mycursor.fetchall()

                if len(fav_list) == 0:
                    fav = False
                else:
                    fav = True
                a = {
                    "Sound_Id":sound[7],
                    "mp3" : sound[8],
                    "Sound_Name" : sound[1],
                    "Description" : sound[2],
                    "Thum" : sound[3],
                    "Fav":fav,
                    "Created" : sound[6]
                }
                songs.append(a)

            sounds_sorted = sorted(
                songs,
                key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
            )
            song_sec = {
                "Section_Name":section_name,
                "Section_songs":sounds_sorted[:100]
            }

            songs = []
            final_sound_list.append(song_sec)

    songs = []
    final_favsound_list = []
    sql_sound_sec_query = """select * from fav_sound where uid = %s"""
    mycursor.execute(sql_sound_sec_query, (Uid,))
    fav_list = mycursor.fetchall()
    for favlist in fav_list:
        sound_id = favlist[2]

        sql_sound_sec_query = """select * from sound where sound_id = %s and uploaded_by = %s"""
        mycursor.execute(sql_sound_sec_query, (sound_id, "admin"))
        sound_list = mycursor.fetchall()

        sql_sound_sec_query = """select * from fav_sound where uid = %s and sound_id = %s"""
        mycursor.execute(sql_sound_sec_query, (Uid, sound_id))
        fav_list = mycursor.fetchall()
        if len(fav_list) == 0:
            fav = False
        else:
            fav = True

        for sound in sound_list:
            a = {
                "Sound_Id":sound_id,
                "mp3": sound[8],
                "Sound_Name": sound[1],
                "Description": sound[2],
                "Thum": sound[3],
                "Fav":fav,
                "Created": sound[6]
            }
            songs.append(a)
        final_favsound_list = sorted(
            songs,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    conn.commit()
    mycursor.close()
    return jsonify({
        "fav_sound": final_favsound_list,
        "admin_sound":final_sound_list
    })


@app.route('/add_admin_videoposts', methods=['POST'])
def insertadminvideospost():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    x = datetime.now()
    data = request.get_json()
    Video_Id = data.get('Video_Id', '')
    UID = data.get('UID', '')
    Description = data.get('Description', '')
    Sound_Id = data.get('Sound_Id', '')
    Video_Thum = data.get('Video_Thum', '')
    Video_Url = data.get('Video_Url', '')
    Views = 0
    Total_Likes = 0
    Privacy_Type = data.get('Privacy_Type', '')
    Allow_Comment = data.get('Allow_Comment', '')
    Allow_Duet = data.get('Allow_Duet', '')
    Sound_Name = data.get('Sound_Name', '')
    Sound_Description = data.get('Sound_Description', '')
    Sound_Thum = data.get('Sound_Thum', '')
    Sound_Section = ""
    Sound_Url = data.get('Sound_Thum', '')
    Uploaded_By = "admin"
    Video_Reports = 0
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")

    hashtag_list = []
    for word in Description.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    Sections = ','.join(hashtag_list)

    # Preparing SQL query to INSERT a record into the database.
    insert_video = (
        "INSERT INTO videos(uid,video_id, description, sound_id, section, thum, video, privacy_type, allow_comments, allow_duet,view,created,total_likes,uploaded_by,video_reports)"
        "VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s, %s)"
    )
    insertdata = (UID, Video_Id, Description, Sound_Id, Sections, Video_Thum, Video_Url, Privacy_Type, Allow_Comment, Allow_Duet,Views,Created_Date,Total_Likes,Uploaded_By,Video_Reports)

    try:
        mycursor.execute(insert_video, insertdata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    hastag_len = len(hashtag_list)
    for i in range(0, hastag_len):
        tag = hashtag_list[i]
        hastag = tag.lower()

        sql_searchsound_query = """select * from discover_section where section_name = %s"""
        mycursor.execute(sql_searchsound_query, (hastag,))
        sectiondata = mycursor.fetchall()
        section_len = len(sectiondata)
        if section_len == 0:
            Section_Id = get_random_string("D_SECTION_", 10)
            insert_dsection = (
                "INSERT INTO discover_section(section_name,created,section_id,videos)"
                "VALUES (%s, %s, %s, %s)"
            )
            insertdata = (tag, Created_Date, Section_Id, Video_Id)

            try:
                mycursor.execute(insert_dsection, insertdata)
                conn.commit()

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))


        else:
            for videos in sectiondata:
                total_videos = videos[4]
                total_videos = total_videos+","+Video_Id
                sql_update_secvideos = """Update discover_section set videos = %s where section_name = %s"""
                insertdata = (total_videos, hastag)
                try:
                    mycursor.execute(sql_update_secvideos, insertdata)
                    conn.commit()

                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))


    sql_searchsound_query = """select * from sound where sound_id = %s"""
    mycursor.execute(sql_searchsound_query, (Sound_Id,))
    soundList = mycursor.fetchall()

    sound_len = len(soundList)

    if sound_len == 0:
        insert_sound = (
            "INSERT INTO sound(sound_id,sound_name, description, thum, section, uploaded_by, created,sound_url)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        insertdata = (
        Sound_Id,Sound_Name,Sound_Description, Sound_Thum,Sound_Section,Uploaded_By, Created_Date, Sound_Url)

        try:
            # Executing the SQL command
            mycursor.execute(insert_sound, insertdata)

            # Commit your changes in the database
            conn.commit()


        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

    conn.commit()
    mycursor.close()
    return jsonify({
        "code": 200,
        "status": "success uploading video"
    })

@app.route('/get_fav_sound', methods=['POST'])
def getfavsound():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')

    songs = []
    final_sound_list = []
    sql_sound_sec_query = """select * from fav_sound where uid = %s"""
    mycursor.execute(sql_sound_sec_query,(Uid,))
    fav_list = mycursor.fetchall()
    for favlist in fav_list:
        sound_id = favlist[2]

        sql_sound_sec_query = """select * from sound where sound_id = %s and uploaded_by = %s"""
        mycursor.execute(sql_sound_sec_query, (sound_id,"admin"))
        sound_list = mycursor.fetchall()
        for sound in sound_list:
            a = {
                "mp3" : sound[8],
                "Sound_Name" : sound[1],
                "Description" : sound[2],
                "Thum" : sound[3],
                "Created" : sound[6]
            }
            songs.append(a)
        final_sound_list = sorted(
            songs,
            key=lambda x: datetime.strptime(x['Created'], '%d:%m:%Y 	%H:%M:%S'), reverse=True
        )

    conn.commit()
    mycursor.close()
    return jsonify({
        "msg":final_sound_list
    })


@app.route('/add_fav_sound', methods=['POST'])
def favsound():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    x = datetime.now()
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Sound_Id = data.get('Sound_Id', '')
    Action = data.get('Action', '')
    Created_Date = x.strftime("%d:%m:%Y %H:%M:%S")
    action = int(Action)

    if action == 1:
        off_video = (
            "INSERT INTO fav_sound(uid,sound_id, created)"
            "VALUES (%s, %s, %s)"
        )
        insertdata = (Uid, Sound_Id, Created_Date)

        try:
            mycursor.execute(off_video, insertdata)

            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        conn.commit()
        mycursor.close()
        return "successfull add"
    else:
        delete_like = (
            "DELETE FROM fav_sound WHERE uid = %s AND sound_id = %s"
        )
        insertdata = (Uid,Sound_Id)

        try:
            mycursor.execute(delete_like, insertdata)
            conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


        conn.commit()
        mycursor.close()
        return "successfull remove"


@app.route('/delete_video', methods=['POST'])
def deletevideo():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Uid = data.get('Uid', '')
    Video_Id = data.get('Video_Id', '')


    sql_selectVideo_query = """select * from videos where video_id = %s"""
    mycursor.execute(sql_selectVideo_query, (Video_Id,))
    videosList = mycursor.fetchall()

    for row in videosList:
        video_url = row[3]
        Video_Thum = row[4]

        x = video_url.split("/")
        video_name = x[-1]
        video_file = "SelfilmVideo/"+video_name


        y = Video_Thum.split("/")
        audio_name = y[-1]
        audio_file = "SelfilmThum/"+audio_name

        import boto3
        s3 = boto3.resource('s3',
                            aws_access_key_id="AKIAITR5W77HM6TL3AFA",
                            aws_secret_access_key="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")
        obj = s3.Object("selfilmindia-hosting-mobilehub-991047198", video_file)
        response = obj.delete()

        obj1 = s3.Object("selfilmindia-hosting-mobilehub-991047198", audio_file)
        response1 = obj1.delete()

    # delete videos from videos table
    delete_video = (
        "DELETE FROM videos WHERE uid = %s AND video_id = %s"
    )
    removedata = (Uid, Video_Id)

    try:
        mycursor.execute(delete_video, removedata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    # delete likes from like table
    delete_like = (
        "DELETE FROM video_like_dislike WHERE video_id = %s"
    )
    removedata = (Video_Id,)

    try:
        mycursor.execute(delete_like, removedata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    # delete comments from comment table
    delete_comment = (
        "DELETE FROM video_comment WHERE video_id = %s"
    )
    removedata = (Video_Id,)

    try:
        mycursor.execute(delete_comment, removedata)
        conn.commit()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


    conn.commit()
    mycursor.close()
    return jsonify({
        "statusCode":200,
        "msg":"deleted successfull"
    })

@app.route('/Add_HTT_Movies', methods=['POST'])
def addhttmovies():
    # Construct connection string
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    mycursor = conn.cursor()
    data = request.get_json()
    Movie_Name = data.get('Movie_Name', '')
    Thum_Url = data.get('Thum_Url', '')
    Trailer_Url = data.get('Trailer_Url', '')
    Live_Url = data.get('Live_Url', '')
    Certificates = data.get('Certificates', '')
    Rating = data.get('Rating', '')
    Language = data.get('Language', '')
    Description = data.get('Description', '')
    Movide_Id = data.get('Movide_Id', '')
    Casts = data.get('Casts', '')

    insert_stmt = (
        "INSERT INTO users(movie_name, thumb_url, trailer_url, live_url, certificate, rating, language, description, movie_id, cast)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    insertdata = (
        Uid, Full_Name, Bio, User_Name, Email, Profile_Picture, Device, Device_Token, Blocked, Verified, Version,
        Signup_Type, Total_Likes, Created_Date)
    print (insertdata)
    try:
        # Executing the SQL command
        mycursor.execute(insert_stmt, insertdata)
        # Commit your changes in the database
        mydb.commit()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        mydb.rollback()



app.run()
