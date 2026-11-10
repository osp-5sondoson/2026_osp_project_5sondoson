"""기존 상품에 원가·카테고리·유효기간·등록 시각을 1회 채우는 보정 스크립트.

등록 폼이 원가·카테고리·유효기간을 저장하지 않던 때 올라간 상품 14개는
목록에서 할인율·D-day가 비어 보이고 카테고리가 전부 "기타"로 잡힌다.
이 스크립트는 그 상품들에 **없는 필드만** 덧붙인다 (이미 값이 있으면 건드리지 않고,
상품을 지우거나 기본 6개 필드를 바꾸지 않는다).

사용법 (프로젝트 루트에서):
    venv/bin/python scripts/fill_item_fields.py --dry-run         # 바뀔 내용만 출력
    venv/bin/python scripts/fill_item_fields.py "상품명"           # 한 개만 적용
    venv/bin/python scripts/fill_item_fields.py                   # 전체 적용
"""
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DBhandler  # noqa: E402

# 상품명 → (원가, 카테고리, 유효기간까지 남은 날)
# 원가·남은 날은 화면 설계 때 쓴 샘플 데이터와 같게 맞춘다.
FIELDS = {
    "스타벅스 아이스 카페 아메리카노 T": (4500, "카페·베이커리", 3),
    "CU 모바일 상품권 5,000원": (5000, "편의점", 327),
    "BBQ 황금올리브치킨 순살+콜라": (27500, "치킨·피자·버거", 7),
    "투썸플레이스 생딸기 생크림 케이크": (35000, "카페·베이커리", 45),
    "던킨 먼치킨 10개입 2ea": (12000, "카페·베이커리", 1),
    "공차 블랙 밀크티 J": (5700, "카페·베이커리", 30),
    "맘스터치 휠렛버거 세트": (7500, "치킨·피자·버거", 88),
    "배스킨라빈스 쿼터 아이스크림": (18500, "카페·베이커리", 152),
    "이디야커피 시그니처라떼 ICED (L)": (4700, "카페·베이커리", 2),
    "이마트24 모바일 금액권 1만원권": (10000, "상품권", 210),
    "교촌치킨 반반콤보": (23000, "치킨·피자·버거", 19),
    "파리바게뜨 시즌과일 우유 생크림 케이크 1호": (32000, "카페·베이커리", 63),
    # 샘플에 없던 상품은 매장 정가 기준
    "메가커피 아이스 아메리카노": (2000, "카페·베이커리", 40),
    "스타벅스 카페라떼 T": (5000, "카페·베이커리", 60),
}


def missing_fields(current, original_price, category, days):
    """현재 값이 비어 있는 필드만 골라 돌려준다"""
    wanted = {
        "original_price": str(original_price),
        "category": category,
        "expire": (date.today() + timedelta(days=days)).isoformat(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return {k: v for k, v in wanted.items() if not current.get(k)}


def main(argv):
    dry_run = "--dry-run" in argv
    names = [a for a in argv if not a.startswith("--")] or list(FIELDS)

    db = DBhandler()
    items = db.get_items()
    for name in names:
        if name not in FIELDS:
            print(f"[건너뜀] 보정표에 없는 상품: {name}")
            continue
        current = items.get(name)
        if not isinstance(current, dict):
            print(f"[건너뜀] DB에 없는 상품: {name}")
            continue
        fields = missing_fields(current, *FIELDS[name])
        if not fields:
            print(f"[유지] {name}: 이미 모두 채워져 있음")
            continue
        if dry_run:
            print(f"[예정] {name}: {fields}")
            continue
        ok = db.update_item(name, fields)
        print(f"[{'완료' if ok else '실패'}] {name}: {fields}")


if __name__ == "__main__":
    main(sys.argv[1:])
