import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="월말평가", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v22.0")
st.markdown("구글 시트 연동형 교재 DB 및 프리미엄 밀착 피드백 엔진 (실속형)")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 

@st.cache_data(show_spinner="구글 시트에서 학생 명단을 연결 중입니다...")
def load_student_data(url):
    csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&headers=1&sheet=students"
    data = pd.read_csv(csv_url)
    data.columns = data.columns.str.strip()
    if '레벨' not in data.columns or '한국어이름' not in data.columns:
        raise ValueError(f"시트에서 '레벨' 또는 '한국어이름' 열을 찾지 못했습니다.")
    data = data.dropna(subset=['레벨', '한국어이름'])
    return data
        
@st.cache_data(show_spinner="구글 시트에서 교재 학습목표 DB를 동기화 중입니다...")
def load_book_data(url):
    try:
        csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&headers=1&sheet=books"
        book_df = pd.read_csv(csv_url)
        book_df.columns = book_df.columns.str.strip()
        book_df['교재'] = book_df['교재'].astype(str).str.strip()
        book_df['유닛'] = book_df['유닛'].astype(str).str.strip()
        book_df['학습목표'] = book_df['학습목표'].astype(str).str.strip()
        return book_df
    except Exception as e:
        st.warning(f"교재 DB 연결 오류: {e}")
        return pd.DataFrame(columns=['교재', '유닛', '학습목표'])

try:
    df = load_student_data(sheet_url)
    df_books = load_book_data(sheet_url)
except Exception as e:
    st.error(f"구글 시트 연결 에러가 발생했습니다. (상세 에러: {e})")
    st.stop()

if "generated_feedback" not in st.session_state:
    st.session_state.generated_feedback = ""

# --- 2. 데이터 및 템플릿 정의 (전문성 & 랜덤화) ---
PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = ["Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4", "English Trophy 3","English Trophy 4","English Trophy 5","English Trophy 6", "Reading Trophy 1", "Reading Trophy 2", "Reading Trophy 3"]
BOOK2_LIST = ["Writing Monster 1", "Bricks Grammar B1", "Bricks Grammar 1"]
UNITS = [f"Unit {i}" for i in range(1, 13)]
MONTHS = [f"{i}월" for i in range(1, 13)]

PHONICS_TARGETS_DB = {
    "Jungle Phonics 1": [chr(i) for i in range(65, 91)], 
    "Jungle Phonics 2": ["ad", "at", "an", "am", "ap", "ag", "ed", "en", "et", "ig", "in", "ip", "og", "op", "ot", "ug", "un", "ut"], 
    "Jungle Phonics 3": ["ade", "ate", "ake", "ame", "ave", "ide", "ike", "ine", "ive", "ole", "one", "ope", "ute", "une"], 
    "Jungle Phonics 4": ["bl", "cl", "fl", "pl", "gl", "sl", "br", "cr", "fr", "pr", "gr", "tr", "sm", "sn", "sp", "st", "sw", "ch", "sh", "th", "wh"] 
}

# 태도 멘트 다변화 (리스트형)
UNDERSTAND_TEXTS = {
    "상 (Excellent)": [
        "새로운 언어적 개념을 직관적으로 흡수하며, 배운 내용을 자신의 언어로 재구성해 내는 뛰어난 이해력을 보여줍니다.",
        "진행되는 수업의 핵심 논리를 빠르고 정확하게 파악하여, 진도가 막힘없이 매끄럽게 진행되고 있습니다."
    ],
    "중 (Good)": [
        "수업의 흐름을 안정적으로 따라가며, 낯선 개념을 차분하게 자신의 지식으로 내재화하는 과정을 훌륭히 수행하고 있습니다.",
        "기본적인 개념을 안정적으로 소화해 내며, 지도를 통해 점진적이고 탄탄하게 실력을 쌓아가고 있습니다."
    ],
    "하 (Needs Effort)": [
        "개념을 온전히 체화하기 위해 반복과 다지기가 필요한 시기입니다. 1:1 맞춤형 피드백을 통해 이해의 공백을 꼼꼼히 채워가고 있습니다."
    ]
}

