import streamlit as st
from streamlit_gsheets import GSheetsConnection

# --- 앱 기본 설정 ---
st.set_page_config(page_title="월말평가 피드백 시스템", page_icon="🏫", layout="centered")
st.title("🏫 학원 월말평가 피드백 자동화")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 🚨 원장님 시트에 맞춰 탭 이름을 "students"로 완벽하게 고쳤습니다!
    df = conn.read(worksheet="students", ttl="10m") 
    df = df.dropna(subset=['레벨', '한국어이름']) 
except Exception as e:
    st.error("구글 시트를 불러오는 데 실패했습니다. 스트림릿 설정(Secrets)에 링크가 잘 들어갔는지 확인해 주세요.")
    st.stop()

# --- 교재 리스트 정의 ---
PHONICS_BOOKS = ["Smart Phonics 1", "Smart Phonics 2", "Smart Phonics 3", "Phonics Monster"]
REGULAR_BOOKS = [
    "Bricks Reading 100", "Subject Link 1", "Grammar Space Beginner", 
    "Toefl Primary Step 1", "Reading Expert 1", "Grammar Zone", "Listening Expert"
]

# --- 2. 학생 및 레벨 선택 ---
st.subheader("1. 학생 및 레벨 선택")
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
    # '영어이름' 열에서 데이터 가져오기
    en_name_row = filtered_df[filtered_df['한국어이름'] == selected_kr_name]['영어이름'].values
    if len(en_name_row) > 0:
        selected_en_name = en_name_row[0]

# --- 3. 학습 및 평가 결과 ---
st.subheader("2. 학습 및 평가 결과")

if "Phonics" in selected_level:
    main_books = PHONICS_BOOKS
    sub_books = ["(파닉스는 메인 교재만 진행)"]
    sub_disabled = True
else:
    main_books = REGULAR_BOOKS
    sub_books = ["없음"] + REGULAR_BOOKS
    sub_disabled = False

col_b1, col_b2 = st.columns(2)
with col_b1:
    book1 = st.selectbox("메인 학습 교재", main_books)
with col_b2:
    book2 = st.selectbox("부교재 (선택)", sub_books, disabled=sub_disabled)

units = st.text_input("평가 단원", placeholder="예: Unit 1 ~ Unit 3")

col_s1, col_s2 = st.columns(2)
with col_s1:
    score = st.text_input("학생 점수", placeholder="예: 85점")
with col_s2:
    avg_score = st.text_input("반 평균 점수", placeholder="예: 78점")

# --- 4. 강사 관찰 및 세부 분석 ---
st.subheader("3. 강사 관찰 및 세부 분석")
traits = st.multiselect(
    "아이의 학습 특성 (복수 선택)",
    [
        "이론과 개념은 잘 이해하나, 실전 시험(문제풀이)에서 실수가 나옴",
        "스피킹(말하기)에는 자신감이 넘치나, 쓰기(Writing)와 스펠링이 다소 약함",
        "수업 집중도가 높고 묻는 질문에 대답을 아주 잘함",
        "이해력이 빠르고 내준 과제(숙제)를 매우 성실하게 수행함",
        "단어 암기를 다소 어려워하나, 포기하지 않고 꾸준히 노력하는 태도가 훌륭함"
    ]
)
weak_points = st.text_area("틀린 부분 및 취약점", placeholder="예: 과거시제 불규칙 동사 변화를 헷갈려 함")
custom_comment = st.text_area("선생님 추가 코멘트", placeholder="예: 다음 학기에는 영작 연습 비중을 늘리겠습니다.")

# --- 5. 피드백 생성 버튼 ---
if st.button("✨ 전문 피드백 자동 작성하기", type="primary"):
    if not selected_kr_name:
        st.error("학생을 선택해주세요!")
    else:
        st.success("피드백이 완성되었습니다. 아래 내용을 복사하여 발송하세요.")
        
        display_name = f"{selected_kr_name}({selected_en_name})" if selected_en_name else selected_kr_name
        display_books = book1 if "Phonics" in selected_level or book2 == "없음" else f"{book1}, {book2}"
        
        traits_text = ""
        if traits:
            traits_text = "\n[선생님 관찰 코멘트]\n평소 학원에서 지켜본 " + selected_kr_name + " 학생은 다음과 같은 긍정적인 특징을 보이고 있습니다.\n- " + "\n- ".join(traits) + "\n"
        
        feedback_text = f"""
안녕하세요, {display_name} 학부모님. 담당 강사입니다.
이번 달 {selected_kr_name} 학생의 학습 현황 및 월말평가 결과를 안내해 드립니다.

■ 현재 레벨: {selected_level}
■ 학습 교재: {display_books}
■ 평가 단원: {units}
■ 평가 결과: {score} (반 평균: {avg_score})

[학습 평가 및 취약점 분석]
이번 평가를 통해 {selected_kr_name}의 성취도를 점검한 결과, 전반적인 학습 능력이 우수합니다만 일부 보완이 필요한 부분이 파악되었습니다. 
{weak_points}
{traits_text}
[다음 학기 학습 방향]
{custom_comment if custom_comment else "다음 진도에서는 이번에 부족했던 부분을 집중적으로 복습하며 탄탄하게 기초를 다질 예정입니다."}

가정에서도 {selected_kr_name} 학생이 자신감을 가질 수 있도록 아낌없는 칭찬과 격려 부탁드립니다. 감사합니다.
        """
        st.text_area("완성된 피드백", value=feedback_text.strip(), height=450)
