---
layout: post
title: "기쁘띠콘의 Firebase Realtime Database 데이터 구조"
author: seoyeon0516
type: Concept
summary: "회원·상품·리뷰·좋아요의 저장 키와 판매자 평점 계산을 기쁘띠콘의 화면 흐름에 맞춰 설명합니다."
---

> 한 줄 요약: 기쁘띠콘은 회원·상품·리뷰·좋아요를 다시 찾는 방법에 맞춰 저장 키를 정하고, 판매자 평점은 리뷰에서 계산합니다.

## 1. 왜 필요했나

기쁘띠콘에서는 회원이 기프티콘을 등록하고, 다른 회원이 상품을 살펴보거나 리뷰와 좋아요를 남깁니다. 화면마다 회원, 상품, 리뷰, 좋아요를 다시 보여 주려면 이 데이터를 저장하고 연결해야 합니다. 우리 팀은 Firebase Realtime Database에 네 종류의 데이터를 저장했습니다.

Realtime Database는 데이터를 JSON 트리로 관리합니다. 트리에서 **키**는 데이터를 찾는 경로의 일부이고, **필드**는 그 경로에 저장한 정보입니다. 기쁘띠콘은 로그인할 때 회원 아이디를 확인하고, 상품 상세를 열 때 상품명을 사용합니다. 리뷰는 한 상품에 여러 건을 저장하고, 좋아요는 상품별로 누른 사용자를 구분해야 합니다. 화면의 조회 기준에 맞춰 `user`, `item`, `review`, `like`의 키를 각각 정했습니다.

## 2. 어떻게 했나

### 회원은 자동 생성 키와 로그인 아이디를 분리

기쁘띠콘의 회원가입은 여러 회원의 아이디와 학교 이메일을 각각 한 기록으로 보관해야 합니다. 아래는 `database.py`의 `insert_user()`입니다. 가입 화면을 처리하는 `app.py`가 비밀번호를 해시로 바꿔 `pw`에 전달하면, 이 함수가 회원 정보를 묶어 저장합니다.

```python
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
```

`user_duplicate_check()`가 아이디 중복을 확인한 뒤 `push()`가 새 회원 경로를 만듭니다. 저장 경로는 `user/<자동 생성 키>`이고, 그 아래의 `id`가 로그인에 쓰는 아이디입니다. 기쁘띠콘의 회원가입은 새 회원 정보를 기존 기록과 구분해 한 건씩 추가하는 흐름이므로, 저장 키를 직접 만들 필요가 없는 `push()`를 사용했습니다. 자동 생성 키는 **회원 기록을 구분하는 저장 키**, `id`는 **화면에서 입력받아 로그인에 사용하는 값**입니다.

회원가입 시에는 `user_duplicate_check()`가 이미 사용 중인 아이디인지 확인한 뒤 새 기록을 추가합니다. 로그인 시에는 `find_user()`가 저장된 회원 기록의 `id`와 입력한 아이디를 비교하고, 비밀번호는 SHA-256 해시값으로 비교합니다. 사용자는 자동 생성 키를 몰라도 자신이 정한 아이디로 로그인할 수 있습니다.

### 상품은 목록과 상세에서 쓰는 이름으로 조회

기쁘띠콘의 상품 목록에서 카드를 누르면 상품명이 상세 페이지 주소로 전달됩니다. 상세 화면도 그 이름으로 상품을 찾아야 하므로, `insert_item()`은 상품명을 저장 키로 사용해 `item/<상품명>`에 상품 정보를 넣습니다. 아래는 두 함수에서 저장과 조회를 담당하는 부분입니다.

```python
self.db.child("item").child(name).set(item_info)

def get_item_byname(self, name):
    return self.db.child("item").child(name).get().val()
```

`item_info`에는 가격, 유효기간, 이미지 파일명과 판매자 아이디 `seller` 등이 들어갑니다. 판매자는 등록 폼의 입력값이 아니라 로그인 세션의 아이디로 정하므로, 등록한 상품을 현재 회원과 연결할 수 있습니다. `set()`은 상품명 경로에 정보를 저장하고, `get_item_byname()`은 상세 주소에서 받은 같은 이름으로 그 정보를 읽습니다.

저장과 조회에 같은 상품명을 사용하므로 별도 ID를 찾는 단계 없이 목록 카드에서 상세 데이터로 이어집니다. 같은 이름을 저장하면 경로가 겹치기 때문에 등록 전에 `item_exists()`로 중복을 확인합니다. Firebase 키에 사용할 수 없는 `.`, `#`, `$`, `[`, `]`, `/`도 입력 단계에서 검사해 경로가 정상적으로 만들어지도록 했습니다.

### 리뷰는 한 상품에 여러 건을 저장

기쁘띠콘에서는 한 상품에 여러 회원이 리뷰를 남길 수 있고, 한 회원도 여러 리뷰를 작성할 수 있습니다. 그래서 리뷰는 상품명이나 작성자 아이디를 저장 키로 쓰지 않습니다. 아래는 `insert_review()`에서 리뷰 데이터를 만들고 키를 생성하는 부분입니다.

```python
review_info = {
    "item": data['item'],
    "title": data['title'],
    "content": data['content'],
    "rating": data['rating'],
    "used": data['used'],
    "writer": data['writer'],
    "img_path": img_path,
    "date": datetime.now().strftime("%Y.%m.%d"),
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
result = self.db.child("review").push(review_info)
return result["name"]
```

