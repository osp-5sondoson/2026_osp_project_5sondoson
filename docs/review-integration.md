# 리뷰 기능 연결 기준

1번 담당이 정한 인터페이스입니다. 각 담당자는 이 이름으로 화면과 DB를 연결합니다.

- 상품 상세의 `리뷰 쓰기` 링크: `GET /reg_reviews?item=<상품명>`
- 등록 폼: `POST /submit_review_post`, `multipart/form-data`
- 폼 입력 이름: `item`(상품명), `title`(제목), `photo`(사진 파일), `content`(본문), `rating`(1~5 정수), `used`(`ok` 또는 `problem`), `writer`(화면 표시용)
- 작성자 신원은 폼의 `writer` 값을 신뢰하지 말고 로그인 세션 `session["id"]`에서 읽기
- 사진은 서버의 `static/images/`에 충돌하지 않는 파일명으로 저장하고, DB에는 파일명만 기록
- Firebase `review` 노드에 `push()`로 저장하고 반환된 자동 키를 리뷰 ID로 사용
- 목록의 사진 링크 및 상세 경로: `/review_detail/<review_id>` (`review_id`는 문자열 키)
- DB 리뷰 필드: `item`, `title`, `img_path`, `content`, `rating`, `used`, `writer`, `date`, `created_at`. 사진 파일명은 `img_path`에 저장

현재 1번 담당 범위는 작성 화면까지입니다. `POST /submit_review_post`의 검증·파일 저장·DB 저장과 실제 리뷰 조회는 각 담당자가 연결해야 합니다.
