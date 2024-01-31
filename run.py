from flask import Flask, render_template,redirect,url_for,session,request,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send,emit,join_room
from datetime import datetime
from flask_migrate import Migrate
import iso8601

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SECRET_KEY'] = 'your_secret_key'  
db=SQLAlchemy(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)

class users(db.Model):
    id=db.Column("id",db.Integer, primary_key=True)
    uname=db.Column(db.String(100))
    email=db.Column(db.String(100))
    password=db.Column(db.String(200))
    status=db.Column(db.String(200))
    
    

    def __init__(self,uname,email,password):
        self.uname= uname
        self.email= email
        self.password =password
        
        

class messages(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    sender_id= db.Column(db.Integer)
    receiver_id= db.Column(db.Integer)
    content=db.Column(db.String(100))
    time=db.Column(db.String(128))
    seen = db.Column(db.Boolean, default=False)



    def __init__(self,sender_id,receiver_id,content,time,seen):
        self.sender_id=sender_id
        self.receiver_id=receiver_id
        self.content=content
        self.time=time
        self.seen=False


@app.route("/")
def home():
    return render_template("home.html")    

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        
        if 'user_id' in session:
            flash('You are already logged in.', 'info')
            return redirect(url_for('chatpage')) 
        else:
            user = users.query.filter_by(email=email,password=password).first()    

       

        if user:
            session['user_id'] = user.id
            user.status="online"
            db.session.commit()
            print("status online")
            flash('Login successful!', 'success')
            return redirect(url_for('chatpage')) 

        else:
            flash('Invalid username or password. Please try again.', 'error')
    

    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"] )
def register():
    if request.method == 'POST':
        # uname=request.form["uname"]
        uname = request.form.get("uname", "")
        email=request.form["email"]
        password=request.form["password"]
        cpass=request.form["cpass"]
        # if password != cpass:
        #      flash('Password and Confirm Password do not match. Please try again.', 'error')
        
        existing_user = users.query.filter_by(uname=uname).first()     

        if existing_user:
            flash('Username already taken. Please choose another.', 'error')
        else:
            new_user = users(uname=uname, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            # session['user_id'] = new_user.id
        
            flash('Registration successful! You can now log in.', 'success')
            return render_template("login.html")
        

    return render_template("register.html")


@app.route('/users')
def display():
    user = users.query.all()
    return render_template('display.html', users=user)

@app.route('/chatpage')
def chatpage():
     if 'user_id' in session:
        current_user_id = session['user_id']
        current_user = users.query.get(current_user_id)
        other_users = users.query.filter(users.id != current_user_id).all()
        return render_template('chat-page.html', current_user=current_user, other_users=other_users)
     else:
        flash('Please log in to access the chat page.', 'info')
        return redirect(url_for('login'))



# @socketio.on('connect')
# def handle_connect():
#     user_id=session['user_id']
#     join_room(user_id)
     
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')

    if user_id is not None:
        print(type(user_id))
        join_room(user_id)
        emit('update_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)
        print(f"user {user_id} connected ")
    else:
        print("User ID not found in session")     


@socketio.on('disconnect')
def handle_disconnect():
    user_id = session['user_id']
    current_user = users.query.get(user_id)
    current_user.status = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emit('disconnect', {'user_id': user_id, 'status': current_user.status}, broadcast=True)
    






@socketio.on('messagesent')
def handle_message(data):
    print("reached here",data)
    user_id=session['user_id']
    print(user_id,"user_iddddddddddddd")
    if user_id is None:
        print("not got usser id")
        return
    
    select_user_id=data['selectuserId']
    print(select_user_id,type(user_id))
    message=data['message']
    print(message)
   

    # print("select_user_id : " ,select_user_id,"message:" ,data['message'] )

    # msg = messages(content= message , sender_id=user_id, receiver_id=select_user_id,  time=str(datetime.utcnow()),seen=False)
    msg = messages(content=message, sender_id=user_id, receiver_id=select_user_id, time=str(datetime.now()), seen=False)

    try:
       db.session.add(msg)
       db.session.commit()  
       send({'content':msg.content, 'sender':msg.sender_id, 'time':msg.time,'seen':False}, room=int(select_user_id))
       send({'content':msg.content, 'sender':msg.sender_id, 'time':msg.time,'seen':False}, room=user_id)
       print("sending message")

    except Exception as e:
        print(f"Error saving to database: {e}")



    # retrive messages from database
    # message=messages.query.filter((messages.sender_id==user_id) & (messages.receiver_id==select_user_id)) | ((messages.sender_id==select_user_id)&(messages.receiver_id==user_id)).order_by(messages.time).all()

    # # sending to 2 seperate rooms
    # for msg in message:
    #     send({'messages':msg.content, 'sender':msg.sender_id, 'time':msg.time}, room=sender_room_name)
    #     send({'messages':msg.content, 'sender':msg.sender_id, 'time':msg.time}, room=receiver_room_name)
    

# @socketio.on('message')
# def handle_message(data):
#     user_id=session['user_id']
#     select_user_id=data['selectuserId']
#     sender_room_name = f"user{user_id}"
#     receiver_room_name = f"user{select_user_id}"

    # if 'content' in data:
    #     content=data['content']
    #     print(f"received message from {user_id} to selected user {select_user_id} and the content is{content}")

# @app.route('/getallmessages/<int:select_user_id>')
# def getmessages(select_user_id):
#     user_id=session.get('user_id')
#     if user_id:
#         select_user_id=select_user_id
#         messages_all=messages.query.filter((messages.sender_id==user_id) & (messages.receiver_id==select_user_id)) | ((messages.sender_id==select_user_id)&(messages.receiver_id==user_id)).order_by(messages.time).all()
#         message_data=[]
#         for message in messages_all:
#             message_info={'content':message.content, 'sender':message.sender_id, 'time':message.time}
            
#         message_data.append(message_info)
#         return jsonify(message_data)
#     else:
#         return jsonify({'error': 'User not logged in'}), 403

@app.route('/getallmessages/<int:select_user_id>')
def getmessages(select_user_id):
    user_id = session.get('user_id')
    user = users.query.get(select_user_id)
    if user_id:
        messages_all = messages.query.filter(
            ((messages.sender_id == user_id) & (messages.receiver_id == select_user_id)) |
            ((messages.sender_id == select_user_id) & (messages.receiver_id == user_id))
        ).order_by(messages.time).all()

        message_data = []
        for message in messages_all:
            message_info = {'content': message.content, 'sender': message.sender_id, 'time': message.time,'seen':message.seen }
            message_data.append(message_info)
            print("this is the msg",message_data)
            print("status here",user.status)

        # return jsonify(message_data)
        return jsonify({"message_data" : message_data,"status" : user.status})  

    else:
        return jsonify({'error': 'User not logged in'}), 403


@app.route('/get_unread_count')
def message_count():
    print("hello")
    message_count={}
    user_id=session.get('user_id')
    

    print("hwklllooooo")
    new_users=users.query.filter(users.id != user_id).all()
    for filter_user in new_users:
        unread_count=messages.query.filter(messages.sender_id.in_([filter_user.id]),messages.receiver_id.in_([user_id]),messages.seen==False).count()

        print(unread_count,"unread message count")
        message_count[filter_user.id]=unread_count
        print("filteruser",message_count)
   
    
    return jsonify({"message_count" : message_count,"curr_user" : user_id})

# @app.route('/mark_message_seen')
# def mark_messages_seen():
#     user_id=session.get('user_id')
#     messages.query.filter_by(receiver_id =user_id,seen=False).update({'seen':True})
#     db.session.commit()
#     print("enter to the db")
#     return jsonify({'status': 'success'})
@app.route('/mark_message_seen', methods=['POST'])  # Added methods=['POST']
def mark_messages_seen():
    user_id = session.get('user_id')
    # Update the messages for the current user with seen=False to seen=True
    messages.query.filter_by(receiver_id=user_id, seen=False).update({'seen': True})
    db.session.commit()
    print("Entered the database")  # Add a debug print statement
    return jsonify({'status': 'success'})


  

# @app.route('/logout')
# def logout():
#     if 'user_id' in session:
#         users.status=datetime.now()
#         db.session.commit()
#         session.pop("user_id",None)
#         flash('you have been logout', 'info')
#     return redirect(url_for('home')) 

@app.route('/logout')
def logout():
    if 'user_id' in session:
        current_user_id = session['user_id']
        current_user = users.query.get(current_user_id)
        current_user.status = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()
        session.pop("user_id",None)
        # emit('update_status', {'user_id': current_user_id, 'status': current_user.status}, broadcast=True)
        # socketio.emit('update_status', {'user_id': current_user_id, 'status': current_user.status}, broadcast=True)

        flash('you have been logout', 'info')
    return redirect(url_for('home')) 




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True) 