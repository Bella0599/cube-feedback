
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
st.markdown("월말 평가 자동화 ")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 (오직 '학생명단'만!) ---
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

DEFAULT_OBJECTIVE = "해당 단원의 핵심 target 어휘를 마스터하고 필수 구문 구조를 이해하여 문장 속에서 자유롭게 활용하기"

PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = ["Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4", "English Trophy 3", "Reading Trophy 1"]
BOOK2_LIST = ["Writing Monster 1", "Bricks Grammar B1", "Bricks Grammar 1"]
UNITS = [f"Unit {i}" for i in range(1, 13)]

def convert_achievement_to_text(rating, objective, name):
    if rating == "상 (Excellent)": return f"이번 학습의 핵심 목표였던 **[{objective}]** 과정을 완벽하게 마스터했습니다. 개념에 대한 깊이 있는 이해를 바탕으로 실전 오답이 거의 없을 뿐만 아니라, 응용 문장 구사력까지 매끄럽고 훌륭하게 발휘하는 탁월한 성취도를 증명해 보였습니다."
    elif rating == "중 (Good)": return f"이번 학습의 핵심 목표였던 **[{objective}]** 내용을 성실하게 이수했습니다. 전반적인 개념 구조를 올바르게 잘 다져두었으며, 약간의 디테일 교정과 지속적인 반복 훈련을 통해 성취도의 정교함을 한 단계 더 안정적으로 끌어올리는 중입니다."
    else: return f"이번 학습의 핵심 목표였던 **[{objective}]** 부분에 대해 차근차근 개념을 빌드업해 가는 단계입니다. 우리 {name}(이)가 해당 규칙을 온전히 자기 것으로 소화할 수 있도록, 학원 수업 전후 밀착 클리닉과 누적 오답 보완을 통해 틈새를 촘촘하게 채워가겠습니다."

UNDERSTAND_TEXTS = {"상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.", "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.", "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간과 복습 훈련이 조금 더 필요한 상태입니다."}
PRESENT_TEXTS = {"상 (Excellent)": "질문에 대한 발표와 참여도가 적극적이며, 자신감 넘치는 목소리로 반 전체 수업 분위기를 주도합니다.", "중 (Good)": "선생님의 질문에 성실하게 답변하며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다.", "하 (Needs Effort)": "내용을 알고 있더라도 발표 시 다소 수줍어하는 경향이 있어, 적극성을 끌어올리도록 격려 중입니다."}
FOCUS_TEXTS = {"상 (Excellent)": "수업 시간 내내 흔들림 없는 높은 몰입도를 보여주며, 지시 사항을 정확하게 이행하는 집중력이 돋보입니다.", "중 (Good)": "기본적인 수업 집중력을 잘 유지하고 있으며, 흐트러짐 없이 강사의 설명에 귀를 기울입니다.", "하 (Needs Effort)": "간혹 집중력이 흐려지는 순간이 관찰되어, 1:1 대면 질문과 밀착 케어를 통해 주의를 환기시키고 있습니다."}

DIAGNOSIS_DB = {
    "Phonics (파닉스)": {"단모음/장모음 규칙 헷갈림": "비슷한 발음의 단어들을 직접 짝지어 소리 내어 읽고 비교하는 클리닉을 통해 모음 규칙을 완벽히 체화시키겠습니다.", "이중자음(sh, ch 등) 발음 어려움": "다양한 시청각 자료와 리드미컬한 챈트 학습을 활용하여 복잡한 자음 결합 소리에 익숙해지도록 지도하겠습니다."},
    "Reading (독해/리딩)": {"글의 메인 아이디어(주제) 파악 어려움": "지문을 읽은 후 스스로 한 줄 제목을 달아보거나 중심 문장을 찾아내는 훈련을 통해, 글의 거시적인 흐름을 짚어내는 능력을 키우겠습니다.", "세부 내용 찾기 실수": "문제를 먼저 분석한 뒤 지문에서 단서를 역추적하는 스캐닝 기술을 보완하여 실전 오답률을 낮추겠습니다."},
    "Grammar (문법)": {"be동사와 일반동사 쓰임 혼동": "두 동사의 핵심 차이점을 직관적으로 인지시키고, 문장 구조 드릴 학습을 강화하겠습니다."},
    "Writing (영작)": {"대소문자 및 문장 부호 누락": "글쓰기의 기본인 문장 부호 규칙을 강조하고, 작성을 마친 문장을 스스로 피드백하며 정교함을 기르도록 지도하겠습니다."}
}

