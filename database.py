
import os
import json
from datetime import datetime
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
        # 실습 기본 6개(seller·price·addr·status·email·img_path)에
        # 화면에서 쓰는 원가·카테고리·유효기간·설명·등록 시각을 더해 저장
        item_info = {
            "seller": data['seller'],
            "price": data['price'],
            "addr": data['addr'],
            "status": data['status'],
            "email": data['email'],
            "img_path": img_path,
            "original_price": data.get('original_price', ""),
            "category": data.get('category', ""),
            "expire": data.get('expire', ""),          # YYYY-MM-DD
            "desc": data.get('desc', ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.db.child("item").child(name).set(item_info)
        return True

    def update_item(self, name, fields):
        """이미 있는 상품에 일부 필드만 덧붙이거나 고친다 (없는 상품이면 False)"""
        if not self.item_exists(name):
            return False
        self.db.child("item").child(name).update(fields)
        return True

    def item_exists(self, name):
        return self.db.child("item").child(name).get().val() is not None

    def get_items(self):
        items = self.db.child("item").get().val()
        return items or {}          # {상품명: {seller, price, ...}, ...}

    def get_item_byname(self, name):
        return self.db.child("item").child(name).get().val()   # 없으면 None

    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "email": "{}@{}".format(data['email_id'], data['email_domain']),
            "phone": data.get('phone', "")
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            return True
        else:
            return False

    def get_user(self, id_):
        """아이디로 회원 정보(id·email·phone)를 찾는다. 없으면 None. 비밀번호 해시는 돌려주지 않음"""
        users = self.db.child("user").get()
        if users.val() is None:
            return None
        for res in users.each():
            value = res.val()
            if isinstance(value, dict) and value.get('id') == id_:
                return {k: v for k, v in value.items() if k != "pw"}
        return None

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        if users.val() is None:
            return True
        for res in users.each():
            value = res.val()
            if isinstance(value, dict) and value.get('id') == id_string:
                return False
        return True

    def find_user(self, id_, pw_hash):
        users = self.db.child("user").get()
        if users.val() is None:
            return False
        for res in users.each():
            value = res.val()
            if isinstance(value, dict) and value.get('id') == id_ and value.get('pw') == pw_hash:
                return True
        return False