PRESENT_TEXTS = {
    "상 (Excellent)": [
        "단순한 정답 찾기를 넘어 자신의 생각을 자신감 있게 영어로 발화하며, 반 전체의 학업 분위기를 주도합니다.",
        "질문에 대한 반응 속도가 빠르고 참여도가 적극적이며, 롤플레이 등 표현 활동에서 두각을 나타냅니다."
    ],
    "중 (Good)": [
        "주어진 질문에 성실하고 명확하게 답변하며, 그룹 활동이나 롤플레이에서도 자신의 역할을 책임감 있게 수행해 냅니다.",
        "선생님의 질문에 안정적으로 대답하며, 본인에게 주어진 학습 목표를 무리 없이 도달해 냅니다."
    ],
    "하 (Needs Effort)": [
        "아직은 영어로 자신을 표현하는 것에 다소 조심스러운 모습이지만, 작은 성공 경험을 지속적으로 제공하여 적극성을 끌어올리고 있습니다."
    ]
}

FOCUS_TEXTS = {
    "상 (Excellent)": [
        "수업의 처음부터 끝까지 밀도 높은 몰입감을 유지하며, 강사의 설명 하나하나를 놓치지 않는 탁월한 집중력을 지녔습니다.",
        "학습 지시 사항을 정확하게 이행하며, 흔들림 없는 태도로 스스로의 학습 목표에 도달하는 집중력이 돋보입니다."
    ],
    "중 (Good)": [
        "학습에 필요한 적절한 긴장감과 집중력을 잘 유지하며, 수업 중 제시되는 가이드라인을 성실하고 흔들림 없이 이행합니다.",
        "기본적인 수업 집중력을 안정적으로 유지하며, 수업의 흐름에 맞춰 차분하게 학습에 임하고 있습니다."
    ],
    "하 (Needs Effort)": [
        "학습 내용이 다소 어려워질 때 주의력이 흩어지는 경향이 있어, 잦은 질문과 대면 케어를 통해 수업에 다시 몰입할 수 있도록 지도 중입니다."
    ]
}

TRAITS_CATEGORIES = {
    "🥇 [주도성과 흡수력] 메타인지가 뛰어난 학생": [
        "스피킹과 리스닝에서 탁월한 언어적 감각을 보이며 능동적으로 수업에 참여하고, 배운 내용을 완전히 자기 것으로 만드는 스펀지 같은 흡수력이 뛰어납니다.", 
        "자기주도적 학습 능력이 탁월하여 과제 완성도가 매우 높고, 학구적인 태도로 반 전체의 긍정적인 시너지를 이끌어냅니다."
    ],
    "🥈 [성실함과 끈기] 안정적으로 성장하는 학생": [
        "수업 내용을 차분하고 진지하게 따라오며, 지도를 통해 기본적인 개념을 단단하게 소화해 내는 묵직한 뚝심이 있습니다.", 
        "학습 태도가 매우 올바르며 피드백을 적극적으로 수용하여, 한 번 틀린 문제를 끝까지 해결하려는 지적 끈기가 돋보입니다."
    ],
    "🥉 [잠재력과 도전 정신] 격려로 빛을 발하는 학생": [
        "어려운 과제나 생소한 문법이 주어지더라도 쉽게 포기하지 않고 끝까지 성실하게 부딪혀보려는 기특한 도전 정신을 가지고 있습니다.", 
        "차분하고 정돈된 태도로 강사의 설명에 귀를 기울이며, 타인과 비교하지 않고 묵묵히 자신만의 단단한 학습 페이스를 만들어 가고 있습니다."
    ]
}

