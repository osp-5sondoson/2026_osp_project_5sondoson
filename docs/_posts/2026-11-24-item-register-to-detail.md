---
layout: post
title: "기프티콘 등록부터 상세 페이지까지: 상품 등록 → 상품 상세 → 구매하기"
author: aseo0544-crypto
type: Explanation
summary: "판매자가 올린 사진과 정보가 Flask에서 검증된 후 사진은 서버에·정보는 Firebase에 저장된 뒤 상세 페이지에 등록/표시됨"
---

> 한 줄 요약: 기쁘띠콘에서 판매자가 **상품 등록** 페이지에서 판매 가능한 **상품을 등록**하는 단계부터, 구매자가 **상품 상세 페이지**에서 그 기프티콘을 보고 **구매하기 버튼**을 만나기까지 코드가 어떤 순서로 동작하는지 설명합니다.

## 1. 왜 필요했나

### 1-1. 상황

기쁘띠콘은 안 쓰는 기프티콘을 이화인끼리 사고파는 중고 거래 마켓입니다. 기쁘띠콘 마켓 개발 초기에는 상품 목록과 상세 화면이 모두 코드에 직접 적어 둔 샘플 데이터로만 보였습니다. 때문에 실제 판매자가 기프티콘을 올릴 방법도, 올린 기프티콘을 판매자나 구매자가 확인할 방법도 없었습니다.

### 1-2. 목표

판매자가 사진과 정보를 입력하면 **잘못된 값은 걸러 내고**, 사진은 서버에, 정보는 Firebase Realtime Database에 저장합니다. 그다음 누구나 상품 이름으로 된 주소(`/view_detail/상품명`)로 **같은 상품의 상세 페이지**를 볼 수 있게 하는 것이 목표입니다.

## 2. 등록·저장·조회 구현 과정

### 흐름 한눈에 보기

| 순서 | 주소 | 하는 일 | 파일 |
|---|---|---|---|
| ① | `GET /reg_items` | 등록 화면 보여 주기 | `app.py`, `templates/reg_items.html` |
| ② | `POST /submit_item_post` | 입력 검증 → 사진 저장 → DB 저장 | `app.py`, `database.py` |
| ③ | `GET /view_detail/<name>` | DB에서 한 건 읽어 상세 화면 보여 주기 | `app.py`, `templates/item_detail.html` |
| ④ | (상세 화면) | 판매 상태에 따라 구매하기 버튼 켜기·끄기 | `templates/item_detail.html` |

### ① 상품 등록 화면(판매자가 로그인 하는 계정으로 접근)

![상품 등록 화면]({{ '/assets/images/item-register.png' | relative_url }})

```python
@app.route("/reg_items")
def reg_item():
    if not session.get("id"):
        return login_redirect("기프티콘을 판매하려면 로그인해 주세요.")
    user = DB.get_user(session["id"]) or {}
    return render_template("reg_items.html", categories=CATEGORIES,
                           seller=session["id"], seller_email=user.get("email", ""))
```

로그인하지 않았으면 등록 화면 대신 로그인 화면으로 보냅니다. 판매자 ID와 이메일은 사용자가 입력하지 않아도 되며 로그인한 계정에서 가져와 자동으로 채워 둡니다. 카테고리는 `CATEGORIES` 목록을 넘겨서 드롭다운으로 고르게 했습니다.

### ② 입력 검증(저장 전 정보 검토)

```python
data = {field: request.form.get(field, "").strip() for field in ITEM_FIELDS}
data["seller"] = session["id"]          # 판매자는 폼 값이 아니라 로그인한 계정

if not all(data[field] for field in ITEM_FIELDS) or not data["email"]:
    error = "모든 항목을 입력해 주세요."
elif any(c in data["name"] for c in FORBIDDEN_KEY_CHARS):
    error = "상품명에는 . # $ [ ] / 를 쓸 수 없어요."
elif int(data["price"]) > int(data["original_price"]):
    error = "판매가는 원가보다 높을 수 없어요."
elif DB.item_exists(data["name"]):
    error = "이미 등록된 상품명이에요. 다른 이름으로 등록해 주세요."
```

폼에서 받은 값을 먼저 검사하고, 하나라도 틀리면 저장하지 않고 등록 화면으로 돌아가 이유를 알려 줍니다. 실제 코드에는 학교 이메일, 숫자 가격, 지난 유효기간, 사진 확장자 검사도 있습니다. 특히 상품명은 뒤에서 Firebase의 키로 쓰기 때문에, Firebase 키에 쓸 수 없는 `. # $ [ ] /`를 막고 같은 이름이 있는지도 확인합니다. 같은 이름으로 다시 저장하면 앞 사람의 상품을 덮어쓰기 때문입니다. 다만 이 때문에 동일한 기프티콘(예: 스타벅스 아메리카노 T 사이즈)을 두 사람이 동시에 팔 수 없다는 한계가 생겼습니다. 판매자를 폼 값이 아니라 `session["id"]`로 정한 것은, 폼을 조작해서 남의 아이디로 등록하는 일을 막기 위해서입니다.

### ③ 사진과 상품 정보 저장 방식과 위치

![Firebase item 노드]({{ '/assets/images/item-firebase.png' | relative_url }})

```python
filename = uuid.uuid4().hex + ext
os.makedirs(UPLOAD_DIR, exist_ok=True)
image_file.save(os.path.join(UPLOAD_DIR, filename))

DB.insert_item(data["name"], data, filename)
```