TRAITS_CATEGORIES = {
    "🥇 우수 학생 추천 (도약과 주도성 칭찬)": ["스피킹과 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여하고, 배운 내용을 완전히 자기 것으로 만드는 흡수력이 뛰어납니다.", "자기주도적 학습 능력이 탁월하여 과제 완성도가 매우 높고, 반 전체의 학업 분위기를 긍정적으로 주도합니다."],
    "🥈 보통 학생 추천 (성실함과 안정적 성장 칭찬)": ["수업 내용을 차분하고 성실하게 따라오며, 지도를 통해 기본적인 개념을 안정적으로 소화해 내는 뚝심이 있습니다.", "학습 태도가 매우 올바르며 피드백을 주면 스펀지처럼 흡수하여, 틀린 문제를 끝까지 해결하려는 끈기가 돋보입니다."],
    "🥉 격려가 필요한 학생 추천 (기특한 노력과 잠재력 칭찬)": ["어려운 과제나 생소한 개념이 주어지더라도 포기하지 않고 끝까지 성실하게 완료하려는 예쁜 태도와 기특한 도전 정신을 가지고 있습니다.", "수업 시간 동안 차분하고 정돈된 태도로 강사의 설명에 성실히 귀를 기울이며, 조금씩 자신만의 학습 페이스를 단단하게 빌드업해 가고 있습니다."]
}

