import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v9.0")
st.markdown("영어 이름 중심의 편리한 검색과 고품격 어학원 전용 피드백을 생성합니다.")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 
try:
    csv_url = sheet_url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=students"
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
        "배운 문법을 활용한 영작 시 실수": "규칙의 단순 암기에 한정되지 않고, 배운 문법 공식을 대입해 본인만의 실전 문장을 직접 구성해보는 응용 라이팅 비중을 늘리겠습니다.",
        "단어 스펠링(철자) 오류": "파닉스 연계 규칙을 활용해 소리를 철자로 유추하는 능력과 함께, 단어장 누적 복습을 통해 어휘의 정확성을 탄탄하게 보완하겠습니다."
    }
}

TRAITS_LIST = [
    "자기주도적 학습 능력이 뛰어나며 과제 완성도가 매우 높습니다.",
    "이론적인 이해도는 높으나 문제 풀이 시 세심한 주의가 조금 더 필요합니다.",
    "스피킹และ 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여합니다.",
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
    # 💡 [업그레이드] 영어이름 (한국어이름) 연동 레이블 생성
    filtered_df = df[df['레벨'] == selected_level].copy()
    filtered_df['student_label'] = filtered_df['영어이름'].fillna('이름없음').astype(str) + " (" + filtered_df['한국어이름'].astype(str) + ")"
    student_list = filtered_df['student_label'].tolist()
    
    # 선생님들이 영어로 치든, 한글로 치든 둘 다 검색창에서 자동 필터링됩니다.
    selected_student = st.selectbox("학생 선택 (영어 또는 한글 이름 검색 가능)", student_list)

selected_en_name = ""
selected_kr_name = ""
if selected_student:
    row = filtered_df[filtered_df['student_label'] == selected_student].iloc[0]
    selected_en_name = row['영어이름']
    selected_kr_name = row['한국어이름']

# --- 교재별 성적 및 단원 입력 ---
st.subheader("📚 2. 교재별 성적표 입력 (100점 만점 기준)")

if "Phonics" in selected_level:
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1:
        main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
    with col_m2:
        main_units = st.multiselect("평가 단원", UNITS, key="main_unit")
    with col_m3:
        main_score = st.text_input("점수", placeholder="예: 90", key="main_score")
    sub_book, sub_units, sub_score = None, [], ""
else:
    st.markdown("**[Main Book 성적]**")
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1:
        main_book = st.selectbox("교재 선택", BOOK1_LIST, key="reg_main")
    with col_m2:
        main_units = st.multiselect("평가 단원", UNITS, key="reg_main_unit")
    with col_m3:
        main_score = st.text_input("점수", placeholder="예: 85", key="reg_main_score")
        
    st.markdown("**[Sub Book 성적]**")
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1:
        sub_book = st.selectbox("교재 선택", ["선택안함"] + BOOK2_LIST, key="reg_sub")
    with col_s2:
        if sub_book != "선택안함":
            sub_units = st.multiselect("평가 단원", UNITS, key="reg_sub_unit")
        else:
            sub_units = []
            st.write("부교재 없음")
    with col_s3:
        if sub_book != "선택안함":
            sub_score = st.text_input("점수", placeholder="예: 80", key="reg_sub_score")
        else:
            sub_score = ""

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
selected_traits = st.multiselect("평소 관찰된 아이의 긍정적 성향 (복수 선택)", TRAITS_LIST)
teacher_custom_feedback = st.text_area("선생님 개별 코멘트 (자유 기재)", placeholder="예: '단어가 약함'이라고 적으셔도 따뜻한 서술형 문장으로 자동 업그레이드됩니다.")

# --- 4. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 맞춤 분석 피드백 생성"):
    if not selected_student:
        st.error("학생을 선택해 주세요.")
    else:
        # 1) 성적표 문자열 조립
        main_units_str = ", ".join(main_units) if main_units else "전체 범위"
        score_report = f"· {main_book} ({main_units_str}) : {main_score}점 / 100점"
        
        if sub_book and sub_book != "선택안함":
            sub_units_str = ", ".join(sub_units) if sub_units else "전체 범위"
            score_report += f"\n· {sub_book} ({sub_units_str}) : {sub_score}점 / 100점"
        
        # 2) 학습 태도 문장
        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        
        # 3) 영역별 진단 문장 (영어 이름 중심)
        diagnosis_text = ""
        if selected_weaknesses:
            diagnosis_text = f"\n이와 더불어, 이번 달 학업 성취도를 정밀 진단한 결과와 이에 따른 큐브어학원의 개별 성장 플랜을 안내해 드립니다.\n"
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    diagnosis_text += f"· 현재 {selected_en_name}는 {area} 영역의 **[{w}]** 부분에서 다소 보완이 필요한 단계로 파악되었습니다. 이를 완벽히 다지기 위해 학원에서는 **{plan}**\n"
        
        # 4) 성향 리스트 결합 (영어 이름 중심)
        traits_text = ""
        if selected_traits:
            traits_text = f"\n평소 학원에서 지켜본 {selected_en_name}는 " + " ".join(selected_traits) + "\n"

        # 5) 선생님의 개별 피드백 문맥 긍정 자동화 로직
        custom_processed_text = ""
        if teacher_custom_feedback:
            raw_feedback = teacher_custom_feedback.strip()
            custom_processed_text = f"""
[담당 강사 개별 관찰 소견]
이번 달 {selected_en_name}를 근거리에서 밀착 지도하며 선생님이 느낀 점을 덧붙여 드립니다.
"{raw_feedback}"
이와 같이 피드백된 지점들은 아이가 더 크게 성장하기 위한 소중한 디딤돌이라 생각합니다. 부족함에 머무르지 않고, 지적된 학습적 디테일들을 하나씩 바르게 고쳐나갈 수 있도록 학원에서도 1:1로 끈기 있게 격려하며 이끌어 가겠습니다.
"""
        else:
            custom_processed_text = f"\n[담당 강사 개별 관찰 소견]\n우리 {selected_en_name}는 매 수업 긍정적인 에너지를 바탕으로 학원 생활에 예쁘게 적응하며 기특하게 성장하고 있습니다.\n"

        # 6) 💡 [핵심 업그레이드] 영어 이름 전면 배치 알림장 템플릿
        feedback_msg = f"""
안녕하세요, {selected_en_name} 학부모님! 😊
큐브어학원에서 이번 한 달간 {selected_en_name}({selected_kr_name}) 학생과 함께 힘차게 달려온 학습 여정과 그 성장을 담은 월말평가 결과를 전해드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 영역별 평가 결과 (100점 만점 기준):
{score_report}

[학습 태도 및 몰입도 리포트]
이번 한 달 동안 학원에서 관찰한 {selected_en_name}의 학습 다이어리입니다.
- {u_sentence}
- {p_sentence}
- {f_sentence}
{traits_text}{diagnosis_text}{custom_processed_text}
선생님들이 신뢰 어린 시선으로 바라본 {selected_en_name}는 앞으로 채워나갈 가능성과 잠재력이 무궁무진한 아이입니다. 이번 평가에서 발견된 우리 아이의 탄탄한 강점은 아낌없이 칭찬해 키워내고, 다소 아쉬웠던 빈틈은 큐브만의 촘촘한 개별 케어 시스템을 통해 확실하게 메워 나가겠습니다.

가정에서도 영어의 날개를 달아가는 {selected_en_name}에게 아낌없는 격려와 따뜻한 칭찬의 말씀 한마디 부탁드립니다. 큐브어학원 역시 언제나 아이의 성장을 가장 가까이서 책임감 있게 지도하겠습니다.

감사합니다.

- 큐브어학원 드림 -
        """
        
        st.success("큐브어학원만의 고품격 피드백 메세지가 생성되었습니다!")
        st.text_area("완성된 피드백 (카톡/문자 전송용)", value=feedback_msg.strip(), height=650)
