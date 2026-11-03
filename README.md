# 기쁘띠콘

안 쓰는 기프티콘을 사고파는 이화인의 마켓입니다.
2026 오픈SW플랫폼 팀 프로젝트(5sondoson)입니다.

## 실행 방법

1. 가상환경을 만들고 패키지를 설치합니다.

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Firebase 설정 파일을 `authentication/firebase_auth.json` 에 둡니다.
   이 파일은 GitHub에 올리지 않으므로 팀원에게 따로 받아야 합니다.

   ```json
   {
     "apiKey": "...",
     "authDomain": "...",
     "databaseURL": "https://<프로젝트>-default-rtdb.<지역>.firebasedatabase.app/",
     "projectId": "...",
     "storageBucket": "...",
     "messagingSenderId": "...",
     "appId": "..."
   }
   ```

3. 서버를 실행하고 http://127.0.0.1:5001 에 접속합니다.

   ```bash
   python app.py
   ```

## 기능

| 페이지 | 경로 | 설명 |
|---|---|---|
| 상품 등록 | `/reg_items` | 사진·상품명·판매자 ID·이메일·판매가·지역·상태를 입력하면 Firebase에 저장 |
| 회원가입 | `/signup` | 아이디·비밀번호·닉네임 입력, 아이디 중복 검사, 비밀번호는 SHA-256 해시로 저장 |
| 로그인 | `/login` | 로그인 화면 |
| 상품 목록 / 리뷰 목록 / 리뷰 등록 | `/list`, `/review`, `/reg_reviews` | 화면 |

## 입력 규칙

- 상품명: 비워 둘 수 없고 `. # $ [ ] /` 는 쓸 수 없습니다 (Firebase 키 규칙). 이미 등록된 상품명은 다시 등록할 수 없습니다.
- 판매가: 0 이상의 숫자
- 사진: png, jpg, jpeg, gif, webp. 서버에는 겹치지 않는 임의 이름으로 저장됩니다.
- 아이디: 영문과 숫자 4~20자, 비밀번호: 4자 이상

## 데이터 구조 (Firebase Realtime Database)

```
item/
  <상품명>/
    seller, price, addr, status, email, img_path
user/
  <자동 생성 키>/
    id, nickname, pw (SHA-256 해시)
```

`status` 값은 `selling`(판매중), `reserved`(예약중), `sold`(판매완료) 중 하나입니다.

## 프로젝트 구조

```
app.py              Flask 라우트
database.py         Firebase 연결 (DBhandler)
templates/          HTML 화면
static/             CSS, JS, 이미지
authentication/     Firebase 설정 파일 (GitHub에 올리지 않음)
```