사진 파일은 `static/images/` 폴더에 저장하고, DB에는 **파일 이름만** 남깁니다. 원래의 파일명을 그대로 쓰면 두 사람이 `image.png`를 올렸을 때 서로 덮어쓰거나, `../` 같은 경로가 섞인 이름이면 폴더 밖에 저장될 수 있습니다. 따라서 `uuid`로 겹치지 않는 파일명을 새로 만들었습니다.

```python
def insert_item(self, name, data, img_path):
    item_info = {
        "seller": data['seller'], "price": data['price'], "addr": data['addr'],
        "status": data['status'], "email": data['email'], "img_path": img_path,
        "original_price": data.get('original_price', ""), "category": data.get('category', ""),
        "expire": data.get('expire', ""), "desc": data.get('desc', ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    self.db.child("item").child(name).set(item_info)
```

`item/{상품명}` 아래에 한 상품의 정보를 `set()`으로 저장합니다. 상품명이 키이기 때문에 차후에 상세 페이지에서 이름 하나로 바로 찾을 수 있습니다. 각 필드를 왜 이렇게 나눴는지는 '데이터 구조 설계(Concept)' 글에 자세히 정리되어 있습니다.

### ④ 상세 페이지: 주소에 들어 있는 상품명으로 한 건 읽기

![상품 상세 화면]({{ '/assets/images/item-detail.png' | relative_url }})

```python
@app.route("/view_detail/<name>")
def view_item_detail(name):
    raw = DB.get_item_byname(str(name))
    if not isinstance(raw, dict):
        flash("존재하지 않는 상품이에요.")
        return redirect(url_for("view_list"))
    all_reviews = load_reviews(DB.get_items())
    item = normalize_item(name, raw, seller_stats(all_reviews))
```

`<name>` 자리에 들어온 상품명으로 `item/{상품명}`을 읽는 **동적 라우팅**입니다. 목록에서 링크를 만들 때 `url_for("view_item_detail", name=...)`를 쓰면, "스타벅스 아이스 카페 아메리카노 T"처럼 한글과 띄어쓰기가 있는 이름도 알아서 주소용 글자로 바뀝니다. 없는 상품명으로 들어오면 500 에러 대신 알림을 띄우고 목록으로 돌려보냅니다.

DB에는 가격이 `"3500"` 같은 문자열로 저장되어 있어서 그대로 계산할 수 없습니다. 따라서 `normalize_item()`에서 가격을 숫자로 바꾸고, 원가와 비교해 **할인율**을, 유효기간으로 **D-day**를 계산하고, 사진이 없으면 기본 사진을 넣은 뒤 화면에 넘깁니다. 목록과 상세가 같은 함수를 쓰기 때문에 두 화면의 값은 항상 같습니다.

### ⑤ 구매하기 버튼: 판매중일 때만 활성화

![구매하기 버튼 상태]({{ '/assets/images/item-buy-status.png' | relative_url }})

```html
<button class="button detail__buy" type="button" data-soon="구매"
  {% raw %}{% if data.status != "selling" %} disabled{% endif %}{% endraw %}>구매하기</button>
```

판매 상태가 `selling`(판매중)일 때만 버튼이 눌리고, 예약중이나 판매완료된 상품일 시 버튼이 비활성화됩니다. 실제 결제·전달 흐름은 아직 만들지 않아 지금은 버튼을 누르면 "준비 중" 안내가 뜨도록 `data-soon`을 달아 두었습니다.

## 3. 결과

이제 판매자가 등록 화면에서 정보를 입력하고 **판매하기**를 누르면, 사진은 `static/images/`에, 정보는 Firebase `item` 노드에 저장되고 곧바로 그 상품의 상세 페이지로 이동합니다. 다른 사용자도 목록에서 같은 상품을 눌러 똑같은 상세 페이지를 볼 수 있습니다. 처음 목표였던 "상품 등록 → 상품 저장 → 상품 표시"가 샘플 데이터 외 실제 데이터로 동작하게 되었습니다.

## 4. 정리

- **배운 점 1**: 사용자가 바꿀 수 있는 폼 값은 믿지 않고, 판매자처럼 중요한 값은 서버가 아는 값(세션)으로 정해야 한다는 것을 배웠습니다.
- **배운 점 2**: 상품명을 DB 키와 주소에 함께 쓰면 찾기는 쉽지만, 키에 못 쓰는 글자와 중복을 등록 단계에서 막아야 합니다. 또한, 이와 같은 방식은 같은 상품을 여러 사람이 사고 파는 중고 거래에는 맞지 않았습니다. ID는 사람이 정하는 이름이 아니라 겹치지 않는 값이어야 한다는 것을 알게 됐습니다.
- **다음에 개선할 점**: 구매하기를 실제로 동작하게 만들어, 구매한 기프티콘이 판매 상태 변경과 함께 구매자의 "내 기프티콘함"에 들어가게 하는 것. 리뷰처럼 push() 자동 키를 상품 ID로 쓰고 상품명은 값으로 저장해서, 같은 기프티콘도 여러 개 등록할 수 있게 바꾸는 것. 구매하기도 실제로 동작하게 만드는 것.

## 참고

- 관련 파일: `app.py`(`reg_item`, `reg_item_submit_post`, `view_item_detail`, `normalize_item`), `database.py`(`insert_item`, `get_item_byname`), `templates/reg_items.html`, `templates/item_detail.html`
- [Flask 공식 문서: Uploading Files](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)
- [Flask 공식 문서: Variable Rules (동적 라우팅)](https://flask.palletsprojects.com/en/stable/quickstart/#variable-rules)
- [Pyrebase4 GitHub](https://github.com/nhorvath/Pyrebase4)
- 저장소: [osp-5sondoson/2026_osp_project_5sondoson](https://github.com/osp-5sondoson/2026_osp_project_5sondoson)
