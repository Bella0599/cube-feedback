import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v7.0")
st.markdown("강사의 정교한 관찰을 따뜻하고 전문적인 문장으로 디자인합니다.")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 
try:
    csv_url = sheet_url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=학생명단"
    df = pd.read_csv(csv_url)
    df = df.dropna(subset=['레벨', '한국어이름'])
except:
    st.error("구글 시트 연결을 기다리고 있습니다. 시트 주소를 확인해 주세요.")
    st.stop()

# --- 2. 데이터 정의 ---
PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = [
    "Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4",
    "English Trophy 3", "English Trophy 4", "English Trophy 5", "English Trophy 6",
    "Reading Trophy 1", "Reading Trophy 2", "Reading Trophy 3"
]
BOOK2_LIST = [
    "Writing Monster 1", "Writing Monster 2", "Writing Monster 3",
    "Bricks Grammar B1", "Bricks Grammar B2", "Bricks Grammar B3",
    "Bricks Grammar 1", "Bricks Grammar 2", "Bricks Grammar 3", "Vista 1"
]
UNITS = [f"Unit {i}" for i in range(1, 13)]

# 📊 [선택 답변별 맞춤형 문장 DB] 상중하 선택에 따라 아래 문장들이 조합됩니다.
UNDERSTAND_TEXTS = {
    "상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.",
    "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.",
    "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간과 복습 훈련이 조금 더 필요한 상태입니다."
}

PRESENT_TEXTS = {
    "상 (Excellent)": "질문에 대한 발표와 참여도가 적극적이며, 자신감 넘치는 목소리로 반 전체 수업 분위기를 주도합니다.",
    "중 (Good)": "선생님의 질문에 성실하게 답변하며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다.",
    "하 (Needs Effort)": "내용을 알고 있더라도 발표 시 다소 수줍어하는 경향이 있어, 적극성을 끌어올리도록 격려 중입니다."
}

FOCUS_TEXTS = {
    "상 (Excellent)": "수업 시간 내내 흔들림 없는 높은 몰입도를 보여주며, 지시 사항을 정확하게 이행하는 집중력이 돋보입니다.",
    "중 (Good)": "기본적인 수업 집중력을 잘 유지하고 있으며, 흐트러짐 없이 강사의 설명에 귀를 기울입니다.",
    "하 (Needs Effort)": "간혹 집중력이 흐려지는 순간이 관찰되어, 1:1 대면 질문과 밀착 케어를 통해 주의를 환기시키고 있습니다."
}

# 🔍 [영역별 진단 및 자연스러운 문장 결합 DB]
DIAGNOSIS_DB = {
    "Phonics (파닉스)": {
        "단모음/장모음 규칙 헷갈림": "비슷한 발음의 단어들을 직접 짝지어 소리 내어 읽고 비교하는 클리닉을 통해 모음 규칙을 완벽히 체화시키겠습니다.",
        "이중자음(sh, ch 등) 발음 어려움": "다양한 시청각 멀티미디어 자료와 리드미컬한 챈트(Chant) 학습을 활용하여 복잡한 자음 결합 소리에 익숙해지도록 지도하겠습니다.",
        "사이트워드(Sight Words) 인지 속도 느림": "한눈에 알아봐야 하는 단어들을 플래시카드 게임 형식으로 반복 노출하여, 문장 읽기의 유창성과 속도를 끌어올리겠습니다."
    },
    "Reading (독해/리딩)": {
        "글의 메인 아이디어(주제) 파악 어려움": "지문을 읽은 후 스스로 한 줄 제목을 달아보거나 중심 문장을 찾아내는 훈련을 통해, 글의 거시적인 흐름을 짚어내는 능력을 키우겠습니다.",
        "세부 내용(True/False) 찾기 실수": "문제를 먼저 분석한 뒤 지문에서 단서를 역추적하는 스캐닝(Scanning) 기술을 보완하여 실전 오답률을 낮추겠습니다.",
        "문장이 길어질 때 끊어 읽기 안 됨": "의미 단위와 구조별로 끊어 읽는 구문 분석 연습을 반복하여, 길고 복잡한 문장도 정확하게 직독직해 하도록 돕겠습니다."
    },
    "Grammar (문법)": {
        "be동사와 일반동사 쓰임 혼동": "두 동사의 핵심 차이점을 직관적으로 인지시키고, 평서문·부정문·의문문으로 자유롭게 변환하는 문장 구조 드릴(Drill) 학습을 강화하겠습니다.",
        "시제(과거/진행형) 형태 변화 실수": "불규칙 동사 변화의 암기를 확실히 다지는 동시에, 문장 속 시간 부사를 포착하여 시제를 정확히 일치시키는 감각을 훈련하겠습니다.",
        "단수/복수 및 관사(a/an/the) 누락": "명사의 수량 개념을 다시 한번 명확히 정립하고, 영작 후 스스로 검토(Proofreading)하여 사소한 실수를 잡아내는 습관을 기르겠습니다."
    },
    "Writing (영작)": {
        "대소문자 및 문장 부호(마침표 등) 누락": "글쓰기의 기본인 문장 부호 규칙을 강조하고, 작성을 마친 문장을 스스로 피드백하며 정교함을 기르도록 세심히 지도하겠습니다.",
        "배운 문법을 활용한 영작 시 실수": "규칙의 단순 암기에 그치지 않고, 배운 문법 공식을 대입해 본인만의 실전 문장을 직접 구성해보는 응용 라이팅 비중을 늘리겠습니다.",
        "단어 스펠링(철자) 오류": "파닉스 연계 규칙을 활용해 소리를 철자로 유추하는 능력과 함께, 단어장 누적 복습을 통해 어휘의 정확성을 탄탄하게 보완하겠습니다."
    }
}

