import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="월말평가 피드백 시스템", page_icon="🏫", layout="centered")
st.title("🏫 학원 월말평가 피드백 (최종 에러 추적)")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 캐시를 완전히 끄고(ttl=0) 실시간으로 읽어옵니다.
    df = conn.read(worksheet="students", ttl=0) 
    
    st.success("✅ 1단계: 구글 시트 연결 및 파일 읽기 성공!")
    st.write(" 시트에서 읽어온 첫 줄 제목들:", df.columns.tolist())
    
    # 2단계: 데이터 정제 (여기서 에러가 날 가능성이 높습니다)
    df = df.dropna(subset=['레벨', '한국어이름']) 
    st.success("✅ 2단계: 학생 명단 인식 성공!")

except Exception as e:
    st.error("🚨 에러가 발생했습니다! 아래의 영문 메시지를 그대로 복사해서 저에게 알려주세요:")
    st.exception(e) # 에러의 구체적인 원인과 위치를 화면에 다 보여줍니다.
    st.stop()

# --- 이하 원래 기능 코드 ---
PHONICS_BOOKS = ["Smart Phonics 1", "Smart Phonics 2", "Smart Phonics 3", "Phonics Monster"]
REGULAR_BOOKS = ["Bricks Reading 100", "Subject Link 1", "Grammar Space Beginner", "Toefl Primary Step 1", "Reading Expert 1", "Grammar Zone", "Listening Expert"]

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
    en_name_row = filtered_df[filtered_df['한국어이름'] == selected_kr_name]['영어이름'].values
    if len(en_name_row) > 0: selected_en_name = en_name_row[0]

st.subheader("2. 학습 및 평가 결과")
if "Phonics" in selected_level:
    main_books, sub_books, sub_disabled = PHONICS_BOOKS, ["(파닉스는 메인 교재만 진행)"], True
else:
    main_books, sub_books, sub_disabled = REGULAR_BOOKS, ["없음"] + REGULAR_BOOKS, False

col_b1, col_b2 = st.columns(2)
with col_b1: book1 = st.selectbox("메인 학습 교재", main_books)
with col_b2: book2 = st.selectbox("부교재 (선택)", sub_books, disabled=sub_disabled)

units = st.text_input("평가 단원", placeholder="예: Unit 1 ~ Unit 3")
col_s1, col_s2 = st.columns(2)
with col_s1: score = st.text_input("학생 점수", placeholder="예: 85점")
with col_s2: avg_score = st.text_input("반 평균 점수", placeholder="예: 78점")

st.subheader("3. 강사 관찰 및 세부 분석")
traits = st.multiselect("아이의 학습 특성 (복수 선택)", ["이론과 개념은 잘 이해하나, 실전 시험에서 실수가 나옴", "스피킹에는 자신감이 넘치나, 쓰기와 스펠링이 다소 약함", "수업 집중도가 높고 질문에 대답을 잘함", "이해력이 빠르고 과제를 성실히 수행함"])
weak_points = st.text_area("틀린 부분 및 취약점", placeholder="예: 과거시제 불규칙 동사 변화를 헷갈려 함")
custom_comment = st.text_area("선생님 추가 코멘트", placeholder="예: 다음 학기에는 영작 연습 비중을 늘리겠습니다.")

if st.button("✨ 전문 피드백 자동 작성하기", type="primary"):
    if not selected_kr_name: st.error("학생을 선택해주세요!")
    else:
        display_name = f"{selected_kr_name}({selected_en_name})" if selected_en_name else selected_kr_name
        display_books = book1 if "Phonics" in selected_level or book2 == "없음" else f"{book1}, {book2}"
        traits_text = "\n[선생님 관찰 코멘트]\n평소 학원에서 지켜본 " + selected_kr_name + " 학생은 다음과 같은 특징을 보입니다.\n- " + "\n- ".join(traits) + "\n" if traits else ""
        feedback_text = f"안녕하세요, {display_name} 학부모님...\n 현재 레벨: {selected_level}\n 교재: {display_books}\n 단원: {units}\n 점수: {score} / 평균: {avg_score}\n{traits_text}\n{weak_points}\n{custom_comment}"
        st.text_area("완성된 피드백", value=feedback_text.strip(), height=300)
