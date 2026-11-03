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

**상품 등록**
- 사진, 상품명, 판매자 ID, 이메일, 판매가, 사용 가능 지역, 상태(판매중·예약중·판매완료)를 입력하면 Firebase에 저장합니다.
- 사진을 고르면 바로 미리보기가 나타납니다.
- 같은 상품명은 다시 등록할 수 없어 다른 판매자의 상품을 덮어쓰지 않습니다.
- 입력이 잘못되면 안내 메시지와 함께 입력한 값을 그대로 유지합니다.

**회원가입**
- 아이디, 비밀번호, 닉네임으로 가입합니다.
- 아이디 중복을 검사합니다.
- 비밀번호는 원문이 아닌 **SHA-256 해시값**으로 저장합니다.
- 가입이 끝나면 로그인 페이지로 이동합니다.

**공통**
- 모든 페이지에 같은 내비게이션 바(상품 목록 · 리뷰 목록 · 상품 등록 · 리뷰 등록 · 로그인)가 있습니다.

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

### 문제 해결

| 증상 | 해결 |
|---|---|
| `ModuleNotFoundError: No module named 'pyrebase'` | 가상환경을 켠 상태에서 `pip install -r requirements.txt` 를 다시 실행 |
| `FileNotFoundError: ... firebase_auth.json` | 3번 단계의 `authentication/firebase_auth.json` 위치와 파일 이름 확인 |
| 상품·회원 정보가 저장되지 않음 | `firebase_auth.json` 의 `databaseURL` 값과 Firebase 보안 규칙(읽기·쓰기 허용 기간) 확인 |

## 페이지 구성

| 페이지 | 경로 | 방식 | 설명 |
|---|---|---|---|
| 홈 | `/` | GET | 서비스 소개 |
| 상품 목록 | `/list` | GET | 상품 목록 화면 |
| 리뷰 목록 | `/review` | GET | 리뷰 목록 화면 |
| 상품 등록 | `/reg_items` | GET | 상품 등록 화면 |
| 상품 등록 처리 | `/submit_item_post` | POST | 입력 검사 → 사진 저장 → Firebase 저장 → 결과 화면 |
| 리뷰 등록 | `/reg_reviews` | GET | 리뷰 등록 화면 |
| 로그인 | `/login` | GET | 로그인 화면 |
| 회원가입 | `/signup` | GET | 회원가입 화면 |
| 회원가입 처리 | `/signup_post` | POST | 입력 검사 → 중복 검사 → 해시 저장 → 로그인 페이지로 이동 |

## 입력 규칙

| 항목 | 규칙 |
|---|---|
| 상품명 | 비워 둘 수 없음, `. # $ [ ] /` 사용 불가 (Firebase 키 규칙), 이미 등록된 이름 불가 |
| 판매가 | 0 이상의 정수 |
| 사진 | png, jpg, jpeg, gif, webp |
| 아이디 | 영문과 숫자 4~20자, 중복 불가 |
| 비밀번호 | 4자 이상 |
| 그 밖의 항목 | 모두 필수 입력 |

업로드한 사진은 서버에 **겹치지 않는 임의 이름**으로 저장되어, 파일 이름이 같아도 서로 덮어쓰지 않습니다.

## 데이터 구조

Firebase Realtime Database에 아래 구조로 저장됩니다.

```
item/
└── <상품명>/
    ├── seller      판매자 ID
    ├── price       판매가
    ├── addr        사용 가능 지역 / 매장
    ├── status      selling | reserved | sold
    ├── email       이메일
    └── img_path    static/images/ 아래 사진 파일 이름
user/
└── <자동 생성 키>/
    ├── id          아이디
    ├── nickname    닉네임
    └── pw          비밀번호 SHA-256 해시
```

## 프로젝트 구조

```
2026_osp_project_5sondoson/
├── app.py                Flask 라우트와 입력 검사
├── database.py           Firebase 연결 (DBhandler)
├── requirements.txt      필요한 패키지
├── templates/
│   ├── index.html        공통 레이아웃 (내비게이션 바)
│   ├── list.html         상품 목록
│   ├── review.html       리뷰 목록
│   ├── reg_items.html    상품 등록
│   ├── result.html       상품 등록 결과
│   ├── reg_reviews.html  리뷰 등록
│   ├── login.html        로그인
│   └── signup.html       회원가입
├── static/
│   ├── style.css         스타일
│   ├── main.js           사진 미리보기
│   └── images/           샘플 이미지와 업로드된 사진
└── authentication/       Firebase 설정 파일 (GitHub에 올리지 않음)
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