DIAGNOSIS_DB = {
    "Phonics (파닉스)": {
        "유사 알파벳 형태 혼동": "모양이 비슷한 'b/d', 'p/q' 등의 구별에 시각적 단서를 추가하여 정확히 내면화할 수 있도록 지도하고 있습니다.",
        "단모음 소리 구별": "단모음(a/e/i)의 미세한 소리 차이 구별 훈련을 위해 입 모양 비교 및 반복 청취 연습을 강화하고 있습니다.",
        "블렌딩 속도": "알파벳 개별 소리는 잘 인지하나 단어로 연결하는 블렌딩 속도 향상을 위해 끊지 않고 이어서 발음하는 훈련을 진행 중입니다.",
        "사이트 워드 인지": "규칙이 적용되지 않는 필수 사이트 워드의 직관적 인지력을 높이기 위해 반복 플래시카드 학습을 병행하고 있습니다."
    },
    "Course Book (코스북/회화)": {
        "실생활 발화 유도": "학습한 문장 구조를 실제 상황에서 스스로 꺼낼 수 있도록 롤플레이와 1:1 발화 유도 비중을 높이고 있습니다.",
        "어휘 인지 및 체화": "새로운 어휘에 대한 노출 빈도를 높여, 억지로 외우기보다 문맥 속에서 자연스럽게 뜻을 유추하고 체화하도록 지도합니다.",
        "복습 습관 형성": "수업 시간의 긍정적인 집중력이 집에서도 이어져 완전한 본인의 지식이 되도록 당일 복습의 중요성을 다독이고 있습니다."
    },
    "Reading (독해/리딩)": {
        "세부 정보 스캐닝": "글의 전체 흐름은 잘 파악하나, 문제를 푸는 단서가 되는 세부 정보를 꼼꼼하게 찾아내는 스캐닝 훈련을 보완 중입니다.",
        "어휘 문맥 추론": "모르는 단어가 나왔을 때 당황하지 않고, 앞뒤 문맥을 통해 의미를 논리적으로 유추해 보는 독해 스킬을 지도하고 있습니다.",
        "문장 구조 분석": "문제를 빨리 푸는 것보다 문장의 주어와 동사를 정확히 끊어 읽고 구조를 바르게 이해하는 정확도 훈련에 집중하고 있습니다."
    },
    "Grammar (문법)": {
        "규칙의 실전 적용": "이해한 문법 개념을 다양한 변형 문제에 직접 대입해 보며, 머리로 아는 것을 실전 감각으로 연결하는 훈련을 진행합니다.",
        "잦은 실수 오답 교정": "문법의 뼈대는 잘 잡혀 있으나 특정 규칙에서 발생하는 반복적인 자잘한 실수를 줄이기 위해 밀착 오답 교정을 실시합니다.",
        "복합 문장 확장": "기본 규칙을 활용하여 길이가 길고 복잡한 문장 구조도 유연하게 분석하고 영작할 수 있도록 심화 대비를 진행합니다."
    },
    "General (공통/학습태도)": {
        "문제 해결 끈기 부족": "어려운 문제 앞에서 멈추기보다, 스스로 아는 선까지 끝까지 풀어보려는 도전 의식을 심어주기 위해 작은 칭찬과 성취를 독려합니다.",
        "단순 옮겨 적기 실수": "내용은 잘 알고 있으나 보기 단어를 옮겨 적을 때 발생하는 꼼꼼함 부족을 해결하기 위해, 풀이 후 재점검 습관을 지도합니다.",
        "어휘 기초 체력 보완": "독해와 문법의 뼈대가 되는 기본 어휘량 확장이 필요하여, 잦은 노출과 반복 테스트를 통해 단어 기초 체력을 끌어올리고 있습니다."
    }
}

