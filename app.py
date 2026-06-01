import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v18.2")
st.markdown("파닉스 진단 고도화 및 수준별 격려/클로징 멘트 자동화 버전")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 
try:
    @st.cache_data(show_spinner="구글 시트에서 학생 명단을 연결 중입니다...")
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

# --- 💡 2. 데이터 및 템플릿 정의 ---
DEFAULT_OBJECTIVE = "해당 단원의 핵심 target 어휘를 마스터하고 필수 구문 구조를 이해하여 자유롭게 활용하기"

PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = ["Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4", "English Trophy 3", "Reading Trophy 1"]
BOOK2_LIST = ["Writing Monster 1", "Bricks Grammar B1", "Bricks Grammar 1"]
UNITS = [f"Unit {i}" for i in range(1, 13)]

def get_rating_from_score(score_str):
    try:
        score = float(score_str)
        if score >= 90: return "상 (Excellent)"
        elif score >= 70: return "중 (Good)"
        else: return "하 (Needs Effort)"
    except:
        return "중 (Good)"

def get_combined_objective(book, units_list):
    return DEFAULT_OBJECTIVE

def convert_achievement_to_text(rating, objective, name):
    if "상" in rating: return f"이번 달 과정을 완벽하게 마스터했습니다. 개념에 대한 깊이 있는 이해를 바탕으로 실전 오답이 거의 없을 뿐만 아니라, 응용 문장 구사력까지 훌륭하게 발휘하는 탁월한 성취도를 증명해 보였습니다."
    elif "중" in rating: return f"이번 달 과정을 성실하게 이수했습니다. 전반적인 개념 구조를 올바르게 잘 다져두었으며, 디테일 교정과 지속적인 반복 훈련을 통해 성취도의 정교함을 한 단계 더 끌어올리는 중입니다."
    else: return f"이번 달 학습의 핵심 목표에 대해 차근차근 개념을 빌드업해 가는 단계입니다. 우리 {name}가 해당 규칙을 온전히 자기 것으로 소화할 수 있도록, 학원 수업 전후 밀착 클리닉과 누적 오답 보완을 통해 틈새를 촘촘하게 채워가겠습니다."

UNDERSTAND_TEXTS = {"상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.", "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.", "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간과 복습 훈련이 조금 더 필요한 상태입니다."}
PRESENT_TEXTS = {"상 (Excellent)": "질문에 대한 발표와 참여도가 적극적이며, 자신감 넘치는 목소리로 반 전체 수업 분위기를 주도합니다.", "중 (Good)": "선생님의 질문에 성실하게 답변하며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다.", "하 (Needs Effort)": "내용을 알고 있더라도 발표 시 다소 수줍어하는 경향이 있어, 적극성을 끌어올리도록 격려 중입니다."}
FOCUS_TEXTS = {"상 (Excellent)": "수업 시간 내내 흔들림 없는 높은 몰입도를 보여주며, 지시 사항을 정확하게 이행하는 집중력이 돋보입니다.", "중 (Good)": "기본적인 수업 집중력을 잘 유지하고 있으며, 흐트러짐 없이 강사의 설명에 귀를 기울입니다.", "하 (Needs Effort)": "간혹 집중력이 흐려지는 순간이 관찰되어, 1:1 대면 질문과 밀착 케어를 통해 주의를 환기시키고 있습니다."}

