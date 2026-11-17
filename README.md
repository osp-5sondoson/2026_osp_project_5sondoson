# 🎁 기쁘띠콘

> 2026 오픈SW플랫폼 팀 프로젝트 · **오손도손**

안 쓰는 기프티콘을 이화인끼리 사고파는 중고 거래 마켓입니다.
사진과 정보를 올려 기프티콘을 판매하고, 회원가입 후 거래에 참여할 수 있습니다.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## 목차

- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [시작하기](#시작하기)
- [페이지 구성](#페이지-구성)
- [입력 규칙](#입력-규칙)
- [데이터 구조](#데이터-구조)
- [프로젝트 구조](#프로젝트-구조)
- [팀원](#팀원)

## 주요 기능

**상품 목록 · 상세**
- Firebase에 등록된 상품을 한 쪽에 12개씩 보여 주고, 카테고리 · 정렬 · 검색 · 판매중만 보기를 지원합니다.
- 상품 사진을 누르면 상세 페이지(`/view_detail/<상품명>`)로 이동합니다.
- 상세 페이지에는 판매자 평점과 판매자가 받은 최근 거래 리뷰가 나옵니다.

**상품 등록**
- 사진, 상품명, 카테고리, 판매가 · 원가, 사용 가능 지역, 유효기간, 상태(판매중 · 예약중 · 판매완료), 설명을 입력하면 Firebase에 저장합니다.
- 판매자 ID와 이메일은 로그인한 계정에서 가져옵니다.
- 같은 상품명은 다시 등록할 수 없어 다른 판매자의 상품을 덮어쓰지 않습니다.

**거래 리뷰**
- 상품 상세의 `리뷰 쓰기`를 누르면 상품명이 채워진 작성 화면이 열립니다.
- 제목 · 사진 · 본문 · 별점을 입력하면 사진은 서버에 저장하고, 리뷰는 `review` 노드에 `push()`로 저장합니다.
- 리뷰 목록은 2×2로 한 쪽에 4개씩 보여 주고, 사진을 누르면 자동 생성된 리뷰 ID를 쓰는 상세 페이지로 이동합니다.
- 리뷰는 상품이 아닌 판매자에게 쌓이며, 판매자 평점은 받은 리뷰 별점의 평균으로 계산합니다.

**좋아요**
- 상품 상세의 하트 버튼을 처음 누르면 좋아요, 다시 누르면 취소됩니다.
- AJAX로 처리해 페이지를 새로 고치지 않고 버튼만 바뀝니다.
- 로그인한 사용자별로 `like` 노드에 저장합니다. 로그인하지 않았으면 로그인 화면으로 안내합니다.

**회원**
- 아이디, 비밀번호, 학교 이메일(@ewha.ac.kr · @ewhain.net), 전화번호(선택)로 가입합니다.
- 아이디 중복을 검사하고, 비밀번호는 원문이 아닌 **SHA-256 해시값**으로 저장합니다.
- 로그인하면 세션에 아이디를 저장하고, 로그인이 필요한 페이지는 로그인 후 원래 페이지로 돌아옵니다.

**특별 페이지**
- 오늘 뭐 먹지?: 예산과 카테고리로 판매 중인 상품을 추천합니다.
- 내 기프티콘함: 구매한 기프티콘을 모아 봅니다.

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 백엔드 | Python, Flask |
| 데이터베이스 | Firebase Realtime Database (Pyrebase4) |
| 프론트엔드 | HTML (Jinja2 템플릿), CSS, JavaScript |
| 협업 | Git, GitHub (브랜치 · Pull Request) |

## 시작하기

### 1. 저장소 받기

```bash
git clone https://github.com/osp-5sondoson/2026_osp_project_5sondoson.git
cd 2026_osp_project_5sondoson
```

### 2. 가상환경 만들고 패키지 설치

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Firebase 설정 파일 넣기

`authentication/firebase_auth.json` 을 만들고 Firebase 콘솔의 웹 앱 설정값을 넣습니다.
**이 파일은 GitHub에 올리지 않으므로** 팀원에게 따로 받아야 합니다.

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

### 4. 실행

```bash
python app.py
```

브라우저에서 http://127.0.0.1:5001 에 접속합니다.

세션 서명 키는 기본값이 들어 있어 그냥 실행해도 됩니다. 배포할 때만 환경변수로 바꿔 넣습니다.

```bash
export SECRET_KEY="임의의 긴 문자열"   # Windows: set SECRET_KEY=...
```

### 문제 해결

| 증상 | 해결 |
|---|---|
| `ModuleNotFoundError: No module named 'pyrebase'` | 가상환경을 켠 상태에서 `pip install -r requirements.txt` 를 다시 실행 |
| `FileNotFoundError: ... firebase_auth.json` | 3번 단계의 `authentication/firebase_auth.json` 위치와 파일 이름 확인 |
| 상품·회원 정보가 저장되지 않음 | `firebase_auth.json` 의 `databaseURL` 값과 Firebase 보안 규칙(읽기·쓰기 허용 기간) 확인 |

## 페이지 구성

| 페이지 | 경로 | 방식 | 설명 |
|---|---|---|---|
| 홈 | `/` | GET | 상품 목록으로 이동 |
| 상품 목록 | `/list` | GET | 상품 목록 (`?page=` 페이지 · 카테고리 · 정렬 · 검색) |
| 상품 상세 | `/view_detail/<상품명>` | GET | 상품 정보 · 판매자 평점 · 판매자 리뷰 · 좋아요 |
| 좋아요 | `/like/<상품명>` | POST | 좋아요 설정 · 취소 후 결과를 JSON으로 반환 (AJAX) |
| 상품 등록 | `/reg_items` | GET | 상품 등록 화면 (로그인 필요) |
| 상품 등록 처리 | `/submit_item_post` | POST | 입력 검사 → 사진 저장 → Firebase 저장 → 상세로 이동 |
| 리뷰 목록 | `/review` | GET | 리뷰 목록 (2×2, 한 쪽에 4개) |
| 리뷰 상세 | `/review_detail/<리뷰 ID>` | GET | 리뷰 한 건 (리뷰 ID는 `push()`가 만든 키) |
| 판매자별 리뷰 | `/seller_reviews/<판매자 ID>` | GET | 판매자가 받은 리뷰와 평점 |
| 리뷰 작성 | `/reg_reviews?item=<상품명>` | GET | 상품명이 채워진 리뷰 작성 화면 (로그인 필요) |
| 리뷰 등록 처리 | `/submit_review_post` | POST | 입력 검사 → 사진 저장 → `review` 노드에 `push()` |
| 오늘 뭐 먹지? | `/today`, `/today/result` | GET | 예산 · 카테고리로 상품 추천 |
| 내 기프티콘함 | `/my_gifticons` | GET | 구매한 기프티콘 (로그인 필요) |
| 로그인 후 홈 | `/home` | GET | 로그인 후 첫 화면 |
| 로그인 | `/login` | GET | 로그인 화면 |
| 로그인 처리 | `/login_confirm` | POST | 아이디 · 비밀번호 해시 확인 후 세션 저장 |
| 로그아웃 | `/logout` | GET | 세션 삭제 후 상품 목록으로 이동 |
| 회원가입 | `/signup` | GET | 회원가입 화면 |
| 회원가입 처리 | `/signup_post` | POST | 입력 검사 → 중복 검사 → 해시 저장 → 로그인 페이지로 이동 |

## 입력 규칙

| 항목 | 규칙 |
|---|---|
| 상품명 | 비워 둘 수 없음, `. # $ [ ] /` 사용 불가 (Firebase 키 규칙), 이미 등록된 이름 불가 |
| 판매가 · 원가 | 0 이상의 정수, 판매가는 원가보다 높을 수 없음 |
| 유효기간 | 이미 지난 날짜 불가 |
| 리뷰 | 상품명 · 제목(40자까지) · 별점(1~5) · 내용(1000자까지) 필수, 사진은 선택 |
| 사진 | png, jpg, jpeg, gif, webp, 한 장당 5MB까지 |
| 아이디 | 영문과 숫자 4~20자, 중복 불가 |
| 비밀번호 | 영문과 숫자를 포함해 8자 이상 |
| 이메일 | 학교 이메일(@ewha.ac.kr · @ewhain.net)만 가능 |

업로드한 사진은 서버에 **겹치지 않는 임의 이름**으로 저장되어, 파일 이름이 같아도 서로 덮어쓰지 않습니다.

## 데이터 구조

Firebase Realtime Database에 아래 구조로 저장됩니다.

```
item/
└── <상품명>/
    ├── seller          판매자 ID (로그인한 계정)
    ├── email           판매자 이메일
    ├── price           판매가
    ├── original_price  원가
    ├── category        카테고리
    ├── addr            사용 가능 지역 / 매장
    ├── expire          유효기간 (YYYY-MM-DD)
    ├── status          selling | reserved | sold
    ├── desc            상품 설명
    ├── img_path        static/images/ 아래 사진 파일 이름
    └── created_at      등록 시각
review/
└── <push() 자동 생성 키 = 리뷰 ID>/
    ├── item            상품명
    ├── title           제목
    ├── content         본문
    ├── rating          별점 1~5
    ├── used            ok (정상 사용) | problem (문제 있었음)
    ├── writer          작성자 ID (로그인한 계정)
    ├── img_path        리뷰 사진 파일 이름 (사진이 없으면 상품 사진)
    ├── date            작성일 (YYYY.MM.DD)
    └── created_at      작성 시각
like/
└── <상품명>/
    └── <사용자 ID>     true (좋아요를 누른 사용자만 저장, 취소하면 삭제)
user/
└── <자동 생성 키>/
    ├── id              아이디
    ├── pw              비밀번호 SHA-256 해시
    ├── email           학교 이메일
    └── phone           전화번호 (선택)
```

판매자 평점은 따로 저장하지 않고, 리뷰의 상품명으로 판매자를 찾아 받은 리뷰 별점의 평균으로 계산합니다.

## 프로젝트 구조

```
2026_osp_project_5sondoson/
├── app.py                  Flask 라우트와 입력 검사
├── database.py             Firebase 연결 (DBhandler)
├── requirements.txt        필요한 패키지
├── scripts/                기존 상품 데이터 보정 스크립트
├── templates/
│   ├── index.html          공통 레이아웃 (헤더 · 푸터)
│   ├── list.html           상품 목록
│   ├── item_detail.html    상품 상세 (좋아요 버튼)
│   ├── reg_items.html      상품 등록
│   ├── review.html         리뷰 목록
│   ├── review_detail.html  리뷰 상세
│   ├── seller_reviews.html 판매자별 리뷰
│   ├── reg_reviews.html    리뷰 작성
│   ├── special.html        오늘 뭐 먹지? (조건 선택)
│   ├── special_result.html 오늘 뭐 먹지? (추천 결과)
│   ├── my_gifticons.html   내 기프티콘함
│   ├── home_logged_in.html 로그인 후 홈
│   ├── login.html          로그인
│   ├── signup.html         회원가입
│   └── 404.html            없는 페이지
├── static/
│   ├── style.css           공통 스타일 (디자인 토큰 · 버튼 · 카드)
│   ├── css/                화면별 스타일
│   ├── main.js             사진 미리보기 · 좋아요(AJAX) 등
│   └── images/             샘플 이미지와 업로드된 사진
└── authentication/         Firebase 설정 파일 (GitHub에 올리지 않음)
```

## 팀원

<table>
  <tr>
    <td align="center" width="160"><a href="https://github.com/subin21cc"><img src="https://github.com/subin21cc.png" width="100" height="100" alt="subin21cc"></a></td>
    <td align="center" width="160"><a href="https://github.com/minjinini"><img src="https://github.com/minjinini.png" width="100" height="100" alt="minjinini"></a></td>
    <td align="center" width="160"><a href="https://github.com/raeyoon"><img src="https://github.com/raeyoon.png" width="100" height="100" alt="raeyoon"></a></td>
    <td align="center" width="160"><a href="https://github.com/seoyeon0516"><img src="https://github.com/seoyeon0516.png" width="100" height="100" alt="seoyeon0516"></a></td>
    <td align="center" width="160"><a href="https://github.com/aseo0544-crypto"><img src="https://github.com/aseo0544-crypto.png" width="100" height="100" alt="aseo0544-crypto"></a></td>
  </tr>
  <tr>
    <td align="center" width="160"><a href="https://github.com/subin21cc">@subin21cc</a></td>
    <td align="center" width="160"><a href="https://github.com/minjinini">@minjinini</a></td>
    <td align="center" width="160"><a href="https://github.com/raeyoon">@raeyoon</a></td>
    <td align="center" width="160"><a href="https://github.com/seoyeon0516">@seoyeon0516</a></td>
    <td align="center" width="160"><a href="https://github.com/aseo0544-crypto">@aseo0544-crypto</a></td>
  </tr>
</table>
