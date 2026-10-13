import os
import time
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
# 2. 메인 파이프라인 (안정형 분석 버전)
# ---------------------------------------------------------------------------

def run_market_risk_analysis_pipeline():
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_korean_str = datetime.now().strftime("2026년 10월 13일")
    
    print("Gemini 시장 하락세 및 리스크 정밀 진단 생성 중...")

    system_instruction = """
너는 신영증권 김효진 박사의 '버블 고점 시그널 분석 방법론'과 거시 경제 지표를 완벽하게 마스터한 금융 시장 모니터링 및 위험 평가 전문가야.
글로벌 증시 흐름과 거시 경제 리스크 지표를 바탕으로 객관적이고 깊이 있는 분석 보고서를 작성해 줘.
말투는 한국 사람들이 읽기 자연스럽고 명확한 애널리스트 톤을 유지할 것.
절대 마크다운 표(Table) 기호(|)를 사용하지 말고, 깔끔한 글머리 기호와 텍스트 형태로만 작성할 것.
"""

    prompt = f"""
작성 기준일: {today_korean_str} (현재 시점)

아래 2가지 분석 파트를 포함한 정밀 진단 보고서를 작성해 줘. (※ 주의: 표(Table) 형태는 절대 사용하지 말고, 리스트와 텍스트로만 작성할 것)

---

### [PART 1. 글로벌 증시 계단식 하락 및 금리 표면장력 압박 (08번 지침 기반)]
1. **1단계: 글로벌 쏠림 및 계단식 하락 징후**
   - 미국 나스닥, 다우존스, S&P 500의 최근 시장 흐름 비교.
   - 유럽, 대만, 한국 등 글로벌 테크 및 주요국 증시의 하락 징후 진단.
   - 하락의 깊이(-1% 미만 소폭 조정 vs 본격적 하락) 평가.
2. **2단계: 금리 할인율이 가하는 표면장력 압박**
   - 현재 미국 기준금리 수준과 연준(Fed)의 통화정책 방향성이 시장에 미치는 할인율 압박 분석.
3. **종합 결론**: 
   - [안심 단계 / 주의 단계 / 위험 단계] 중 하나를 명확히 제시하고 근거 요약.

---

### [PART 2. 시장 상투/하락장 징후 6대 지표 감지기 (09번 지침 기반)]
다음 6대 핵심 지표의 현재 시장 상황을 평가해 줘. (표 대신 각 항목별 상세 텍스트로 작성)

1. **종합 위험도 평가**: [안정 / 주의 / 경계 / 위험] 등급 부여
2. **6대 지표 현황 및 세부 해석**:
   - 1) 미국 국채 10년물-2년물 금리차 (10Y-2Y): 현황 및 리스크 해석
   - 2) 미국 실질 기준금리: 현황 및 리스크 해석
   - 3) 버핏 지수 (Buffett Indicator): 현황 및 리스크 해석
   - 4) 마진 데트 (신용잔고): 현황 및 리스크 해석
   - 5) 쉴러 PE (CAPE): 현황 및 리스크 해석
   - 6) 공포와 탐욕 지수 및 VIX: 현황 및 리스크 해석
3. **자산 배분 시사점**: 투자자가 취해야 할 실전적 행동 가이드.
"""

    analysis_result = ""
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"API 요청 시도 중... (시도 {attempt}/{max_retries})")
            # 도구(Search)로 인한 충돌 방지를 위해 pure generation 수행
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    max_output_tokens=8192
                )
            )
            
            if response.text and len(response.text.strip()) > 0:
                analysis_result = response.text.strip()
                break
            else:
                print(f"[경고] 시도 {attempt}: 빈 응답 수신")
        except Exception as e:
            print(f"[경고] 시도 {attempt} 실패: {e}")
            
        if attempt < max_retries:
            print("5초 후 재시도합니다...")
            time.sleep(5)
        else:
            if not analysis_result:
                analysis_result = "[오류] 모델이 유효한 응답을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."

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
    print("🚀 시장 하락세 및 리스크 진단 스크립트 실행 시작오류 방지 버전...")
    run_market_risk_analysis_pipeline()