# 파닉스 진단 DB 고급화 반영
DIAGNOSIS_DB = {
    "Phonics (파닉스)": {
        "유사 알파벳 형태 혼동": "대부분의 알파벳은 잘 인지하고 있으나, 간혹 모양이 비슷한 'b'와 'd', 'p'와 'q'를 헷갈리는 모습이 보입니다. 시각적인 단서나 쓰기 연습을 통해 헷갈리는 알파벳을 정확히 구별하고 내면화할 수 있도록 지도하겠습니다.",
        "단모음 소리 구별 (a/e/i)": "자음의 소리는 잘 인지하나, 단모음(특히 'a'와 'e', 'e'와 'i')의 미세한 소리 차이를 구별하는 데 어려움을 느낄 때가 있습니다. 입 모양을 비교하며 정확한 모음 소리를 내고 듣는 연습을 강화하겠습니다.",
        "블렌딩(음가 조합) 속도 저하": "개별 알파벳의 소리는 정확히 알고 있지만, 이를 자연스럽게 연결하여 하나의 단어로 읽어내는 '블렌딩' 과정에서 시간이 조금 걸립니다. 소리를 끊지 않고 천천히 이어서 발음하는 훈련을 꾸준히 진행하겠습니다.",
        "첫 글자만 보고 유추하는 습관": "단어를 읽을 때 끝까지 조합하지 않고, 첫 글자나 옆의 그림만 보고 짐작해서 읽으려는 경향이 있습니다. 손가락으로 글자를 하나씩 짚어가며 끝까지 정확하게 읽는 습관을 들이도록 돕겠습니다.",
        "불규칙 사이트 워드 인지 부족": "파닉스 규칙이 적용되지 않는 자주 쓰이는 단어(the, is 등)를 파닉스 규칙대로 읽으려다 문장 읽기에서 막히는 경우가 있습니다. 눈으로 바로 보고 읽어내는 '사이트 워드' 반복 플래시카드 학습을 병행하겠습니다.",
        "유사 발음 조음 위치 혼동 (v/b, f/p)": "우리말에 없는 발음인 'v/b', 'f/p', 'r/l' 소리를 구별하거나 직접 발음할 때 조음 위치를 혼동하는 모습이 보입니다. 거울을 활용해 혀의 위치와 입술 모양을 정확하게 잡는 연습을 하겠습니다.",
        "알파벳 쓰기 획순 및 선 맞추기": "알파벳을 쓸 때 획순이 틀리거나, 영어 4선 노트 기준선에 맞게 쓰는 것을 아직 어려워합니다. 바른 글씨체를 형성하기 위해 선에 맞춰 쓰는 소근육 연습을 꼼꼼히 지도하겠습니다.",
        "거울 글씨 (좌우 반전 오류)": "간혹 's', 'j', 'z' 같은 특정 알파벳을 좌우 반전하여 쓰는 '거울 글씨' 현상이 나타납니다. 이 시기 아이들에게 흔한 발달 과정이므로, 지속적인 워크시트 연습을 통해 자연스럽게 교정해 나가겠습니다.",
        "긴 단어에 대한 두려움 (Chunking 필요)": "알파벳이 여러 개 모인 긴 단어를 보면 지레 겁을 먹고 스스로 읽어보기 전에 포기하려는 모습이 있습니다. 긴 단어를 두 부분으로 쪼개어 읽는 방법을 알려주어 성취감과 자신감을 심어주겠습니다.",
        "틀릴까 봐 목소리가 작아지는 현상": "스스로 큰 소리 내어 읽어보는 발화 연습이 중요하지만, 틀릴까 봐 목소리가 작아지는 경향이 있습니다. 학원에서도 격려를 아끼지 않겠으니, 댁에서도 아이가 자신 있게 읽을 수 있도록 많은 응원 부탁드립니다."
    },
    "Reading (독해/리딩)": {"글의 메인 아이디어(주제) 파악 어려움": "지문을 읽은 후 스스로 한 줄 제목을 달아보거나 중심 문장을 찾아내는 훈련을 통해, 글의 거시적인 흐름을 짚어내는 능력을 키우겠습니다.", "세부 내용 찾기 실수": "문제를 먼저 분석한 뒤 지문에서 단서를 역추적하는 스캐닝 기술을 보완하여 실전 오답률을 낮추겠습니다."},
    "Grammar (문법)": {"be동사와 일반동사 쓰임 혼동": "두 동사의 핵심 차이점을 직관적으로 인지시키고, 문장 구조 드릴 학습을 강화하겠습니다."},
    "Writing (영작)": {"대소문자 및 문장 부호 누락": "글쓰기의 기본인 문장 부호 규칙을 강조하고, 작성을 마친 문장을 스스로 피드백하며 정교함을 기르도록 지도하겠습니다."}
}

