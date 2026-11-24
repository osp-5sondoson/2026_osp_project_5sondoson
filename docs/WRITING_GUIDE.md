# 기술 블로그 글 올리는 방법

블로그 주소: https://osp-5sondoson.github.io/2026_osp_project_5sondoson/
마감: **11/30(월)** 사이버캠퍼스 제출 (팀당 1번). 각자 **11/28(토)까지** 글을 올린다.

## 누가 무엇을 쓰나

| 종류 (`type`) | 담당 | 주제 예시 |
|---|---|---|
| `Explanation` | subin21cc | 특별 페이지: 오늘 뭐 먹지? · 내 기프티콘함 |
| `Explanation` | aseo0544-crypto | 상품 등록 → 상품 상세 → 구매하기 |
| `Concept` | seoyeon0516 | Firebase Realtime DB 데이터 구조 설계 (회원·상품·리뷰·좋아요, 판매자 평점 계산) |
| `Guide` | minjinini | 프로젝트 로컬 실행 가이드 (clone → 설치 → Firebase 설정 → 실행 → 회원가입·로그인) |
| `Tip / Debugging` | raeyoon | 로그인·세션 디버깅 (세션 키 `user_id`→`id` 불일치, 로그인 실패 flash, 비밀번호 해시) |

## 조건 (과제 공지)

- 글마다 **300단어 이상** (한국어·영어 모두 가능)
- 강의 11 슬라이드의 **"What Makes a Good Post?"**와 **"Common Structure"**를 따른다.

## 올리는 순서

1. `git switch main && git pull` 후 새 브랜치를 만든다. 예: `git switch -c docs/blog-concept`
2. `docs/_post-template.md`를 복사해 `docs/_posts/` 안에 새 파일을 만든다.
   - 파일 이름: `YYYY-MM-DD-영어-제목.md` (예: `2026-11-28-firebase-data-structure.md`)
   - 파일 이름의 영어 부분이 글 주소가 된다 → `/posts/firebase-data-structure/`
3. 맨 위 `---` 사이의 값을 채운다. **`type`은 위 표의 값과 글자 하나까지 똑같이** 써야 메인 페이지에 자동으로 나온다.
4. 그림은 `docs/assets/images/` 에 넣고 본문에서 이렇게 쓴다.
   `![설명]({{ '/assets/images/파일이름.png' | relative_url }})`
5. 커밋 → push → PR을 올리고 본인이 머지한다. 1~2분 뒤 블로그에 반영된다.

## 미리 보기 (선택)

```bash
cd docs
jekyll serve --baseurl /2026_osp_project_5sondoson
# http://127.0.0.1:4000/2026_osp_project_5sondoson/
```
(`gem install jekyll minima jekyll-feed jekyll-seo-tag` 가 필요하다. 안 해도 GitHub에서 알아서 만들어진다.)