# 💡 [원장님 특별 요청] 12종 명품 강사 코멘트 DB
TEACHER_TEMPLATES = {
    "선택 안 함 (아래 직접 입력)": "",
    "🌟 [성취도/태도 우수] 전반적 우수 및 잠재력 칭찬": "이번 달 평가에서 {name}(이)는 매우 우수한 성적을 거두었습니다. 수업 중 보여주는 집중력과 과제 수행 능력이 탁월하며, 새로운 개념을 습득하는 속도도 빠릅니다. 지금의 성실하고 바른 태도를 꾸준히 유지한다면 앞으로 더 큰 발전이 있을 것으로 몹시 기대됩니다.",
    "🌟 [성취도/태도 우수] 자기 주도 학습 능력 칭찬": "{name}(이)는 스스로 학습 목표를 세우고 이를 달성하려는 의지가 돋보이는 한 달이었습니다. 모르는 부분은 부끄러워하지 않고 적극적으로 질문하며 스스로 해결하려는 자세가 훌륭합니다. 올바른 자기 주도적 학습 습관이 잘 잡혀 있어 매우 긍정적입니다.",
    "🌟 [성취도/태도 우수] 수업 참여도 및 발표력 칭찬": "{name}(이)는 수업에 가장 열정적으로 참여하며 반 분위기를 주도하는 훌륭한 학생입니다. 발표 시 자신의 생각을 논리적으로 잘 전달할 뿐만 아니라, 다른 친구들의 의견도 깊게 경청하는 배려심 깊은 태도가 인상적입니다.",
    "📈 [성실성/발전] 꾸준한 노력형 학생 격려": "{name}(이)는 매시간 성실하게 수업에 임하며, 지난달에 비해 전반적인 이해도가 크게 향상되었습니다. 비록 처음 개념을 익히는 속도는 조금 느릴 수 있으나, 끝까지 포기하지 않고 과제를 완수해 내는 끈기와 성실함이 우리 {name}(이)의 가장 큰 장점입니다.",
    "📈 [성실성/발전] 태도 개선 및 성장 칭찬": "{name}(이)의 학습에 임하는 태도가 수업 초반에 비해 눈에 띄게 의젓해졌습니다. 산만했던 모습이 줄어들고 집중하는 시간이 길어졌으며, 이번 월말평가 결과 역시 긍정적인 상승 곡선을 그리고 있습니다. 앞으로의 성장이 더욱 기대됩니다.",
    "📈 [성실성/발전] 기초 확립 및 다음 단계 도약": "이번 달은 {name}(이)가 특정 영역의 기초 개념을 탄탄하게 다지는 데 집중하였고, 성공적으로 목표를 달성했습니다. 이제는 기본기를 바탕으로 응용문제를 다루는 연습을 병행하며, 한 단계 더 높은 수준으로 나아갈 준비가 되었습니다.",
    "💡 [영역 보완/주의] 집중력 향상 요망": "{name}(이)는 충분한 학습 능력과 잠재력을 갖추고 있으나, 수업 중 간혹 집중력이 흐트러지는 모습이 보입니다. 짧은 시간이라도 몰입해서 학습하는 습관을 기르고 학습 환경을 잘 정돈한다면, 지금보다 성취도가 훨씬 높아질 것입니다.",
    "💡 [영역 보완/주의] 복습 및 과제 수행 강조": "{name}(이)가 수업 시간에 다룬 내용은 잘 이해하고 따라오고 있으나, 가정에서의 복습과 과제 수행이 다소 불규칙합니다. 학원에서 배운 내용을 온전히 자기 것으로 만드는 '복습 과정'에 조금 더 신경 써주시면 실력 향상에 큰 도움이 될 것입니다.",
    "💡 [영역 보완/주의] 자신감 부여 및 적극성 독려": "{name}(이)가 충분히 정답을 알고 있음에도 틀릴까 봐 발표를 주저하는 경향이 있습니다. 틀리는 것은 학습의 자연스럽고 당연한 과정이니, 수업 시간에 실패를 두려워하지 않고 조금 더 자신감을 가지고 적극적으로 참여했으면 좋겠습니다.",
    "🔍 [심화/문제 해결] 응용문제 해결력 보완": "{name}(이)가 기본적인 개념은 훌륭하게 숙지하고 있지만, 두 가지 이상의 개념이 섞인 복합 응용문제를 마주했을 때 당황하는 기색이 있습니다. 다음 달부터는 다양한 유형의 심화 문제를 풀어보며 문제 해결 능력을 기르는 데 집중하겠습니다.",
    "🔍 [심화/문제 해결] 꼼꼼한 검토 습관 요망": "{name}(이)의 문제 풀이 속도가 빠르고 전반적인 이해도도 높지만, 간혹 덜렁대는 성격 탓에 충분히 아는 문제에서 잔실수를 하는 경우가 있습니다. 문제를 끝까지 꼼꼼하게 읽고, 풀이 후 한 번 더 검토하는 습관을 기르도록 지도하겠습니다.",
    "🔍 [심화/문제 해결] 심화 학습 및 도전 권장": "{name}(이)는 현재 정규 진도를 매우 수월하게 따라오고 있으며, 주어진 과제도 완벽하게 소화하고 있습니다. 현재 수준에 만족하기보다는 난이도를 조금 더 높여 심화 학습을 진행해 볼 것을 권장하며, 이를 통해 잠재력을 최대치로 끌어올리겠습니다."
}

def refine_teacher_feedback(raw_text, name):
    if not raw_text: return ""
    refined_sentences = []
    if any(kw in raw_text for kw in ["단어", "어휘", "스펠링"]): refined_sentences.append("현재 성취도가 훌륭한 만큼 단어 암기에 조금만 더 투자하면 독해력과 영작 표현력이 놀랍도록 정교해질 것입니다.")
    if any(kw in raw_text for kw in ["숙제", "과제"]): refined_sentences.append("가끔 과제에서 놓치는 실수가 있습니다. 학원에서도 수업 전 숙제를 더블 체크하며 꼼꼼히 완수하는 습관을 빌드업하겠습니다.")
    if any(kw in raw_text for kw in ["집중", "산만"]): refined_sentences.append("주변에 호기심이 많아 간혹 시선이 분산될 때가 있습니다. 높은 몰입도를 유지하도록 밀착 케어로 집중 페이스를 조절하겠습니다.")
    if refined_sentences: return " ".join(refined_sentences)
    return f"현재 진행 과정에서 '{raw_text}'라는 작은 보완점이 관찰되었습니다. {name}(이)의 잠재력을 알기에 학원에서도 이 부분을 1:1로 섬세하게 지도하겠습니다."

# --- 3. 사용자 입력 화면 UI 구성 ---
st.subheader("👤 1. 학생 선택")
col1, col2 = st.columns(2)
with col1: selected_level = st.selectbox("현재 레벨", df['레벨'].unique().tolist())
with col2:
    filtered_df = df[df['레벨'] == selected_level].copy()
    filtered_df['student_label'] = filtered_df['영어이름'].fillna('이름없음').astype(str) + " (" + filtered_df['한국어이름'].astype(str) + ")"
    selected_student = st.selectbox("학생 선택", filtered_df['student_label'].tolist())