TRAITS_CATEGORIES = {
    "🥇 우수 학생 추천 (도약과 주도성 칭찬)": ["스피킹과 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여하고, 배운 내용을 완전히 자기 것으로 만드는 흡수력이 뛰어납니다.", "자기주도적 학습 능력이 탁월하여 과제 완성도가 매우 높고, 반 전체의 학업 분위기를 긍정적으로 주도합니다."],
    "🥈 보통 학생 추천 (성실함과 안정적 성장 칭찬)": ["수업 내용을 차분하고 성실하게 따라오며, 지도를 통해 기본적인 개념을 안정적으로 소화해 내는 뚝심이 있습니다.", "학습 태도가 매우 올바르며 피드백을 주면 스펀지처럼 흡수하여, 틀린 문제를 끝까지 해결하려는 끈기가 돋보입니다."],
    "🥉 격려가 필요한 학생 추천 (기특한 노력과 잠재력 칭찬)": ["어려운 과제나 생소한 개념이 주어지더라도 포기하지 않고 끝까지 성실하게 완료하려는 예쁜 태도와 기특한 도전 정신을 가지고 있습니다.", "수업 시간 동안 차분하고 정돈된 태도로 강사의 설명에 성실히 귀를 기울이며, 조금씩 자신만의 학습 페이스를 단단하게 빌드업해 가고 있습니다."]
}

# 수준별 격려 템플릿 대폭 추가
TEACHER_TEMPLATES = {
    "선택 안 함 (아래 직접 입력)": "",
    "🌱 [기초/격려] 과정 중심의 응원 (태도 칭찬)": "지금 당장 눈에 보이는 큰 점수보다 중요한 건 {name}(이)가 포기하지 않고 영어를 대하는 태도입니다. 기초를 다지는 지금의 시간이 훗날 {name}(이)가 영어를 즐길 수 있는 가장 든든한 밑거름이 될 거예요. {name}(이)의 속도에 맞춰, 저도 포기하지 않고 끝까지 함께 걷겠습니다.",
    "🌱 [기초/격려] 작은 성취 칭찬 (자신감 부여)": "오늘 수업 중 {name}(이)가 스스로 문장을 읽어낸 순간이 있었습니다. 그 작은 성공들이 모여 큰 자신감이 될 거예요. 지금은 틀리는 것이 너무나 당연한 과정이니, {name}(이)가 주눅 들지 않고 계속 도전할 수 있도록 댁에서도 따뜻한 응원 부탁드립니다.",
    "🌱 [기초/격려] 공감과 믿음 전달": "영어를 처음 익히며 {name}(이)가 겪는 어려움들을 저 또한 충분히 공감하고 있습니다. 아이가 어려워하는 부분을 하나씩 세심하게 채워가다 보면, 어느새 영어와 친구가 되어있는 {name}(이)를 발견하실 거예요. 학부모님의 믿음이 아이에게는 무엇보다 큰 힘이 됩니다.",
    
    "🌿 [중간/도약] 성실함 인정과 확신": "수업에 임하는 {name}(이)의 모습에서 매달 깊은 신뢰를 느낍니다. 성실함은 그 무엇보다 강력한 실력입니다. 지금처럼 기본기를 착실히 다져간다면, 머지않아 더 높은 도약의 순간을 맞이하게 될 것이라 확신합니다.",
    "🌿 [중간/도약] 한 단계 성장 가능성": "우리 {name}(이)는 지금 한 단계 더 성장하기 위해 힘차게 날갯짓하는 중입니다. 조금만 더 힘을 내서 지금의 노력을 유지한다면, 더 복잡한 문장도 자유롭게 다루는 모습을 보실 수 있을 거예요. 제가 아이의 성장을 곁에서 가장 가까이 돕겠습니다.",
    "🌿 [중간/도약] 긍정적 학습 습관 칭찬": "예전보다 학습 태도가 훨씬 의젓해졌습니다. 스스로 공부하려는 의지가 눈에 띄게 좋아진 점이 무척 대견하네요. 지금처럼 올바른 학습 습관을 차곡차곡 쌓아가다 보면, 영어 공부가 {name}(이)에게 더 즐거운 도전이 될 것입니다.",
    
    "🌳 [우수/심화] 더 높은 곳을 향한 심화 도전": "현재 실력에 안주하지 않고 더 깊이 있는 내용을 이해하려는 {name}(이)의 열정이 참 멋집니다. 이제는 조금 더 난도가 높은 심화 과정으로 아이의 가능성을 넓혀보려 합니다. 아이의 잠재력이 더 넓은 세상에서 활짝 피어날 수 있도록 이끌겠습니다.",
    "🌳 [우수/심화] 문제 해결 능력과 자부심 고취": "오늘 수업에서 {name}(이)가 보여준 문제 해결 능력은 저도 감탄할 정도였습니다. 영어를 단순히 지식으로 습득하는 것을 넘어, 자신의 생각을 조리 있게 표현하는 단계로 멋지게 진입하고 있네요. 아이가 영어에 대해 큰 자부심을 느낄 수 있도록 아낌없이 칭찬해 주세요.",
    "🌳 [우수/심화] 훌륭한 자기 주도 학습 태도": "스스로 무엇을 모르는지 파악하고 질문하는 모습이 무척 훌륭합니다. 자기 주도적으로 학습하는 지금의 모습은 영어뿐만 아니라 아이의 모든 학습 과정에서 가장 큰 자산이 될 거예요. 지금처럼 꾸준히 자기만의 속도로 정상을 향해 갈 수 있게 힘껏 격려하겠습니다."
}

