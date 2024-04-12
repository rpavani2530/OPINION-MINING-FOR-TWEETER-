from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from sklearn.externals import joblib
import random

load_index = 0
global svm_classifier

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def ChangePassword(request):
    if request.method == 'GET':
       return render(request, 'ChangePassword.html', {})

def PostTopic(request):
    if request.method == 'GET':
       return render(request, 'PostTopic.html', {})

def HomePage(request):
    if request.method == 'GET':
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        status_data = ''
        con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == user:
                    status_data = row[5]
                    break
            if status_data == 'none':
                status_data = ''   
            output = ''
            output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+user+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+status_data+'</font></td><td><font size=3 color=black>welcome : '+user+'</font></td></tr></table></br></br>'
            output+=getPostData()
            context= {'data':output}
            return render(request, 'UserScreen.html', context)

def getPostData():
    output = '<table border=1 align=center>'
    output+='<tr><th><font size=3 color=black>Username</font></th>'
    output+='<th><font size=3 color=black>Image</font></th>'
    output+='<th><font size=3 color=black>Image Name</font></th>'
    output+='<th><font size=3 color=black>Name</font></th>'
    output+='<th><font size=3 color=black>Topic</font></th>'
    output+='<th><font size=3 color=black>Description</font></th>'
    output+='<th><font size=3 color=black>View Post</font></th></tr>'

    con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM post")
        rows = cur.fetchall()
        for row in rows:
            username = row[0]
            post_id = str(row[1])
            image = row[2]
            name = row[3]
            topic = row[4]
            description = row[5]
            output+='<tr><td><font size=3 color=black>'+username+'</font></td>'
            output+='<td><img src=/static/post/'+post_id+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+image+'</font></td>'
            output+='<td><font size=3 color=black>'+name+'</font></td>'
            output+='<td><font size=3 color=black>'+topic+'</font></td>'
            output+='<td><font size=3 color=black>'+description+'</font></td>'
            output+='<td><a href=\'PostComment?id='+post_id+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
    output+="</table><br/><br/><br/><br/><br/><br/>"        
    return output

def getComments(pid):
    output = '<table border=1 align=center>'
    output+='<tr><th><font size=3 color=black>Post ID</font></th>'
    output+='<th><font size=3 color=black>Username</font></th>'
    output+='<th><font size=3 color=black>Comment</font></th>'
    output+='<th><font size=3 color=black>Rating</font></th></tr>'
    

    con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM comment where post_id='"+pid+"'")
        rows = cur.fetchall()
        for row in rows:
            pid = row[0]
            username = str(row[1])
            comment = row[2]
            rate = row[3]
            output+='<tr><td><font size=3 color=black>'+pid+'</font></td>'
            output+='<td><font size=3 color=black>'+username+'</font></td>'
            output+='<td><font size=3 color=black>'+comment+'</font></td>'
            output+='<td><font size=3 color=black>'+rate+'</font></td></tr>'
            
    output+="</table><br/><br/><br/><br/><br/><br/>"        
    return output