TEACHER_TEMPLATES = {
    "선택 안 함 (아래 직접 입력)": [""],
    "🌱 [기초/격려] 과정 중심의 응원": [
        "지금 당장 눈에 보이는 점수보다 더 가치 있는 것은 {name}(이)가 영어를 대하는 '진지하고 예쁜 태도'입니다. 기초의 뿌리를 튼튼히 내리는 지금의 시간이 훗날 {name}(이)가 거침없이 영어를 구사할 수 있는 가장 든든한 밑거름이 될 것입니다.",
        "새로운 언어를 배우는 과정에서 {name}(이)가 보여주는 맑은 호기심과 노력에 큰 박수를 보냅니다. 당장의 결과에 집중하기보다, 아이가 영어에 흥미를 잃지 않고 꾸준히 나아갈 수 있도록 따뜻하고 든든한 페이스메이커가 되겠습니다."
    ],
    "🌿 [중간/도약] 성실함 인정과 확신": [
        "수업에 임하는 {name}(이)의 흔들림 없는 성실함에서 매달 깊은 신뢰를 느낍니다. 꾸준함은 그 어떤 화려한 스킬보다 강력한 실력입니다. 지금처럼 기본기를 착실하고 단단하게 다져간다면, 머지않아 폭발적으로 성장하는 도약의 순간을 맞이하게 될 것이라 확신합니다.",
        "어려운 과제가 주어져도 묵묵히 제 몫을 다해내는 {name}(이)의 끈기가 무척 대견합니다. 배운 것을 온전히 자기 것으로 만들어가는 이 단단한 과정이, 앞으로 한 단계 더 높은 영어의 바다로 나아가는 강력한 돛이 되어줄 것입니다."
    ],
    "🌳 [우수/심화] 심화 도전 및 잠재력": [
        "현재의 훌륭한 성취에 안주하지 않고, 더 깊이 있는 언어의 규칙을 탐구하려는 {name}(이)의 열정이 참으로 멋집니다. 이제는 조금 더 지적 호기심을 자극하는 심화 과정으로 아이의 무한한 잠재력을 활짝 피워내겠습니다.",
        "뛰어난 흡수력과 주도적인 학습 태도로 늘 반 전체에 좋은 귀감이 되어주는 {name}(이)입니다. 아이가 가진 탁월한 언어적 감각이 텍스트에만 머물지 않고, 자신의 생각을 논리적으로 거침없이 표현하는 수준까지 확장되도록 밀도 있게 훈련하겠습니다."
    ]
}

CLOSING_MENT_DB = {
    "🤝 [협력 강조형] 신뢰와 파트너십 강조": [
        "아이의 진정한 성장은 학원에서의 밀착 지도와 가정에서의 따뜻한 격려가 완벽한 호흡을 이룰 때 가장 크게 빛납니다. 귀한 자녀를 믿고 맡겨주셔서 진심으로 감사드리며, 매 수업 최선을 다하겠습니다.",
        "가정에서 보내주시는 든든한 믿음과 응원 덕분에 우리 아이가 이달에도 한 뼘 더 성장할 수 있었습니다. 학부모님과 발을 맞추어 아이의 영어 여정을 가장 완벽하게 서포트하겠습니다. 감사합니다."
    ],
    "🌱 [성장 중시형] 과정의 소중함 강조": [
        "평가표에 적힌 숫자의 결과보다, 아이가 영어의 장벽을 허물고 스스로 해내려 노력하는 '성장의 과정'에 더 큰 박수를 보내주시면 좋겠습니다. 가정에서도 아이의 작은 성공들을 듬뿍 칭찬해 주세요.",
        "어제보다 오늘 더 자연스럽게 영어를 입 밖으로 꺼내는 아이의 용기에 주목해 주시기 바랍니다. 이 아름다운 변화의 순간들을 놓치지 않고 꼼꼼히 기록하고 이끌겠습니다. 늘 감사합니다."
    ],
    "🛡️ [안심 전달형] 정성과 책임 강조": [
        "매시간 '우리 아이들에게 지금 가장 필요한 징검다리가 무엇일까'를 치열하게 고민하며 수업에 임하고 있습니다. 영어가 스트레스가 아닌 든든한 무기가 될 수 있도록 정성을 다해 지도하겠습니다.",
        "아이마다 이해하는 속도와 받아들이는 방법이 다름을 인지하고, 한 명 한 명의 눈높이에 맞춘 세심한 지도를 약속드립니다. 평소 아이의 학습 방향에 대해 궁금하신 점이 있다면 언제든 편하게 연락해 주십시오."
    ]
}

def parse_score(score_str):
    try: return int(score_str)
    except: return 90

# --- 3. 사용자 입력 화면 UI 구성 ---
st.subheader("👤 1. 평가 월 및 학생 선택")
col1, col2, col3 = st.columns([1, 1, 2])
with col1: selected_month = st.selectbox("평가 월", MONTHS, index=4) 
with col2: selected_level = st.selectbox("현재 레벨", df['레벨'].unique().tolist())
with col3:
    filtered_df = df[df['레벨'] == selected_level].copy()
    filtered_df['student_label'] = filtered_df['영어이름'].fillna('이름없음').astype(str) + " (" + filtered_df['한국어이름'].astype(str) + ")"
    selected_student = st.selectbox("학생 선택", filtered_df['student_label'].tolist())