selected_en_name, selected_kr_name = "", ""
if selected_student:
    row = filtered_df[filtered_df['student_label'] == selected_student].iloc[0]
    selected_en_name, selected_kr_name = row['영어이름'], row['한국어이름']

# --- 4. 교재별 성적표 및 정보시트 연동 (이전 버전 고정형) ---
st.subheader("📚 2. 교재별 정보시트 및 성취도 평가")
if "Phonics" in selected_level:
    col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
    with col_m1: main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
    with col_m2: main_unit_single = st.selectbox("집중 평가 단원", UNITS, key="p_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 95", key="p_score")
    
    main_objective = OBJECTIVE_DB.get(main_book, {}).get(main_unit_single, DEFAULT_OBJECTIVE)
    st.info(f"📋 **[{main_book} - {main_unit_single} 학습 목표 정보시트]**\n\n{main_objective}")
    main_rating = st.radio(f"▶ {selected_en_name}의 핵심 목표 달성도 체크", ["상 (Excellent)", "중 (Good)", "하 (Needs Effort)"], key="p_rate", horizontal=True)
    sub_book, sub_unit_single, sub_score, sub_rating, sub_objective = None, None, "", None, ""
else:
    st.markdown("🔺 **[Main Book 설정]**")
    col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
    with col_m1: main_book = st.selectbox("교재 선택", BOOK1_LIST, key="m_book")
    with col_m2: main_unit_single = st.selectbox("집중 평가 단원", UNITS, key="m_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 90", key="m_score")
    
    main_objective = OBJECTIVE_DB.get(main_book, {}).get(main_unit_single, DEFAULT_OBJECTIVE)
    st.info(f"📋 **[Main 목표 정보시트]** {main_objective}")
    main_rating = st.radio(f"▶ Main Book 목표 달성도 체크", ["상 (Excellent)", "중 (Good)", "하 (Needs Effort)"], key="m_rate", horizontal=True)
    
    st.divider()
    st.markdown("🔺 **[Sub Book 설정]**")
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1: sub_book = st.selectbox("교재 선택", ["선택안함"] + BOOK2_LIST, key="s_book")
    with col_s2: sub_unit_single = st.selectbox("집중 평가 단원", UNITS, key="s_unit") if sub_book != "선택안함" else None
    with col_s3: sub_score = st.text_input("점수", placeholder="예: 85", key="s_score") if sub_book != "선택안함" else ""
    
    if sub_book and sub_book != "선택안함":
        sub_objective = OBJECTIVE_DB.get(sub_book, {}).get(sub_unit_single, DEFAULT_OBJECTIVE)
        st.info(f"📋 **[Sub 목표 정보시트]** {sub_objective}")
        sub_rating = st.radio(f"▶ Sub Book 목표 달성도 체크", ["상 (Excellent)", "중 (Good)", "하 (Needs Effort)"], key="s_rate", horizontal=True)
    else:
        sub_rating, sub_objective = None, ""

st.subheader("📊 3. 학생 성향 및 긍정 피드백")
col5, col6, col7 = st.columns(3)
with col5: rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6: rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7: rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

st.markdown("**[수업 시간 아이를 빛내주는 칭찬 성향 선택]**")
selected_traits = []
for category_name, traits in TRAITS_CATEGORIES.items():
    selected = st.multiselect(category_name, traits)
    selected_traits.extend(selected)

st.subheader("🔍 4. 영역별 보완점 및 성장 플랜")
analysis_areas = ["Phonics (파닉스)"] if "Phonics" in selected_level else ["Reading (독해/리딩)"]
if sub_book and sub_book != "선택안함":
    if "Grammar" in sub_book: analysis_areas.append("Grammar (문법)")
    elif "Writing" in sub_book: analysis_areas.append("Writing (영작)")

selected_weaknesses = {}
for area in analysis_areas:
    selected = st.multiselect(f"[{area}] 이번 달 미세 보완이 필요한 디테일", list(DIAGNOSIS_DB[area].keys()))
    if selected: selected_weaknesses[area] = selected