`push()`는 리뷰마다 다른 키를 만들고 `result["name"]`으로 그 키를 돌려줍니다. `item`에는 상품 키인 이름을 넣습니다. 작성 화면은 `item_exists()`로 등록된 상품인지 확인하므로, 리뷰 목록에서 다시 그 상품을 찾을 수 있습니다. `writer`는 작성 폼의 임의 값 대신 로그인 세션의 아이디를 사용합니다. `get_reviews()`는 각 리뷰에 Firebase 키를 `id`로 붙여 목록에 전달합니다. 같은 상품이나 작성자의 리뷰도 별개의 기록으로 다룰 수 있는 이유입니다.

### 좋아요는 상품과 사용자별로 저장

기쁘띠콘의 상품 상세는 좋아요 총수와 함께 로그인한 회원이 이미 눌렀는지도 보여 줍니다. 같은 회원이 버튼을 다시 누르면 좋아요가 취소되어야 하므로, `like/<상품명>/<사용자 아이디>`를 한 사람의 선택 상태를 나타내는 경로로 사용했습니다.

```python
def set_like(self, item_name, user_id, liked):
    if liked:
        self.db.child("like").child(item_name).child(user_id).set(True)
    else:
        self.db.child("like").child(item_name).child(user_id).remove()
```

`set_like()`는 누를 때 해당 경로에 `True`를 저장하고, 취소할 때 같은 경로를 삭제합니다. 따라서 같은 회원의 좋아요가 여러 건으로 쌓이지 않습니다. `get_like()`는 그 경로에 값이 있는지 확인하고, `count_likes()`는 상품 아래의 사용자 키 개수를 세어 버튼의 상태와 총수를 화면에 전달합니다.

### 판매자 평점은 연결된 리뷰에서 계산

상품 목록과 상세에는 상품 자체의 별점보다 **그 판매자가 받은 리뷰의 평균 평점**이 필요합니다. 리뷰에는 상품명 `item`이 저장되고, 상품에는 판매자 아이디 `seller`가 저장됩니다. `load_reviews()`가 리뷰의 상품명으로 상품을 찾아 판매자를 붙인 뒤, `seller_stats()`가 판매자별 별점과 리뷰 수를 계산합니다.

```python
def seller_stats(reviews):
    totals = {}
    for review in reviews:
        if review.get("seller") and 1 <= review.get("rating", 0) <= 5:
            total = totals.setdefault(review["seller"], [0, 0])
            total[0] += review["rating"]
            total[1] += 1
    return {seller: {"rating": round(score / count, 1), "count": count}
            for seller, (score, count) in totals.items()}
```

예를 들어 한 판매자가 4점과 5점 리뷰를 받으면 평균은 4.5점입니다. 이 계산은 화면에 필요한 순간 리뷰를 바탕으로 수행하므로, 새 리뷰를 저장할 때 상품마다 별도 평점 필드를 함께 고칠 필요가 없습니다. 리뷰의 `item`과 상품의 `seller`가 판매자 평점을 만드는 연결 고리입니다.

## 3. 결과

핵심 저장 경로는 `user/<자동 생성 키>`, `item/<상품명>`, `review/<자동 생성 키>`, `like/<상품명>/<사용자 아이디>`입니다. 아래 캡처는 실제 데이터에서 상품과 회원의 키가 어떻게 다른지 보여 줍니다.

![상품명을 키로 사용하는 item 노드]({{ '/assets/images/firebase-item-blog.png' | relative_url }})

*그림 1. `item → 상품명 → 상품 정보`. 이메일 값은 가렸다.*

![자동 생성 키를 사용하는 user 노드]({{ '/assets/images/firebase-user-blog.png' | relative_url }})

*그림 2. `user → 자동 생성 키 → id`. 기존 회원 기록에 있는 `nickname`은 현재 회원가입 코드의 필수 필드는 아니다. `pw`의 해시값은 가렸다.*

상품 상세는 주소에서 전달받은 상품명으로 한 건을 읽습니다. 로그인은 회원 기록의 `id`와 입력값을 비교합니다. 리뷰 목록은 `push()`가 만든 키로 각 리뷰를 구분하고, 리뷰 안의 `item`과 `writer` 필드로 상품과 작성자를 연결합니다. 좋아요는 상품명과 사용자 아이디로 현재 상태를 찾고, 판매자 평점은 리뷰를 상품의 판매자와 연결해 계산합니다.

## 4. 정리

이번 구현을 통해 Firebase의 키는 단순한 이름이 아니라 화면이 데이터를 다시 찾는 경로라는 점을 배웠습니다. 회원과 리뷰는 새 기록마다 고유한 키를 생성하고, 상품은 상세 주소에 쓰는 이름을 키로 사용했습니다. 좋아요는 상품과 사용자 아이디를 함께 경로로 사용해 한 사람의 선택 상태를 저장했습니다. 각 방식은 기쁘띠콘에서 해당 데이터를 다시 사용하는 흐름에 맞춰 정했습니다.

한 데이터의 키와 필드가 다른 데이터를 연결하는 데도 쓰인다는 점을 확인했습니다. 리뷰의 `item`은 상품 키인 이름을 가리키고, 상품의 `seller`는 판매자 평점을 계산할 기준이 됩니다. 앞으로 같은 이름의 상품을 여러 판매자가 등록해야 한다면 상품에 고유 ID를 부여하고, 상세 주소와 리뷰·좋아요의 상품 참조도 함께 바꾸는 방향으로 확장할 수 있습니다.

## 참고

- [프로젝트의 Firebase 저장·조회 코드](https://github.com/osp-5sondoson/2026_osp_project_5sondoson/blob/main/database.py)
- [상품 입력 검사와 판매자 평점 계산 코드](https://github.com/osp-5sondoson/2026_osp_project_5sondoson/blob/main/app.py)
- [Firebase 공식 문서: 데이터 구조 설계](https://firebase.google.com/docs/database/web/structure-data)
