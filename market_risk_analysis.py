import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. 환경 및 사용자 설정 (GitHub Secrets / 환경변수에서 불러옴)
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------------------------
# 2. 메인 파이프라인 (하락세 판단 기준 및 6대 리스크 지표 통합 분석)
# ---------------------------------------------------------------------------

def run_market_risk_analysis_pipeline():
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_korean_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    print("Gemini 실시간 웹 서칭 및 시장 하락세/리스크 진단 요청 중...")

    system_instruction = """
너는 신영증권 김효진 박사의 '버블 고점 시그널 분석 방법론'과 거시 경제 지표를 완벽하게 마스터한 금융 시장 모니터링 및 위험 평가 전문가야.
막연한 낙관론을 배제하고, 구글 실시간 검색(`google_search`) 기능을 활용하여 현재 글로벌 증시(나스닥, 다우, S&P500, 유럽, 대만 등)의 계단식 하락 징후와 6대 리스크 지표(10Y-2Y 금리차, 실질금리, 버핏지수, 마진데트, 쉴러PE, 공포탐욕지수/VIX)의 최신 수치를 객관적으로 분석해 줘.
말투는 한국 사람들이 읽기 자연스럽고 명확한 애널리스트 톤을 유지할 것.
"""

    prompt = f"""
기준일자: {today_korean_str}

오늘 날짜 기준(2026년 10월 등 최신 시점)의 실시간 데이터를 검색하여 아래 **2가지 분석 파트**를 포함한 통합 리포트를 작성해 줘.

---

### [PART 1. 글로벌 증시 계단식 하락 및 금리 표면장력 분석 (08번 지침 기반)]
1. **1단계: 글로벌 쏠림 및 계단식 하락 징후 (현재 상태 진단)**
   - 미국 나스닥 대비 다우존스, S&P 500의 수익률 및 마이너스 전환 여부 확인.
   - 유럽, 대만 등 글로벌 주변국/테크 강국의 최근 1~3개월 수익률이 마이너스로 돌아선 국가가 늘어나고 있는지 진단 (테크 강국까지 무너지기 시작하는지 확인).
   - 하락의 깊이(-1% 미만 미미한 조정 vs 본격적 하락) 구분.
2. **2단계: 금리 할인율이 가하는 표면장력 압박**
   - 미국의 기준금리 방향성(인상/동결/인하) 체크 및 이전 사이클 최고점과의 비교 분석.
3. **종합 결론**: 
   - "아직 버블의 끝이 아니다(안심 단계)" / "신호가 무르익는 중(주의 단계)" / "냉정하게 비중을 줄여야 할 때(위험 단계)" 중 하나로 명확히 제시하고 그 이유 요약.

---

### [PART 2. 시장 상투/하락장 징후 6대 지표 감기기 (09번 지침 기반)]
구글 검색을 통해 아래 6대 지표의 최신 수치를 확인하고 표 및 세부 분석을 제공할 것.
1. **미국 국채 10년물-2년물 금리차 (US 10Y-2Y Yield Spread)**
2. **미국 실질 기준금리 (기준금리 - CPI 인플레이션)**
3. **버핏 지수 (Buffett Indicator - 시가총액 대 GDP 비율 추정치)**
4. **마진 데트 (Margin Debt / 증권사 신용잔고 추이)**
5. **쉴러 PE (Shiller PE / CAPE Ratio)**
6. **공포와 탐욕 지수 (Fear & Greed Index) 및 VIX**

- **출력 구성**: 종합 위험도 평가(등급), 6대 지표 현황 표, 세부 분석, 자산 배분 시사점 순으로 작성.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                tools=[{"google_search": {}}]
            )
        )
        analysis_result = response.text.strip() if response.text else "응답 내용 없음"
    except Exception as e:
        analysis_result = f"[실행 오류 발생]: {e}"
        print(analysis_result)

    # -----------------------------------------------------------------------
    # 리포트 본문 구성 및 이메일 발송
    # -----------------------------------------------------------------------
    report_body = f"=========================================================\n"
    report_body += f" 📊 [{today_str}] 시장 하락세 및 리스크 정밀 진단 보고서\n"
    report_body += f"=========================================================\n\n"
    report_body += analysis_result

    send_email(report_body, today_str)


# ---------------------------------------------------------------------------
# 3. 이메일 발송 함수
# ---------------------------------------------------------------------------

def send_email(content, today_str):
    print("이메일 발송 준비 중...")
    
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD or not RECEIVER_EMAIL:
        print("❌ 이메일 발송 실패: 환경변수를 확인해 주세요.")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"[{today_str}] 시장하락세및리스크진단"
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 성공적으로 이메일을 발송했습니다!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")


if __name__ == "__main__":
    print("🚀 시장 하락세 및 리스크 진단 스크립트 실행 시작...")
    run_market_risk_analysis_pipeline()