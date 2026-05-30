import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 ")
st.markdown(" 월말평가 학부모 안내문 프리미엄 버전")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 
try:
    @st.cache_data(show_spinner="구글 시트에서 학생 명단을 안전하게 연결 중입니다...")
    def load_student_data(url):
        csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=students"
        data = pd.read_csv(csv_url)
        data = data.dropna(subset=['레벨', '한국어이름'])
        return data
    df = load_student_data(sheet_url)
except:
    st.error("구글 시트 연결을 기다리고 있습니다. 시트 주소를 확인해 주세요.")
    st.stop()

if "generated_feedback" not in st.session_state:
    st.session_state.generated_feedback = ""

# --- 2. 라이브러리 데이터 정의 ---
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

# 💡 [업그레이드] 학생 성향을 학습 수준별 3단계로 세분화하여 배치
TRAITS_CATEGORIES = {
    "🥇 우수 학생 추천 (도약과 주도성 칭찬)": [
        "스피킹과 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여하고, 배운 내용을 완전히 자기 것으로 만드는 흡수력이 뛰어납니다.",
        "자기주도적 학습 능력이 탁월하여 과제 완성도가 매우 높고, 반 전체의 학업 분위기를 긍정적으로 주도합니다.",
        "어휘 암기 속도와 독해 능력이 우수하여 글의 맥락을 정확하게 파악하며, 질문의 수준이 깊고 호기심이 왕성합니다."
    ],
    "🥈 보통 학생 추천 (성실함과 안정적 성장 칭찬)": [
        "수업 내용을 차분하고 성실하게 따라오며, 지도를 통해 기본적인 개념을 안정적으로 소화해 내는 뚝심이 있습니다.",
        "학습 태도가 매우 올바르며 피드백을 주면 스펀지처럼 흡수하여, 틀린 문제를 끝까지 해결하려는 끈기가 돋보입니다.",
        "영어 학습에 대한 친밀감과 자신감이 꾸준히 향상되고 있으며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다."
    ],
    "🥉 격려가 필요한 학생 추천 (기특한 노력과 잠재력 칭찬)": [
        "어려운 과제나 생소한 개념이 주어지더라도 포기하지 않고 끝까지 성실하게 완료하려는 예쁜 태도와 기특한 도전 정신을 가지고 있습니다.",
        "선생님의 지도와 격려에 즉각적으로 반응하며, 칭찬을 받을 때마다 눈빛이 반짝이고 다음 학습에 몰입하는 긍정적인 힘이 좋습니다.",
        "수업 시간 동안 차분하고 정돈된 태도로 강사의 설명에 성실히 귀를 기울이며, 조금씩 자신만의 학습 페이스를 단단하게 빌드업해가고 있습니다."
    ]
}

def refine_teacher_feedback(raw_text, name):
    if not raw_text:
        return ""
    refined_sentences = []
    if any(kw in raw_text for kw in ["단어", "어휘", "스펠링", "Voca"]):
        refined_sentences.append("현재 성취도가 훌륭한 만큼 단어 암기에 아주 조금만 더 시간을 투자하여 깊이를 더해간다면, 앞으로 독해력과 영작 표현력이 무서울 정도로 정교해질 것입니다. 학원에서도 1:1 밀착 점검을 통해 아이가 어휘 암기에 성취감을 느끼도록 가볍게 당겨주겠습니다.")
    if any(kw in raw_text for kw in ["숙제", "과제", "홈워크"]):
        refined_sentences.append("가끔 과제에서 한두 군데 놓치는 귀여운 실수가 발견되기도 합니다. 한 단계 더 높은 자기주도적 성장을 위해, 학원 수업 전 숙제 상태를 먼저 상냥하게 더블 체크하고 꼼꼼히 완수하는 습관을 완벽하게 빌드업하겠습니다.")
    if any(kw in raw_text for kw in ["집중", "산만", "장난", "떠듦"]):
        refined_sentences.append("주변 환경이나 친구들에게 워낙 호기심과 에너지가 넘치다 보니, 간혹 시선이 분산되는 순간이 있습니다. 수업 시간의 높은 몰입도를 끝까지 유지할 수 있도록 눈맞춤 질문과 밀착 케어로 아이의 집중 페이스를 예쁘게 조절해 가겠습니다.")
    if any(kw in raw_text for kw in ["글씨", "알파벳", "대소문자"]):
        refined_sentences.append("글씨를 써 내려갈 때 조금만 더 차분함을 더한다면, 사소한 실수를 완벽하게 제로(0)로 만들 수 있습니다. 작성 후 스스로 한번 되짚어 보는 검토(Proofreading) 루틴을 자연스럽게 훈련시키겠습니다.")
    if any(kw in raw_text for kw in ["속도", "느림", "시간"]):
        refined_sentences.append("문제를 풀거나 과제를 할 때 진중함이 돋보이나, 실전에서의 템포를 조금만 더 리드미컬하게 당겨준다면 본인의 진짜 실력을 제한 시간 내에 막힘없이 100% 쏟아낼 수 있도록 타임 매니지먼트 클리닉을 병행하겠습니다.")
    
    if refined_sentences:
        return " ".join(refined_sentences)
    else:
        if len(raw_text) <= 15 and not raw_text.endswith((".", "요", "다")):
            return f"현재 진행 중인 학습 과정에서 '{raw_text}'라는 작은 디테일적 보완점이 관찰되었습니다. 우리 {name}의 뛰어난 잠재력을 알기에, 학원에서도 이 부분을 놓치지 않고 1:1로 섬세하게 터치하여 완벽한 성장을 이끌어 내겠습니다."
        else:
            return f"{raw_text}\n이처럼 관찰된 사소한 틈새들은 {name}가 더 완벽한 영어 날개를 달기 위한 기분 좋은 성장통이라 생각합니다. 학원에서도 촘촘하게 1:1로 맞춤 지도하여 자신감을 꽉 채워 주겠습니다."