# 고급 클로징 멘트 DB
CLOSING_MENT_DB = {
    "🤝 [협력 강조형] 신뢰와 파트너십을 강조할 때": "아이의 성장은 강사인 저와 학부모님의 따뜻한 관심이 함께 모일 때 더욱 빛이 난다고 믿습니다. 우리 아이가 영어를 통해 더 넓은 세상을 꿈꿀 수 있도록, 저 또한 최선을 다해 지도하겠습니다. 늘 믿고 맡겨주셔서 진심으로 감사합니다.",
    "🌱 [성장 중시형] 과정의 소중함을 강조할 때": "시험 점수라는 결과보다, 아이가 영어를 대하는 태도가 얼마나 긍정적으로 변화하고 있는지에 더 주목해 주시면 좋겠습니다. 그 성장의 과정을 곁에서 꼼꼼히 기록하고 이끌겠습니다. 아이가 즐겁게 영어를 즐길 수 있도록 가정에서도 많은 격려 부탁드립니다.",
    "🛡️ [안심 전달형] 정성과 책임을 강조할 때": "매시간 아이들의 눈높이에서 가장 필요한 것이 무엇인지 고민하며 수업하고 있습니다. 아이가 영어 때문에 힘들지 않게, 오히려 영어로 자신감을 얻을 수 있도록 세심하게 지도하겠습니다. 시험 결과에 대해 궁금하신 점은 언제든 편하게 연락해 주세요. 감사합니다."
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

# --- 4. 교재별 성적표 및 다중 단원 선택 ---
st.subheader("📚 2. 교재별 성적표 입력 (100점 만점 기준)")
if "Phonics" in selected_level:
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
    with col_m2: main_units = st.multiselect("평가 단원", UNITS, key="main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 90", key="main_score")
    if main_score:
        st.caption(f"💡 자동 평가: **'{get_rating_from_score(main_score)}'**")
    sub_book, sub_units, sub_score = None, [], ""
else:
    st.markdown("**[Main Book 성적]**")
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("교재 선택", BOOK1_LIST, key="reg_main")
    with col_m2: main_units = st.multiselect("평가 단원", UNITS, key="reg_main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 85", key="reg_main_score")
    if main_score:
        st.caption(f"💡 자동 평가: **'{get_rating_from_score(main_score)}'**")
        
    st.markdown("**[Sub Book 성적]**")
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1: sub_book = st.selectbox("교재 선택", ["선택안함"] + BOOK2_LIST, key="reg_sub")
    with col_s2:
        if sub_book != "선택안함": sub_units = st.multiselect("평가 단원", UNITS, key="reg_sub_unit")
        else: sub_units = []; st.write("부교재 없음")
    with col_s3:
        if sub_book != "선택안함": sub_score = st.text_input("점수", placeholder="예: 80", key="reg_sub_score")
        else: sub_score = ""
    if sub_book != "선택안함" and sub_score:
        st.caption(f"💡 자동 평가: **'{get_rating_from_score(sub_score)}'**")

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

st.subheader("✍️ 5. 담당 강사 개별 피드백 및 클로징")
selected_template = st.selectbox("📌 마법의 코멘트 템플릿 선택 (수준별 격려)", list(TEACHER_TEMPLATES.keys()))
teacher_custom_feedback = st.text_area("✍️ 추가 개별 코멘트 (선택 사항)", placeholder="템플릿 내용 외에 덧붙이고 싶은 말씀이 있다면 자유롭게 입력해 주세요.")
st.markdown("---")
selected_closing = st.selectbox("💌 안내문 클로징 멘트 선택", list(CLOSING_MENT_DB.keys()))

# --- 5. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 프리미엄 피드백 생성"):
    if not selected_student:
        st.error("학생을 선택해 주세요.")
    else:
        main_units_str = ", ".join(main_units) if main_units else "단원 미지정"
        score_report = f"· {main_book} ({main_units_str}) : {main_score}점 / 100점"
        
        main_rating_val = get_rating_from_score(main_score)
        main_objective_val = get_combined_objective(main_book, main_units)
        objective_narrative = f"✔ [Main] {convert_achievement_to_text(main_rating_val, main_objective_val, selected_en_name)}"
        
        if sub_book and sub_book != "선택안함": 
            sub_units_str = ", ".join(sub_units) if sub_units else "단원 미지정"
            score_report += f"\n· {sub_book} ({sub_units_str}) : {sub_score}점 / 100점"
            
            sub_rating_val = get_rating_from_score(sub_score)
            sub_objective_val = get_combined_objective(sub_book, sub_units)
            objective_narrative += f"\n\n✔ [Sub] {convert_achievement_to_text(sub_rating_val, sub_objective_val, selected_en_name)}"
            
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
                    care_plan_text += f"· 완벽한 도약을 위해 {area}의 [{w}] 부분을 미세하게 터치해 주는 단계가 필요합니다. 학원에서는 이를 위해 {plan}\n"
        if not care_plan_text: care_plan_text = f"· 현재 {selected_en_name}(이)는 모든 영역의 밸런스를 예쁘게 유지하고 있습니다.\n"

        custom_processed_text = ""
        if selected_template != "선택 안 함 (아래 직접 입력)":
            custom_processed_text += TEACHER_TEMPLATES[selected_template].format(name=selected_en_name) + " "
        if teacher_custom_feedback:
            custom_processed_text += refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 한 달간 {selected_en_name}(이)를 지도하며 선생님이 느낀 점은, 아이가 지닌 가능성과 성실함이 매우 기특하다는 것입니다. 앞으로도 든든한 페이스메이커가 되겠습니다."
        
        # 마지막 클로징 멘트
        final_closing_ment = CLOSING_MENT_DB[selected_closing]

        st.session_state.generated_feedback = f"""
안녕하세요, {selected_en_name} 학부모님! 😊
큐브어학원에서 이번 한 달간 {selected_en_name}({selected_kr_name}) 학생과 함께 힘차게 달려온 학습 여정과 성장을 담은 월말평가 리포트를 전해드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 영역별 평가 결과 (100점 만점 기준):
{score_report}


[1. 핵심 단원별 목표 성취 리포트]
단순 정량 평가를 넘어, 이번 달 아이가 배운 구체적인 목표 달성도 분석입니다.
{objective_narrative}


[2. 학생 성향 및 긍정 태도 리포트]
이번 한 달 동안 학원에서 세심하게 관찰한 {selected_en_name}의 다이어리입니다.
{positive_section}


[3. 완벽한 도약을 위한 단 하나의 디테일 & 큐브 케어 플랜]
다음 레벨로의 완벽한 점프와 빈틈없는 영어 날개를 달아주기 위한 큐브만의 촘촘한 개별 솔루션입니다.
{care_plan_text}

[4. 담당 강사 개별 밀착 소견]
우리 {selected_en_name} 는 {custom_processed_text.strip()}


{final_closing_ment}

- 큐브어학원 드림 -
        """.strip()
        st.success("큐브어학원만의 명품 피드백 메세지가 완성되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=800)