def PostMyComment(request):
    global load_index
    global svm_classifier
    if request.method == 'POST':
        comment = request.POST.get('comment', False)
        pid = request.POST.get('pid', False)
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        if load_index == 0:
            svm_classifier = joblib.load('svmClassifier.pkl')
            load_index = 1
        X =  [comment]
        sentiment = svm_classifier.predict(X)
        senti = sentiment[0]
        rate = 0
        if senti == 0:
            rate = random.randint(0,2)
        if senti == 1:
            rate = random.randint(3,5)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO comment(post_id,username,comment,rate) VALUES('"+pid+"','"+str(user)+"','"+comment+"','"+str(rate)+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        output = '<table align=\"center\" width=\"80\">'
        output+= '<tr><td><b>Comment</b></td><td><input type=\"text\" name=\"comment\" style=\"font-family: Comic Sans MS\" size=\"60\"></td></tr>'
        output+= '<tr><td></td><td><input type=\"hidden\" name=\"pid\" style=\"font-family: Comic Sans MS\" value='+pid+'></td></tr>'
        output+= '<tr><td></td><td><input type=\"submit\" value=\"Submit\"></td></tr></table><br/><br/>'
        output+= getComments(pid)
        context= {'data':output}
        return render(request, 'PostCommentPage.html', context)
    

def PostComment(request):
    if request.method == 'GET':
        pid = request.GET['id']
        output = '<table align=\"center\" width=\"80\">'
        output+= '<tr><td><b>Comment</b></td><td><input type=\"text\" name=\"comment\" style=\"font-family: Comic Sans MS\" size=\"60\"></td></tr>'
        output+= '<tr><td></td><td><input type=\"hidden\" name=\"pid\" style=\"font-family: Comic Sans MS\" value='+pid+'></td></tr>'
        output+= '<tr><td></td><td><input type=\"submit\" value=\"Submit\"></td></tr></table><br/><br/>'
        output+= getComments(pid)
        context= {'data':output}
        return render(request, 'PostCommentPage.html', context)


def PostMyTopic(request):
    if request.method == 'POST':
        name = request.POST.get('name', False)
        topic = request.POST.get('topic', False)
        description = request.POST.get('description', False)
        myfile = request.FILES['image']
        imagename = request.FILES['image'].name
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        count = 0

        con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select count(*) FROM post")
            rows = cur.fetchall()
            for row in rows:
                count = row[0]
        count = count + 1        

        fs = FileSystemStorage()
        filename = fs.save('C:/Python/OpinionMining/OpinionApp/static/post/'+str(count)+'.png', myfile)
      
        db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO post(username,post_id,image,name,topic,description) VALUES('"+user+"','"+str(count)+"','"+imagename+"','"+name+"','"+topic+"','"+description+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        status_data = ''
        if db_cursor.rowcount == 1:
            con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("select * FROM register")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == user:
                        status_data = row[5]
                        break
            if status_data == 'none':
                status_data = ''   
            output = ''
            output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+user+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+status_data+'</font></td><td><font size=3 color=black>welcome : '+user+'</font></td></tr></table></br></br>'
            output+=getPostData()
            context= {'data':output}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Error in post topic'}
            return render(request, 'PostTopic.html', context)
    
    
def ChangeMyPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password', False)
        user = ''
with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
                        
        db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update register set password='"+password+"' where username='"+user+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record updated")
        status_data = ''
        if db_cursor.rowcount == 1:
            con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("select * FROM register")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == user and row[1] == password:
                        status_data = row[5]
                        break
            if status_data == 'none':
                status_data = ''   
            output = ''
            output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+user+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+status_data+'</font></td><td><font size=3 color=black>welcome : '+user+'</font></td></tr></table></br></br>'
            output+=getPostData()
            context= {'data':output}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Error in updating status'}
            return render(request, 'UpdateStatus.html', context)      

def UpdateStatus(request):
    if request.method == 'GET':
       return render(request, 'UpdateStatus.html', {})

def UpdateMyStatus(request):
    if request.method == 'POST':
        status = request.POST.get('status', False)
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
                        
        db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update register set status='"+status+"' where username='"+user+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record updated")
        if db_cursor.rowcount == 1:
            output = ''
            output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+user+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+status+'</font></td><td><font size=3 color=black>welcome : '+user+'</font></td></tr></table></br></br>'
            output+=getPostData()
            context= {'data':output}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Error in updating status'}
            return render(request, 'UpdateStatus.html', context)  

def EditProfile(request):
    if request.method == 'GET':
        output = ''
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        output = ''
        username = ''
        password = ''
        contact = ''
        email = ''
        address = ''
        con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register where username='"+user+"'")
            rows = cur.fetchall()
            for row in rows:
                username = row[0]
                password = row[1]
                contact = row[2]
                email = row[3]
                address = row[4]
        output+='<tr><td><b>Username</b></td><td><input type=text name=username style=font-family: Comic Sans MS size=30 value='+username+' readonly></td></tr>'
        output+='<tr><td><b>Password</b></td><td><input type=password name=password style=font-family: Comic Sans MS size=30 value='+password+'></td></tr>'
        output+='<tr><td><b>Contact&nbsp;No</b></td><td><input type=text name=contact style=font-family: Comic Sans MS size=20 value='+contact+'></td></tr>'
        output+='<tr><td><b>Email&nbsp;ID</b></td><td><input type=text name=email style=font-family: Comic Sans MS size=40 value='+email+'></td></tr>'
        output+='<tr><td><b>Address</b></td><td><input type=text name=address style=font-family: Comic Sans MS size=60 value='+address+'></td></tr>'
        context= {'data':output}
        return render(request, 'EditProfile.html', context)    

def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      myfile = request.FILES['image']

      fs = FileSystemStorage()
      filename = fs.save('C:/Python/OpinionMining/OpinionApp/static/profiles/'+username+'.png', myfile)
      
      db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query="INSERT INTO register(username,password,contact,email,address,status) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"','none')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)

def EditMyProfile(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      myfile = request.FILES['image']

      if os.path.exists('C:/Python/OpinionMining/OpinionApp/static/profiles/'+username+'.png'):
          os.remove('C:/Python/OpinionMining/OpinionApp/static/profiles/'+username+'.png')

      fs = FileSystemStorage()
      filename = fs.save('C:/Python/OpinionMining/OpinionApp/static/profiles/'+username+'.png', myfile)
      
      db_connection = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "update register set username='"+username+"',password='"+password+"',contact='"+contact+"',email='"+email+"',address='"+address+"' where username='"+username+"'"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record updated")
      status_data = ''
      if db_cursor.rowcount == 1:
          con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
          with con:
              cur = con.cursor()
              cur.execute("select * FROM register")
              rows = cur.fetchall()
              for row in rows:
                  if row[0] == username and row[1] == password:
                      status_data = row[5]
                      break
          if status_data == 'none':
              status_data = ''            
          output = ''
          output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+username+'.png width=200 height=200></img></td>'
          output+='<td><font size=3 color=black>'+status_data+'</font></td><td><font size=3 color=black>welcome : '+username+'</font></td></tr></table></br></br>'
          output+=getPostData()
          context= {'data':output}
          return render(request, 'UserScreen.html', context)
      else:
       context= {'data':'Error in editing profile'}
       return render(request, 'EditProfile.html', context)    
        
def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        status_data = ''
        con = pymysql.connect(host='localhost',port = 3308,user = 'root', password = 'root', database = 'opinionmining',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    status = 'success'
                    status_data = row[5]
                    break
        if status_data == 'none':
            status_data = ''
        if status == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            output = ''
            output+='<table border=0 align=center width=100%><tr><td><img src=/static/profiles/'+username+'.png width=200 height=200></img></td>'
            output+='<td><font size=3 color=black>'+status_data+'</font></td><td><font size=3 color=black>welcome : '+username+'</font></td></tr></table></br></br>'
            output+=getPostData()
            context= {'data':output}
            return render(request, 'UserScreen.html', context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', contex