# --- 3. 사용자 입력 화면 UI 구성 ---
st.subheader("👤 1. 학생 선택")
col1, col2 = st.columns(2)
with col1:
    levels = df['레벨'].unique().tolist()
    selected_level = st.selectbox("현재 레벨", levels)
with col2:
    filtered_df = df[df['레벨'] == selected_level].copy()
    filtered_df['student_label'] = filtered_df['영어이름'].fillna('이름없음').astype(str) + " (" + filtered_df['한국어이름'].astype(str) + ")"
    student_list = filtered_df['student_label'].tolist()
    selected_student = st.selectbox("학생 선택", student_list)

selected_en_name = ""
selected_kr_name = ""
if selected_student:
    row = filtered_df[filtered_df['student_label'] == selected_student].iloc[0]
    selected_en_name = row['영어이름']
    selected_kr_name = row['한국어이름']

st.subheader("📚 2. 교재별 성적표 입력 (100점 만점 기준)")
if "Phonics" in selected_level:
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
    with col_m2: main_units = st.multiselect("평가 단원", UNITS, key="main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 90", key="main_score")
    sub_book, sub_units, sub_score = None, [], ""
else:
    st.markdown("**[Main Book 성적]**")
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("교재 선택", BOOK1_LIST, key="reg_main")
    with col_m2: main_units = st.multiselect("평가 단원", UNITS, key="reg_main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 85", key="reg_main_score")
        
    st.markdown("**[Sub Book 성적]**")
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1: sub_book = st.selectbox("교재 선택", ["선택안함"] + BOOK2_LIST, key="reg_sub")
    with col_s2:
        if sub_book != "선택안함": sub_units = st.multiselect("평가 단원", UNITS, key="reg_sub_unit")
        else: sub_units = []; st.write("부교재 없음")
    with col_s3:
        if sub_book != "선택안함": sub_score = st.text_input("점수", placeholder="예: 80", key="reg_sub_score")
        else: sub_score = ""

# ✨ [원장님 요청 3번 분리] 학생 성향 및 긍정 피드백 섹션
st.subheader("📊 3. 학생 성향 및 긍정 피드백")
col5, col6, col7 = st.columns(3)
with col5: rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6: rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7: rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

st.markdown("**[수업 시간 아이들을 빛내주는 칭찬 성향 선택]**")
selected_traits = []
for category_name, traits in TRAITS_CATEGORIES.items():
    selected = st.multiselect(category_name, traits)
    selected_traits.extend(selected)

# ✨ [원장님 요청 4번 분리] 보완점 및 성장 플랜 섹션
st.subheader("🔍 4. 영역별 보완점 및 성장 플랜")
analysis_areas = []
if "Phonics" in selected_level:
    analysis_areas.append("Phonics (파닉스)")
else:
    analysis_areas.append("Reading (독해/리딩)")
    if sub_book and "Grammar" in sub_book: analysis_areas.append("Grammar (문법)")
    elif sub_book and "Writing" in sub_book: analysis_areas.append("Writing (영작)")

selected_weaknesses = {}
for area in analysis_areas:
    weakness_options = list(DIAGNOSIS_DB[area].keys())
    selected = st.multiselect(f"[{area}] 이번 달 미세 보완이 필요한 디테일", weakness_options)
    if selected:
        selected_weaknesses[area] = selected

