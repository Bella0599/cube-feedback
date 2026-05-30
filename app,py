import streamlit as st

# 1. 앱 기본 디자인 설정
st.set_page_config(page_title="월말평가 시스템", page_icon="🏫", layout="centered")
st.title("🏫 [v2.0] 프리미엄 월말평가 피드백 자동화")
st.markdown("선택만 하세요. **원장님 퀄리티의 전문적인 피드백**은 AI가 완성합니다.")
st.divider()

# 2. 학생 및 레벨 정보
st.subheader("1. 학생 및 레벨 정보")
col1, col2 = st.columns(2)
with col1:
    name_kr = st.text_input("학생 이름 (한글)", placeholder="예: 홍길동")
with col2:
    # 💡 꿀팁: 나중에 구글시트(DB)를 연동하면 한글 이름만 쳐도 영어가 자동으로 뜨게 할 수 있습니다!
    name_en = st.text_input("학생 이름 (영어)", placeholder="예: David")

level = st.selectbox("현재 레벨 선택", ["파닉스반 (Phonics)", "레벨 1 (초급)", "레벨 2 (중급)", "레벨 3 (고급)"])

# 3. 학습 및 평가 결과 (레벨에 따른 교재 수 자동 조절)
st.subheader("2. 진도 및 평가 결과")
col_b1, col_b2 = st.columns(2)
with col_b1:
    book1 = st.text_input("학습 교재 1", placeholder="예: Smart Phonics 1")
with col_b2:
    if level == "파닉스반 (Phonics)":
        book2 = st.text_input("학습 교재 2", value="(파닉스반은 1권만 진행)", disabled=True)
    else:
        book2 = st.text_input("학습 교재 2 (부교재)", placeholder="예: Reading Space 1")

units = st.text_input("평가 단원", placeholder="예: 1~3단원")

col_s1, col_s2 = st.columns(2)
with col_s1:
    score = st.text_input("학생 점수", placeholder="예: 85점")
with col_s2:
    avg_score = st.text_input("반 평균 점수", placeholder="예: 78점")

# 4. 강사 관찰 및 분석 (선택형 코멘트 도입!)
st.subheader("3. 강사 관찰 및 세부 분석")
st.info("💡 학생의 특징을 클릭만으로 선택하세요. (여러 개 선택 가능)")

# 강사들이 가장 많이 쓰는 특징들을 객관식으로 제공
traits = st.multiselect(
    "아이의 학습 특성 (복수 선택)",
    [
        "이론과 개념은 잘 이해하나, 실전 시험(문제풀이)에서 실수가 나옴",
        "스피킹(말하기)에는 자신감이 넘치나, 쓰기(Writing)와 스펠링이 다소 약함",
        "수업 집중도가 높고 묻는 질문에 대답을 아주 잘함",
        "이해력이 빠르고 내준 과제(숙제)를 매우 성실하게 수행함",
        "처음엔 낯을 가렸으나 점차 영어에 자신감이 붙고 참여도가 좋아짐",
        "단어 암기를 다소 어려워하나, 포기하지 않고 꾸준히 노력하는 태도가 훌륭함"
    ]
)

weak_points = st.text_area("틀린 부분 및 취약점 (상세)", placeholder="예: 과거시제 불규칙 동사 변화를 헷갈려 하여 2단원 오답이 집중되었습니다.")
custom_comment = st.text_area("선생님 추가 코멘트 (다음 학기 계획 등)", placeholder="예: 다음 학기에는 영작 연습 비중을 늘려 쓰기 약점을 보완하겠습니다.")

# 5. 피드백 자동 생성 버튼
if st.button("✨ 전문 피드백 자동 작성하기", type="primary"):
    if not name_kr:
        st.warning("학생 이름(한글)을 입력해주세요!")
    else:
        st.success("피드백이 완성되었습니다. 아래 내용을 복사하여 카톡이나 문자로 발송하세요.")
        
        # 이름 조합 (영어가 있으면 병기)
        display_name = f"{name_kr}({name_en})" if name_en else name_kr
        
        # 교재 조합
        display_books = book1 if level == "파닉스반 (Phonics)" or not book2 else f"{book1}, {book2}"
        
        # 학생 특징 문장화 (선택한 것들을 자연스럽게 묶어줌)
        traits_text = ""
        if traits:
            traits_text = "\n[선생님 관찰 코멘트]\n평소 학원에서 지켜본 " + name_kr + " 학생은 다음과 같은 긍정적인 특징을 보이고 있습니다.\n- " + "\n- ".join(traits) + "\n"
        
        # 최종 피드백 문구 조립
        feedback_text = f"""
안녕하세요, {display_name} 학부모님. 담당 강사입니다.
이번 달 {name_kr} 학생의 학습 현황 및 월말평가 결과를 안내해 드립니다.

■ 현재 레벨: {level}
■ 학습 교재: {display_books}
■ 평가 단원: {units}
■ 평가 결과: {score} (반 평균: {avg_score})

[학습 평가 및 취약점 분석]
이번 평가를 통해 {name_kr}의 성취도를 점검한 결과, 전반적인 학습 능력이 우수합니다만 일부 보완이 필요한 부분이 파악되었습니다. 
{weak_points}
{traits_text}
[다음 학기 학습 방향]
{custom_comment if custom_comment else f"다음 진도에서는 이번에 부족했던 부분을 집중적으로 복습하며 탄탄하게 기초를 다질 예정입니다."}

가정에서도 {name_kr} 학생이 자신감을 가질 수 있도록 아낌없는 칭찬과 격려 부탁드립니다.
학습에 관해 궁금하신 점이 있으시면 언제든 편하게 연락 주십시오. 감사합니다.
        """
        
        # 텍스트 박스에 결과 출력
        st.text_area("완성된 피드백 (복사해서 사용하세요)", value=feedback_text.strip(), height=450)
