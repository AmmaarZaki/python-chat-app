from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

users: list = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000, 9999)}"
    gender = random.choice(["girl", "boy"])
    avatar = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {"username": username, "gender": gender, "avatar": avatar}

    emit("user_joined", {"username": username, "avatar": avatar}, broadcast=True)
    emit("set_username", {"username": username})
    emit("set_gender", {"gender": gender})
    
@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)
        
@socketio.on("send_message")
def handle_message(data: str):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)
        
@socketio.on("update_username")
def handle_update_username(data: str):
    old_username: str = users[request.sid]["username"]
    new_username: str = data["username"]
    users[request.sid]["username"] = new_username
    
    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username
    }, broadcast=True)
    
@socketio.on("update_gender")
def handle_update_gender(data: str):
    username = users[request.sid]["username"]
    old_gender = users[request.sid]["gender"]
    new_gender = data["gender"]
    users[request.sid]["gender"] = new_gender
    users[request.sid]["avatar"] = f"https://avatar.iran.liara.run/public/{new_gender}?username={username}"
    
    emit("gender_updated", {
        "username": username,
        "old_gender": old_gender,
        "new_gender": new_gender
    }, broadcast=True)  

if __name__ == "__main__":
    socketio.run(app)