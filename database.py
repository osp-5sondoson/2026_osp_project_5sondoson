import os
import json
import pyrebase

AUTH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "authentication", "firebase_auth.json")


class DBhandler:
    def __init__(self):
        with open(AUTH_PATH) as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['seller'],
            "price": data['price'],
            "addr": data['addr'],
            "status": data['status'],
            "email": data['email'],
            "img_path": img_path
        }

        self.db.child("item").child(name).set(item_info)
        return True

    def item_exists(self, name):
        return self.db.child("item").child(name).get().val() is not None

    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "nickname": data['nickname']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            return True
        else:
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        if users.val() is None:
            return True
        for res in users.each():
            value = res.val()
            if isinstance(value, dict) and value.get('id') == id_string:
                return False
        return True