st.subheader("✍️ 5. 담당 강사 추가 개별 피드백 (템플릿 12종)")
selected_template = st.selectbox("📌 큐브어학원 마법의 코멘트 템플릿 선택", list(TEACHER_TEMPLATES.keys()))
teacher_custom_feedback = st.text_area("✍️ 추가 개별 코멘트 (선택 사항)", placeholder="템플릿 내용 외에 덧붙이고 싶은 말씀이나, 직접 작성하고 싶은 내용이 있다면 짧게 입력해 주세요.")

# --- 5. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 프리미엄 피드백 생성"):
    if not selected_student:
        st.error("학생을 선택해 주세요.")
    else:
        score_report = f"· {main_book} ({main_unit_single}) : {main_score}점 / 100점"
        if sub_book and sub_book != "선택안함": score_report += f"\n· {sub_book} ({sub_unit_single}) : {sub_score}점 / 100점"
        
        objective_narrative = f"✔ [Main] {convert_achievement_to_text(main_rating, main_objective, selected_en_name)}"
        if sub_book and sub_book != "선택안함": objective_narrative += f"\n\n✔ [Sub] {convert_achievement_to_text(sub_rating, sub_objective, selected_en_name)}"
            
        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        traits_text = f"\n특히 {selected_en_name}(이)는 평소 학원에서 " + " ".join(selected_traits) if selected_traits else ""
        positive_section = f"- {u_sentence}\n- {p_sentence}\n- {f_sentence}{traits_text}"

        care_plan_text = ""
        if selected_weaknesses:
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    care_plan_text += f"· 더욱 완벽한 성장을 위해 {area} 영역의 **[{w}]** 부분을 아주 미세하게 터치해 주는 단계가 필요합니다. 학원에서는 이를 위해 **{plan}**\n"
        if not care_plan_text: care_plan_text = f"· 현재 {selected_en_name}(이)는 특별한 취약점 없이 모든 영역의 밸런스를 예쁘게 유지하고 있습니다.\n"

        custom_processed_text = ""
        
        if selected_template != "선택 안 함 (아래 직접 입력)":
            custom_processed_text += TEACHER_TEMPLATES[selected_template].format(name=selected_en_name) + "\n"
            
        if teacher_custom_feedback:
            custom_processed_text += refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
            
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 한 달간 {selected_en_name}(이)를 지도하며 선생님이 느낀 점은, 아이가 지닌 가능성과 성실함이 매우 기특하다는 것입니다. 앞으로도 든든한 페이스메이커가 되겠습니다."
            
        custom_processed_text = "· " + custom_processed_text.strip().replace("\n", "\n· ")

        st.session_state.generated_feedback = f"""
안녕하세요, {selected_en_name} 학부모님! 😊
큐브어학원에서 이번 한 달간 {selected_en_name}({selected_kr_name}) 학생과 함께 힘차게 달려온 학습 여정과 성장을 담은 월말평가 리포트를 전해드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 영역별 평가 결과 (100점 만점 기준):
{score_report}


[1. 핵심 단원별 목표 성취 리포트 - 정보시트 기반]
단순 정량 평가를 넘어, 이번 달 아이가 배운 알맹이 중심의 구체적인 목표 달성도 분석입니다.
{objective_narrative}


[2. 학생 성향 및 긍정 태도 리포트]
이번 한 달 동안 학원에서 세심하게 관찰한 {selected_en_name}의 다이어리입니다.
{positive_section}


[3. 완벽한 도약을 위한 단 하나의 디테일 & 큐브 케어 플랜]
다음 레벨로의 완벽한 점프와 빈틈없는 영어 날개를 달아주기 위한 큐브만의 촘촘한 개별 솔루션입니다.
{care_plan_text}


[4. 담당 강사 개별 밀착 소견]
우리 {selected_en_name}는 {custom_processed_text}


가정에서도 영어 공부의 즐거움을 알아가는 {selected_en_name}에게 아낌없는 격려와 따뜻한 칭찬의 말씀 한마디 부탁드립니다.
큐브어학원 역시 언제나 아이의 성장을 가장 가까이서 책임감 있게 지도하겠습니다.
감사합니다.

- 큐브어학원 드림 -
        """.strip()
        st.success("큐브어학원만의 명품 피드백 메세지가 완성되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=700)