# ✨ [원장님 요청 5번 분리] 선생님 추가 개별 피드백 섹션
st.subheader("✍️ 5. 담당 강사 추가 개별 피드백")
teacher_custom_feedback = st.text_area("선생님 개별 코멘트 (단답식 간결 기재 가능)", placeholder="예: '단어약함', '숙제미흡' 등 짧게 입력하셔도 학부모님용 명품 문장으로 자동 필터링 변환됩니다.")

# --- 4. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 프리미엄 피드백 생성"):
    if not selected_student:
        st.error("학생을 선택해 주세요.")
    else:
        main_units_str = ", ".join(main_units) if main_units else "전체 범위"
        score_report = f"· {main_book} ({main_units_str}) : {main_score}점 / 100점"
        
        if sub_book and sub_book != "선택안함":
            sub_units_str = ", ".join(sub_units) if sub_units else "전체 범위"
            score_report += f"\n· {sub_book} ({sub_units_str}) : {sub_score}점 / 100점"
        
        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        
        # 3번 조립: 학생성향 + 긍정 피드백
        traits_text = ""
        if selected_traits:
            traits_text = f"\n특히 {selected_en_name}는 평소 학원에서 " + " ".join(selected_traits)
            
        positive_section = f"""- {u_sentence}
- {p_sentence}
- {f_sentence}{traits_text}"""

        # 4번 조립: 보완점 및 학원 대책
        care_plan_text = ""
        if selected_weaknesses:
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    care_plan_text += f"· 현재 {selected_en_name}가 가진 멋진 기량 속에서, 더욱 탄탄한 성장을 위해 {area} 영역의 **[{w}]** 부분을 아주 미세하게 터치해 주는 단계가 필요합니다. 이를 완벽하게 내재화하기 위해 학원에서는 **{plan}**\n"
        if not care_plan_text:
            care_plan_text = f"· 현재 {selected_en_name}는 특별한 취약점 없이 모든 영역의 밸런스를 예쁘게 유지하고 있으며, 지금의 긍정적인 학습 흐름을 끊김 없이 쭉 이어갈 수 있도록 밀착 케어 중입니다.\n"

        # 5) 선생님 추가 개별 피드백 (스마트 필터링)
        custom_processed_text = ""
        if teacher_custom_feedback:
            filtered_text = refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
            custom_processed_text = f"· {filtered_text}"
        else:
            custom_processed_text = f"· 이번 한 달간 {selected_en_name}를 근거리에서 지도하며 선생님이 느낀 점은, 우리 아이가 지닌 잠재력과 매일의 성실함이 매우 기특하다는 것입니다. 앞으로도 칭찬과 격려를 아끼지 않고 든든한 페이스메이커가 되어 주겠습니다."

        # 세련된 알림장 템플릿 완성
        st.session_state.generated_feedback = f"""
안녕하세요, {selected_en_name} 학부모님! 😊
큐브어학원에서 이번 한 달간 {selected_en_name}({selected_kr_name}) 학생과 함께 힘차게 달려온 학습 여정과 그 성장을 담은 월말평가 결과를 전해드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 영역별 평가 결과 (100점 만점 기준):
{score_report}


[1. 학생 성향 및 긍정 피드백 리포트]
이번 한 달 동안 학원에서 세심하게 관찰한 {selected_en_name}의 다이어리입니다.
{positive_section}


[2. 완벽한 도약을 위한 단 하나의 디테일 & 큐브 케어 플랜]
지금도 충분히 훌륭한 성장을 보여주고 있지만, 다음 레벨로의 완벽한 점프와 빈틈없는 영어 날개를 달아주기 위한 큐브만의 촘촘한 개별 성장 솔루션입니다.
{care_plan_text}


[3. 담당 강사 개별 밀착 소견]
우리 {selected_en_name}를 가장 가까이서 밀착 지도하고 아끼는 마음을 담은 코멘트입니다.
{custom_processed_text}


선생님들이 신뢰 어린 시선으로 바라본 {selected_en_name}는 앞으로 채워나갈 가능성과 잠재력이 무궁무진한 아이입니다. 이번 평가에서 증명해낸 우리 아이의 큰 강점들은 아낌없이 칭찬해 자신감을 백 배 키워내고, 미세하게 발견된 빈틈은 큐브만의 섬세한 개별 케어 시스템을 통해 성장의 발판으로 확실하게 다져가겠습니다.

가정에서도 영어 공부의 즐거움을 알아가는 {selected_en_name}에게 아낌없는 격려와 따뜻한 칭찬의 말씀 한마디 부탁드립니다. 큐브어학원 역시 언제나 아이의 성장을 가장 가까이서 책임감 있게 지도하겠습니다.

감사합니다.

- 큐브어학원 드림 -
        """.strip()
        st.success("큐브어학원만의 명품 피드백 메세지가 완성되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=680)