selected_en_name, selected_kr_name = "", ""
if selected_student:
    row = filtered_df[filtered_df['student_label'] == selected_student].iloc[0]
    selected_en_name, selected_kr_name = row['영어이름'], row['한국어이름']

# --- 4. 교재별 성적표 및 다중 단원 선택 ---
st.subheader("📚 2. 교재 성적 입력")
is_phonics = "Phonics" in selected_level
primary_units = []

if is_phonics:
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1: primary_book = st.selectbox("주교재", PHONICS_BOOKS)
    with col_p2: test_range = st.selectbox("평가 범위", ["Midterm Test (Unit 1-4)", "Final Test (Unit 1-8)"])
    with col_p3: primary_score = st.text_input("점수", placeholder="예: 90")
    
    phonics_options = PHONICS_TARGETS_DB.get(primary_book, [])
    if test_range == "Final Test (Unit 1-8)":
        primary_units = st.multiselect("학습 타겟", phonics_options, default=phonics_options)
    else:
        primary_units = st.multiselect("학습 타겟", phonics_options, default=phonics_options[:4] if len(phonics_options)>=4 else phonics_options)
    sub_book, sub_units, sub_score = None, [], ""
else:
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1: primary_book = st.selectbox("주교재", BOOK1_LIST)
    with col_p2: primary_units = st.multiselect("평가 단원", UNITS, default=["Unit 1", "Unit 2", "Unit 3"])
    with col_p3: primary_score = st.text_input("점수", placeholder="예: 85")
        
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1: sub_book = st.selectbox("부교재", ["선택안함"] + BOOK2_LIST)
    with col_s2:
        if sub_book != "선택안함": sub_units = st.multiselect("평가 단원 (부교재)", UNITS)
        else: sub_units = []
    with col_s3:
        if sub_book != "선택안함": sub_score = st.text_input("부교재 점수", placeholder="예: 80")
        else: sub_score = ""

# --- 5. 상세 성취도 및 보완점 (실속형 UI) ---
st.markdown("---")
st.subheader("🎯 3. 수업 태도 및 성취 진단")
col5, col6, col7 = st.columns(3)
with col5: rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6: rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7: rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

selected_traits = []
for category_name, traits in TRAITS_CATEGORIES.items():
    selected = st.multiselect(category_name, traits)
    selected_traits.extend(selected)

if is_phonics: available_areas = ["Phonics (파닉스)", "General (공통/학습태도)"]
else: available_areas = ["Course Book (코스북/회화)", "Reading (독해/리딩)", "Grammar (문법)", "Writing (영작)", "General (공통/학습태도)"]

selected_weaknesses = {}
for area in available_areas:
    selected = st.multiselect(f"📌 [{area}] 밀착 케어 항목 선택", list(DIAGNOSIS_DB[area].keys()))
    if selected: selected_weaknesses[area] = selected

# --- 6. 다음 달 진도 및 액션 플랜 (신규 추가) ---
st.markdown("---")
st.subheader("🚀 4. 다음 달 안내 및 Next Step")
next_step_progress = st.text_input("📖 다음 달 주/부교재 진도 안내", placeholder="예: 주교재 Unit 4~6 (과거시제 학습) / 부교재 Unit 2")
next_step_home = st.text_area("🏠 가정 연계 학습 가이드 (홈케어)", placeholder="예: 다음 달부터 시제가 변형됩니다. 가정에서 단어장 예문 3개씩 소리 내어 읽도록 격려 부탁드립니다.")

# --- 7. 선생님 코멘트 ---
st.markdown("---")
st.subheader("✍️ 5. 담당 강사 개별 피드백 및 클로징")
selected_template = st.selectbox("마법의 코멘트 템플릿", list(TEACHER_TEMPLATES.keys()))
teacher_custom_feedback = st.text_area("추가 개별 코멘트 (선택)", placeholder="여기에 작성된 내용은 템플릿 멘트 뒤에 자연스럽게 이어집니다.")
selected_closing = st.selectbox("클로징 안내 멘트", list(CLOSING_MENT_DB.keys()))

