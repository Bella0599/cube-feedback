import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="월말평가 피드백 시스템", page_icon="🏫", layout="centered")
st.title("🏫 학원 월말평가 피드백 자동화 (에러 추적 모드)")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 (에러 추적 버전) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="학생명단", ttl="0m") # 테스트를 위해 캐시를 0분으로 설정
    
    # 시트가 잘 연결되었는지 화면에 임시로 띄워봅니다.
    st.success("데이터베이스 연결 자체는 성공했습니다! 🎉")
    st.write("구글 시트에서 읽어온 첫 줄 이름들:", df.columns.tolist())
    
    # 여기서 에러가 날 확률이 높습니다 (글자 오타 등)
    df = df.dropna(subset=['레벨', '한국어이름']) 

except Exception as e:
    st.error("🚨 진짜 에러 원인을 찾았습니다! 아래 문구를 원장님께 보여주세요:")
    st.code(str(e)) # 진짜 에러 메시지를 화면에 검은 박스로 출력합니다.
    st.stop()

# --- 이하 코드 동일 ---
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
    if len(en_name_row) > 0:
        selected_en_name = en_name_row[0]

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
