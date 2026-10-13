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
# 2. 메인 파이프라인 (메모리 반도체 사이클 & 구리 선행 지표 통합 분석)
# ---------------------------------------------------------------------------

def run_memory_copper_analysis_pipeline():
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_korean_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    print("Gemini 실시간 웹 서칭 및 통합 분석 요청 중...")

    system_instruction = """
너는 첨단 반도체 업황(DRAM, NAND)의 사이클 변화를 추적하는 '반도체 투자 전문 애널리스트'이자, AI 데이터 센터와 반도체 경기의 선행 지표인 '구리(Dr. Copper) 시장'을 분석하는 '원자재 및 거시경제 전문 애널리스트'야.
막연한 공포나 낙관론을 배제하고, 구글 실시간 검색(`google_search`) 기능을 적극 활용하여 현재 시점(최신 트렌드포스 현물가/고정가 동향, 빅테크 CapEx 및 Q&A 발주 톤, LME 구리 재고 및 CFTC 포지션)의 데이터를 수집·반영하여 객관적이고 냉정하게 분석해 줘.
말투는 한국 사람들이 읽기 자연스럽고 명확한 애널리스트 톤을 유지할 것.
"""

    prompt = f"""
기준일자: {today_korean_str}

오늘 날짜 기준(2026년 10월 등 최신 시점)의 실시간 데이터를 직접 검색하여 아래 **3가지 파트**로 구성된 통합 리포트를 작성해 줘.

---

### [PART 1. 메모리 반도체 사이클 진단 (02번 지침 기반)]
1. **종합 진단**: 현재 반도체 사이클이 어느 단계(고점/하락기/바닥 다지기/반등기)에 있는지 한 줄로 명확히 요약할 것.
2. **체크리스트별 현황**: 
   - DRAMeXchange 고정거래가 현황 (현물가 하락의 고정가 전이 여부)
   - TrendForce 리포트 기반 공급 과잉률(Oversupply Rate) 추이
   - 주요 기업(삼성전자, SK하이닉스, 마이크론 등) IR 내 '감산' 및 'CAPEX 축소' 멘트 파악
3. **투자 행동 지침**: 지금 당장 사용자가 취해야 할 행동(매수 시작/관망/비중 축소 등) 구체적 제언.

---

### [PART 2. 반도체 사이클 & 리스크 감시 비서 (06번 지침 기반)]
- **종합 위험도 점수**: [0~100점 점수 부여] (점수가 높을수록 매도 및 현금 확보 필요)
- **1) 현물가-고정가 동향 (데드크로스 여부)**: 요약 및 분석
- **2) 수급 및 공급망 상황 (리드 타임 & 재고)**: 주요 유통사 리드 타임 및 제조사 재고 상황
- **3) 거시 경제 및 빅테크 투자 (금리 & CapEx)**: 금리 동향 및 마이크로소프트/구글/메타/AWS 등의 CapEx 축소/지연 여부
- **4) 핵심 단기 신호 (중요)**: 메모리/HBM 가격 상승 부담을 이유로 빅테크가 실제 물량을 조절하거나 투자 효율화로 스탠스를 전환하는 뉘앙스(Q&A 및 발주 톤)가 있는지 확실하게 조사하여 기재.
- **투자자 행동 가이드라인**: 현금 비중 조절 관련 실전적 조언.

---

### [PART 3. 구리(Dr. Copper) 시장 선행 지표 체크 (03번 지침 기반)]
- **한 줄 진단**: (예: 기술적 우상향 및 실물 수요 뒷받침으로 강력한 상승 랠리 지속)
- **1. 차트 추세 (주봉 및 이동평균선)**: 구리 선물(HG) 주봉 기준 20/60주선 등 주요 이평선 위 포지션 및 기술적 판단.
- **2. 상승세 확증 2대 지표 검증**:
  - ① LME 재고량 (실물 수요 소진 속도)
  - ② CFTC 투기적 포지션 (헤지펀드 순매수 베팅 현황)
- **3. 전문가 분석 및 전방 수요 전망 (종합)**: 국내외 IB(골드만삭스 등) 전망 및 AI 데이터 센터·반도체 수요와의 연계성 분석.
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
    report_body += f" 📊 [{today_str}] 메모리반도체 사이클 현황 통합 보고서\n"
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
    msg['Subject'] = f"[{today_str}] 메모리반도체 사이클 현황"
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 성공적으로 이메일을 발송했습니다!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")


if __name__ == "__main__":
    print("🚀 메모리반도체 사이클 현황 분석 스크립트 실행 시작...")
    run_memory_copper_analysis_pipeline()