# --- 8. 피드백 메세지 생성 로직 (실속형 포맷팅) ---
if st.button("✨ 큐브어학원 월말평가 리포트 생성"):
    if not selected_student or not primary_units:
        st.error("학생 및 평가 단원을 정확히 선택해 주세요.")
    else:
        # 성적 텍스트 정리
        primary_units_str = f"({test_range})" if is_phonics else f"({', '.join(primary_units)})"
        score_report = f"· 주교재 [{primary_book}] {primary_units_str} : {primary_score}점"
        if sub_book and sub_book != "선택안함": 
            sub_units_str = f"({', '.join(sub_units)})" if sub_units else ""
            score_report += f"\n· 부교재 [{sub_book}] {sub_units_str} : {sub_score}점"

        # 성취도 텍스트 (객관적 묘사)
        p_score_num = parse_score(primary_score)
        if p_score_num >= 90:
            achieve_text = f"이번 달 주요 진도 영역의 핵심 개념을 정확히 이해하고 우수한 성취도를 보였습니다."
        elif p_score_num >= 75:
            achieve_text = f"전반적인 진도를 안정적으로 소화하였으나, 일부 응용 영역에서 정교한 복습을 병행하고 있습니다."
        else:
            achieve_text = f"새로운 개념을 익히는 과정에서 다소 시간이 필요하여, 1:1 맞춤형 반복 학습을 통해 이해도를 끌어올리고 있습니다."

        # 태도 텍스트 (랜덤 매칭)
        u_sentence = random.choice(UNDERSTAND_TEXTS[rating_understand])
        p_sentence = random.choice(PRESENT_TEXTS[rating_present])
        f_sentence = random.choice(FOCUS_TEXTS[rating_focus])
        traits_text = "\n- " + "\n- ".join(selected_traits) if selected_traits else ""

        # 케어 플랜 텍스트
        care_plan_text = ""
        if selected_weaknesses:
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    care_plan_text += f"✔️ [{area} - {w}]\n  : {DIAGNOSIS_DB[area][w]}\n\n"
        if not care_plan_text: 
            care_plan_text = "· 현재 모든 영역의 밸런스를 우수하게 유지하며 학습하고 있습니다.\n"

        # Next Step 텍스트
        next_prog = next_step_progress if next_step_progress else "개별 진도표 참조"
        next_home = next_step_home if next_step_home else "지금처럼 학원 과제를 성실히 수행할 수 있도록 가정에서도 많은 격려 부탁드립니다."

        # 코멘트 텍스트
        custom_processed_text = ""
        if selected_template != "선택 안 함 (아래 직접 입력)":
            chosen_template = random.choice(TEACHER_TEMPLATES[selected_template])
            custom_processed_text += chosen_template.format(name=selected_en_name) + " "
        if teacher_custom_feedback:
            custom_processed_text += teacher_custom_feedback.strip()
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 달에도 성실하게 수업에 참여해 준 {selected_en_name}(이)를 크게 칭찬합니다."
        
        final_closing_ment = random.choice(CLOSING_MENT_DB[selected_closing]).format(name=selected_en_name)

        # 최종 출력 폼 (실속형)
        st.session_state.generated_feedback = f"""
[큐브어학원 월말평가 결과지]

■ 학생명: {selected_en_name} ({selected_kr_name})
■ 평가월: {selected_month}
■ 현재반: {selected_level}

1. 교재별 학습 결과
{score_report}


2. 수업 태도 및 성취 브리핑
- [성취] {achieve_text}
- [이해] {u_sentence}
- [참여] {p_sentence}
- [집중] {f_sentence}{traits_text}


3. 영역별 심층 분석 및 케어 계획
{care_plan_text.strip()}


4. 다음 달 학습 안내 (Next Step)
- [진도 안내] {next_prog}
- [가정 연계 학습] {next_home}

--------------------------------------------------
[담당 강사 코멘트]

{custom_processed_text.strip()}

{final_closing_ment}

- 큐브어학원 드림 -
        """.strip()
        st.success(f"데이터 기반 실속형 피드백 메세지가 빌드되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=700)
