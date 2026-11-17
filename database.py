
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


    def get_review_by_id(self, review_id):
        """Firebase에서 리뷰 ID로 리뷰 한 건 조회"""
        review = self.db.child("review").child(review_id).get().val()
        return review if isinstance(review, dict) else None
    
    def get_like(self, item_name, user_id):
        """user_id가 이 상품에 좋아요를 눌렀는지 (like/<상품명>/<user_id> 에 True 가 있으면 누른 것)"""
        return bool(self.db.child("like").child(item_name).child(user_id).get().val())

    def set_like(self, item_name, user_id, liked):
        """좋아요를 누르면 like/<상품명>/<user_id> = True, 취소하면 그 값을 지운다"""
        if liked:
            self.db.child("like").child(item_name).child(user_id).set(True)
        else:
            self.db.child("like").child(item_name).child(user_id).remove()

    def count_likes(self, item_name):
        """이 상품에 좋아요를 누른 사용자 수"""
        likes = self.db.child("like").child(item_name).get().val()
        return len(likes) if isinstance(likes, dict) else 0

    def insert_review(self, data, img_path):
        """리뷰 하나를 review 노드에 push()로 저장하고, 자동 생성된 리뷰 ID(키)를 돌려준다"""
        review_info = {
            "item": data['item'],
            "title": data['title'],
            "content": data['content'],
            "rating": data['rating'],          # 1~5 숫자
            "used": data['used'],              # ok(문제없이 사용) / problem(문제 있었음)
            "writer": data['writer'],          # 로그인한 계정 ID
            "img_path": img_path,              # static/images 안의 파일명
            "date": datetime.now().strftime("%Y.%m.%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        result = self.db.child("review").push(review_info)
        return result["name"]
    
    def get_reviews(self):
        """Firebase review 노드의 전체 리뷰를 가져온다"""
        reviews = self.db.child("review").get()

        if reviews.val() is None:
            return []

        result = []

        for review in reviews.each():
            data = dict(review.val())

            if isinstance(data, dict):
                data["id"] = review.key()
                result.append(data)

        return result

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
