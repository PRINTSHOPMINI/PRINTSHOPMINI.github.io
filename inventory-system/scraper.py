"""
fax.printnuri.com 매출 데이터 스크래퍼
스크린샷 분석 결과 반영 버전
"""

import json as _json
import logging
import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class PrintnuriScraper:
    BASE_URL       = "https://fax.printnuri.com"
    # 로그인 URL - 실제 로그인 페이지 주소로 교체 필요
    LOGIN_URL      = "https://fax.printnuri.com/login"
    # 거래관리 > 상품내역 (tossOrderItem 페이지)
    SALES_BASE_URL = "https://fax.printnuri.com/tossOrderItem"

    # 누적 수집 시작일
    START_DATE = date(2026, 2, 1)

    # ── 상품명 정규화 매핑 ────────────────────────────────────────────────────
    # 스크린샷에서 확인된 실제 상품명 → 시스템 상품명
    PRODUCT_MAP = {
        "코팅지 a4":    "코팅A4",
        "코팅 a4":      "코팅A4",
        "코팅지a4":     "코팅A4",
        "코팅a4":       "코팅A4",
        "코팅지 a3":    "코팅A3",
        "코팅 a3":      "코팅A3",
        "코팅지a3":     "코팅A3",
        "코팅a3":       "코팅A3",
        "l홀더":        "L홀더",
        "l(엠) - 홀더": "L홀더",
        "l(엠)-홀더":   "L홀더",
        "엘홀더":       "L홀더",
        "서류봉투":     "서류봉투",
        "각대봉투":     "서류봉투",
        "제본":         "제본",
        "제본표지":     "제본",
        "흑백제본":     "제본",
        "컬러제본":     "제본",
    }

    # ── 지점명 접두사 제거 ────────────────────────────────────────────────────
    # "프린트샵미니_서정리역점" → "서정리역점"
    BRANCH_PREFIXES = ["프린트샵미니_", "프린트샵미니 ", "printshopmini_"]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Referer": "https://fax.printnuri.com/",
        })
        self.is_authenticated = False

    # ════════════════════════════════ 인증 ════════════════════════════════════

    def login(self, username: str, password: str) -> tuple[bool, str]:
        try:
            resp = self.session.get(self.LOGIN_URL, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            csrf = self._find_csrf(soup)

            # fax.printnuri.com 로그인 폼 필드명 (실제와 다를 경우 수정)
            login_data: dict = {
                "id":       username,
                "password": password,
            }
            if csrf:
                login_data["_token"] = csrf

            resp = self.session.post(
                self.LOGIN_URL,
                data=login_data,
                allow_redirects=True,
                timeout=15,
            )

            # 로그인 성공 시 나타나는 텍스트 ("나가기" 버튼 또는 메뉴)
            success_signals = ["나가기", "거래관리", "tossorderitem", "로그아웃", "logout"]
            if any(s in resp.text.lower() for s in success_signals):
                self.is_authenticated = True
                logger.info("로그인 성공: %s", username)
                return True, "로그인 성공"

            self.is_authenticated = False
            return False, "로그인 실패: 아이디 또는 비밀번호를 확인하세요"

        except requests.exceptions.Timeout:
            return False, "연결 시간 초과"
        except requests.exceptions.ConnectionError:
            return False, "연결 오류: 인터넷 연결을 확인하세요"
        except Exception as e:
            logger.exception("login() 예외")
            return False, f"오류: {e}"

    def set_cookie(self, cookie_string: str) -> tuple[bool, str]:
        """
        브라우저 개발자도구 콘솔에서 복사한 쿠키 문자열을 등록합니다.
        콘솔에서: document.cookie  입력 후 나오는 값 복사
        """
        try:
            self.session.cookies.clear()
            for pair in cookie_string.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    key, _, value = pair.partition("=")
                    self.session.cookies.set(
                        key.strip(), value.strip(), domain="fax.printnuri.com"
                    )

            test = self.session.get(self.SALES_BASE_URL, timeout=15)
            # 로그인 페이지로 리다이렉트되지 않고 테이블 데이터가 있으면 성공
            if test.status_code == 200 and "거래관리" in test.text:
                self.is_authenticated = True
                logger.info("쿠키 인증 성공")
                return True, "세션 쿠키 설정 완료"

            self.is_authenticated = False
            return False, "세션 쿠키가 유효하지 않습니다. 브라우저에서 다시 복사하세요."
        except Exception as e:
            return False, f"쿠키 설정 오류: {e}"

    # ════════════════════════════════ 데이터 수집 ═════════════════════════════

    def fetch_sales_data(self) -> list | None:
        """START_DATE ~ 오늘까지 누적 판매 데이터 수집"""
        if not self.is_authenticated:
            return None

        # fax.printnuri.com은 날짜 범위 일괄 조회를 지원하면 한 번에 처리
        all_data = self._fetch_range(self.START_DATE, date.today())
        if all_data is not None:
            logger.info("날짜 범위 일괄 조회 성공: %d건", len(all_data))
            return all_data

        # 날짜별 순차 조회 (fallback)
        all_sales: list = []
        current = self.START_DATE
        today = date.today()
        while current <= today:
            date_str = current.strftime("%Y%m%d")
            try:
                day_sales = self._fetch_one_day(date_str)
                if day_sales is None:
                    self.is_authenticated = False
                    return None
                all_sales.extend(day_sales)
                logger.info("%s: %d건", date_str, len(day_sales))
            except Exception as e:
                logger.warning("%s 수집 오류: %s", date_str, e)
            current += timedelta(days=1)

        return all_sales

    def _fetch_range(self, start: date, end: date) -> list | None:
        """
        날짜 범위 일괄 조회.
        fax.printnuri.com/tossOrderItem 검색 폼 파라미터명 기반.
        실제 파라미터명이 다르면 아래를 수정하세요.
        """
        params = {
            "startDate": start.strftime("%Y-%m-%d"),  # 조회시작일
            "endDate":   end.strftime("%Y-%m-%d"),    # 조회종료일
        }
        try:
            resp = self.session.get(self.SALES_BASE_URL, params=params, timeout=30)
            if resp.status_code != 200:
                return None
            if "login" in resp.url.lower():
                self.is_authenticated = False
                return None
            result = self.parse_sales_data(resp.text)
            # 결과가 비어있으면 파라미터명이 틀린 것 → fallback
            return result if result else None
        except Exception:
            return None

    def _fetch_one_day(self, date_str: str) -> list | None:
        """특정 날짜(YYYYMMDD) 조회"""
        d = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        params = {"startDate": d, "endDate": d}
        resp = self.session.get(self.SALES_BASE_URL, params=params, timeout=20)

        if resp.status_code in (401, 403):
            return None
        if "login" in resp.url.lower():
            return None
        if resp.status_code != 200:
            return []

        return self.parse_sales_data(resp.text)

    # ════════════════════════════════ HTML 파싱 ════════════════════════════════

    def parse_sales_data(self, html: str) -> list:
        """
        tossOrderItem 페이지 HTML 파싱.

        스크린샷 확인 컬럼 순서:
        0:승인시간  1:그룹명  2:지점명  3:승인번호  4:상품명
        5:카테고리  6:단가    7:수량    8:결제금액  9:결제수단
        10:주문상태 11:주문번호
        """
        sales: list = []

        soup = BeautifulSoup(html, "html.parser")

        # 테이블 탐색 (여러 패턴 시도)
        table = (
            soup.find("table", id="tossOrderItemTable")
            or soup.find("table", class_="table")
            or soup.find("table")
        )
        if not table:
            logger.warning("테이블을 찾지 못했습니다")
            return sales

        rows = table.find_all("tr")
        if len(rows) < 2:
            return sales

        # 헤더로 컬럼 인덱스 자동 감지
        header_cells = rows[0].find_all(["th", "td"])
        headers = [c.get_text(strip=True) for c in header_cells]
        logger.debug("헤더: %s", headers)

        branch_col  = self._find_col(headers, ["지점명", "지점", "매장"])
        product_col = self._find_col(headers, ["상품명", "상품", "품목"])
        qty_col     = self._find_col(headers, ["수량"])
        status_col  = self._find_col(headers, ["주문상태", "상태"])

        # 헤더 감지 실패 시 스크린샷 기준 인덱스 사용
        if branch_col  is None: branch_col  = 2
        if product_col is None: product_col = 4
        if qty_col     is None: qty_col     = 7
        if status_col  is None: status_col  = 10

        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) <= max(branch_col, product_col, qty_col):
                continue
            try:
                # COMPLETED 주문만 집계
                if status_col < len(cols):
                    status = cols[status_col].get_text(strip=True).upper()
                    if status and status not in ("COMPLETED", "완료", "승인"):
                        continue

                raw_branch  = cols[branch_col].get_text(strip=True)
                raw_product = cols[product_col].get_text(strip=True)
                qty_raw     = cols[qty_col].get_text(strip=True)
                qty         = int(re.sub(r"[^\d]", "", qty_raw) or 0)

                branch  = self._normalize_branch(raw_branch)
                product = self._normalize_product(raw_product)

                if branch and product and qty > 0:
                    sales.append({"branch": branch, "product": product, "quantity": qty})
                    logger.debug("  %s / %s / %d", branch, product, qty)

            except (ValueError, IndexError):
                continue

        return sales

    # ════════════════════════════════ 정규화 ══════════════════════════════════

    def _normalize_branch(self, raw: str) -> str:
        """접두사 제거: '프린트샵미니_서정리역점' → '서정리역점'"""
        name = raw.strip()
        for prefix in self.BRANCH_PREFIXES:
            if name.lower().startswith(prefix.lower()):
                name = name[len(prefix):]
                break
        return name

    def _normalize_product(self, raw: str) -> str:
        """상품명 정규화: '코팅지 A4' → '코팅A4'"""
        key = raw.strip().lower()
        # 서류봉투는 괄호 포함 패턴 처리
        if "서류봉투" in key or "각대봉투" in key:
            return "서류봉투"
        for pattern, normalized in self.PRODUCT_MAP.items():
            if pattern in key:
                return normalized
        return raw.strip()

    # ════════════════════════════════ 유틸리티 ════════════════════════════════

    @staticmethod
    def _find_csrf(soup: BeautifulSoup) -> str | None:
        for name in ["_token", "csrf_token", "__RequestVerificationToken"]:
            tag = soup.find("input", {"name": name})
            if tag:
                return tag.get("value")
        meta = soup.find("meta", {"name": "csrf-token"})
        if meta:
            return meta.get("content")
        return None

    @staticmethod
    def _find_col(headers: list[str], keywords: list[str]) -> int | None:
        for i, h in enumerate(headers):
            for kw in keywords:
                if kw in h:
                    return i
        return None
