import streamlit as st
import pandas as pd

# --- 1. 앱 기본 설정 ---
st.set_page_config(page_title="월말평가 피드백 시스템", page_icon="🏫", layout="centered")

# CSS로 디자인 살짝 보강 (McKinsey 스타일의 깔끔한 폰트 느낌)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; }
    .stSelectbox, .stTextInput, .stTextArea { margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 학원 전용 월말평가 피드백 시스템")
st.markdown("정교한 관찰이 아이의 성장을 만듭니다. 선생님의 진심을 담아주세요.")
st.divider()

# --- 2. 구글 시트 데이터 불러오기 (치트키 주소 방식) ---
# 원장님의 실제 시트 주소를 아래 큰따옴표 안에 넣어주세요.
sheet_url = "https://docs.google.com/spreadsheets/d/1xfm...원장님의_실제_주소" 

try:
    csv_url = sheet_url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=학생명단"
    df = pd.read_csv(csv_url)
    df = df.dropna(subset=['레벨', '한국어이름'])
except:
    st.error("구글 시트 연결을 기다리고 있습니다. 시트 주소가 정확하고 '링크가 있는 모든 사용자'로 설정되었는지 확인해 주세요.")
    st.stop()

# --- 3. 데이터 정의 ---
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
RATINGS = ["상 (Excellent)", "중 (Good)", "하 (Needs Effort)"]
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

# --- 4. 사용자 입력 화면 ---
st.subheader("👤 1. 학생 선택")
col1, col2 = st.columns(2)
with col1:
    levels = df['레벨'].unique().tolist()
    selected_level = st.selectbox("현재 레벨", levels)
with col2:
    filtered_df = df[df['레벨'] == selected_level]
    student_list = filtered_df['한국어이름'].tolist()
    selected_kr_name = st.selectbox("학생 이름", student_list)

# 영어 이름 매칭
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
        main_book = st.selectbox("Main Book (Book1)", BOOK1_LIST)
with col4:
    if "Phonics" in selected_level:
        st.info("파닉스반은 단권으로 진행됩니다.")
        sub_book = None
    else:
        sub_book = st.selectbox("Sub Book (Book2)", BOOK2_LIST)

selected_units = st.multiselect("평가 단원 (다중 선택 가능)", UNITS)
score = st.text_input("평가 점수", placeholder="예: 95점 / 100점")

st.subheader("📊 3. 학습 태도 분석")
col5, col6, col7 = st.columns(3)
with col5:
    rating_understand = st.selectbox("수업 이해도", RATINGS)
with col6:
    rating_present = st.selectbox("발표 및 참여", RATINGS)
with col7:
    rating_focus = st.selectbox("집중도", RATINGS)

st.subheader("🌟 4. 아이 성향 및 개별 의견")
selected_traits = st.multiselect("학생의 주요 학습 성향 (선택)", TRAITS_LIST)
teacher_custom_feedback = st.text_area("선생님의 개별 피드백 (자유 기재)", placeholder="여기에 작성하시는 내용이 메세지 중간에 자연스럽게 포함됩니다.")

# --- 5. 피드백 메세지 생성 로직 ---
if st.button("✨ 프리미엄 학부모 안내 메세지 생성"):
    if not selected_kr_name:
        st.error("학생을 선택해 주세요.")
    else:
        # 상/중/하 점수 -> 자연스러운 문구 변환
        def get_rating_text(r):
            if "상" in r: return "매우 우수함"
            if "중" in r: return "양호하며 안정적임"
            return "보완이 필요하나 점차 나아지는 중"

        units_str = ", ".join(selected_units)
        traits_str = "\n- ".join(selected_traits)
        books_str = main_book if not sub_book else f"{main_book}, {sub_book}"
        
        # 안내 메세지 템플릿
        feedback_msg = f"""
안녕하세요, {selected_kr_name}({selected_en_name}) 학부모님! 😊
이번 달 {selected_kr_name}와(과) 함께한 학습 여정과 월말평가 결과를 안내드립니다.

■ 현재 레벨: {selected_level}
■ 학습 교재: {books_str}
■ 평가 범위: {units_str}
■ 평가 점수: {score}

[학습 태도 리포트]
우리 {selected_kr_name}는 이번 달 수업에서 다음과 같은 모습들을 보여주었습니다.
- 수업 이해도: {get_rating_text(rating_understand)}
- 발표 및 참여도: {get_rating_text(rating_present)}
- 수업 집중도: {get_rating_text(rating_focus)}

[강사 종합 의견]
{selected_kr_name}는 {traits_str if selected_traits else "차분하게 학습을 이어가며 매 수업 성장하는 모습이 인상적입니다."}

{teacher_custom_feedback if teacher_custom_feedback else ""}

선생님이 바라본 {selected_kr_name}는 가능성이 매우 큰 아이입니다. 이번 평가를 통해 파악된 {selected_kr_name}의 강점은 더욱 키우고, 다소 아쉬웠던 부분은 다음 학기 진도에서 꼼꼼한 개별 보강과 반복 학습을 통해 완벽히 채워나갈 예정입니다.

지치지 않고 영어의 재미를 느껴가는 {selected_kr_name}에게 가정에서도 아낌없는 칭찬과 응원 부탁드립니다! 학원에서도 더욱 세심하고 따뜻하게 지도하겠습니다.

감사합니다.

- 담당 강사 및 원장 드림 -
        """
        
        st.success("학부모님용 전문 안내 메세지가 생성되었습니다!")
        st.text_area("복사하여 전송하세요", value=feedback_msg.strip(), height=550)