TRAITS_LIST = [
    "자기주도적 학습 능력이 뛰어나며 과제 완성도가 매우 높습니다.",
    "이론적인 이해도는 높으나 문제 풀이 시 세심한 주의가 조금 더 필요합니다.",
    "스피킹과 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여합니다.",
    "영어 쓰기(Writing) 시 문장 구조 파악 능력이 뛰어나고 창의적입니다.",
    "수업 시간 질문이 많고 호기심이 왕성하여 학습 속도가 빠릅니다.",
    "조용하지만 내실이 탄탄하며, 배운 내용을 자기 것으로 만드는 힘이 좋습니다.",
    "어휘 암기 속도가 빠르고 단어 테스트에서 항상 우수한 성적을 거둡니다.",
    "독해 능력이 뛰어나 글의 맥락을 정확하게 파악하는 장점이 있습니다.",
    "영어 학습에 대한 자신감이 크게 향상되었고 참여도가 몰라보게 좋아졌습니다.",
    "학습 태도가 매우 성실하며 틀린 문제를 끝까지 해결하려는 끈기가 돋보입니다."
]

# --- 3. 사용자 입력 화면 ---
st.subheader("👤 1. 학생 선택")
col1, col2 = st.columns(2)
with col1:
    levels = df['레벨'].unique().tolist()
    selected_level = st.selectbox("현재 레벨", levels)
with col2:
    filtered_df = df[df['레벨'] == selected_level]
    student_list = filtered_df['한국어이름'].tolist()
    selected_kr_name = st.selectbox("학생 이름", student_list)

selected_en_name = ""
if selected_kr_name:
    en_row = filtered_df[filtered_df['한국어이름'] == selected_kr_name]['영어이름'].values
    selected_en_name = en_row[0] if len(en_row) > 0 else ""

st.subheader("📚 2. 교재 및 평가 범위")
col3, col4 = st.columns(2)
with col3:
    if "Phonics" in selected_level:
        main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
        sub_book = None
    else:
        main_book = st.selectbox("Main Book", BOOK1_LIST)
with col4:
    if "Phonics" in selected_level:
        st.info("파닉스반은 단권 진행")
        sub_book = None
    else:
        sub_book = st.selectbox("Sub Book", ["선택안함"] + BOOK2_LIST)

selected_units = st.multiselect("평가 단원", UNITS)
score = st.text_input("평가 점수", placeholder="예: 95점 / 100점")

st.subheader("📊 3. 학습 태도 분석")
col5, col6, col7 = st.columns(3)
with col5:
    rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6:
    rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7:
    rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

st.subheader("🔍 4. 영역별 취약점 진단 및 성장 플랜")
analysis_areas = []
if "Phonics" in selected_level:
    analysis_areas.append("Phonics (파닉스)")
else:
    analysis_areas.append("Reading (독해/리딩)")
    if sub_book and "Grammar" in sub_book:
        analysis_areas.append("Grammar (문법)")
    elif sub_book and "Writing" in sub_book:
        analysis_areas.append("Writing (영작)")

selected_weaknesses = {}
for area in analysis_areas:
    weakness_options = list(DIAGNOSIS_DB[area].keys())
    selected = st.multiselect(f"[{area}] 이번 달 가장 집중 보완이 필요한 부분", weakness_options)
    if selected:
        selected_weaknesses[area] = selected

st.subheader("🌟 5. 학생 성향 및 강사 추가 의견")
selected_traits = st.multiselect("평소 관찰된 아이의 긍정적 성향 (복수 선택 가능)", TRAITS_LIST)
teacher_custom_feedback = st.text_area("선생님 개별 코멘트 (자유 기재)", placeholder="아이의 특별한 에피소드나 칭찬을 적어주시면 편지가 더욱 풍성해집니다.")

# --- 4. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 맞춤 분석 피드백 생성"):
    if not selected_kr_name:
        st.error("학생을 선택해 주세요.")
    else:
        units_str = ", ".join(selected_units)
        books_str = main_book if not sub_book or sub_book == "선택안함" else f"{main_book}, {sub_book}"
        
        # 1) 학습 태도 서사형 문장 조합
        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        
        # 2) 진단 및 케어 방향성 문장 조합
        diagnosis_text = ""
        if selected_weaknesses:
            diagnosis_text = f"\n이와 더불어, 이번 달 학업 성취도를 정밀 진단한 결과와 이에 따른 큐브어학원의 개별 성장 플랜을 안내해 드립니다.\n"
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    # 딱딱한 양식이 아니라 서술형으로 자연스럽게 결합
                    diagnosis_text += f"· 현재 {selected_kr_name}는 {area} 영역의 **[{w}]**
