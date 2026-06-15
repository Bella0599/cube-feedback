import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v21.0")
st.markdown("구글 시트 연동 교재 DB & 주/부교재 점수대별 독립 내러티브 엔진")
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
        
    @st.cache_data(show_spinner="구글 시트에서 교재 학습목표 DB를 동기화 중입니다...")
    def load_book_data(url):
        try:
            csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=books"
            book_df = pd.read_csv(csv_url)
            book_df['교재'] = book_df['교재'].astype(str).str.strip()
            book_df['유닛'] = book_df['유닛'].astype(str).str.strip()
            book_df['학습목표'] = book_df['학습목표'].astype(str).str.strip()
            return book_df
        except:
            return pd.DataFrame(columns=['교재', '유닛', '학습목표'])

    df = load_student_data(sheet_url)
    df_books = load_book_data(sheet_url)
except:
    st.error("구글 시트 연결을 기다리고 있습니다. 시트 주소 및 탭 이름(students, books)을 확인해 주세요.")
    st.stop()

if "generated_feedback" not in st.session_state:
    st.session_state.generated_feedback = ""

# --- 💡 2. 데이터 및 템플릿 정의 ---
PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = ["Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4", "English Trophy 3", "English Trophy 4", "English Trophy 5", "English Trophy 6", "Reading Trophy 1", "Reading Trophy 2", "Reading Trophy 3"]
BOOK2_LIST = ["Writing Monster 1", "Bricks Grammar B1", "Bricks Grammar 1"]
UNITS = [f"Unit {i}" for i in range(1, 13)]
MONTHS = [f"{i}월" for i in range(1, 13)]

# [💡 자동화 함수] 구글 시트 기반 교재 목표 동적 매칭
def get_auto_objective(book, unit, book_dataframe):
    if book_dataframe is not None and not book_dataframe.empty:
        filtered = book_dataframe[(book_dataframe['교재'] == str(book).strip()) & (book_dataframe['유닛'] == str(unit).strip())]
        if not filtered.empty:
            return filtered.iloc[0]['학습목표']
    return f"{book} {unit}의 핵심 Target 어휘 마스터 및 필수 규칙 문장 확장"

# [💡 신규 업그레이드] 점수대별 주교재 vs 부교재 분리형 안내문 생성기 (중복 원천 차단)
def get_dynamic_score_comment(book_type, score_str, name):
    try:
        score = int(score_str)
    except:
        return ""
        
    # 주교재 전용 코멘트 뱅크 (상/중/하 각각 3개씩 분리)
    primary_bank = {
        "high": [
            f"이번 달 다룬 주교재의 핵심 개념을 완벽하게 파악하고 있으며, 높은 오답 방어율로 성실하고 탄탄한 학습 성과를 증명해 주었습니다.",
            f"출제된 주교재의 다소 까다로운 문항까지 거침없이 해결해 내는 깊이 있는 이해도와 흔들림 없는 실력이 무척 돋보입니다.",
            f"주교재 단원별 핵심 포인트를 아주 정교하게 인지하고 있으며, 실전 문제 풀이에서도 훌륭한 응용력을 보여주었습니다."
        ],
        "mid": [
            f"주교재의 전반적인 진도 이해도는 안정적이나, 일부 문항에서 사소한 실수가 발견되어 개념을 완벽하게 다듬는 과정에 있습니다.",
            f"대부분의 주교재 핵심 문제를 잘 해결해 내고 있으며, 오답 피드백을 통해 2%의 아쉬운 빈틈을 차근차근 메워가는 중입니다.",
            f"주교재 학습에 진지하게 임하며 기본기를 충실히 소화했습니다. 문제를 더 꼼꼼히 정독하는 습관만 더하면 큰 도약이 기대됩니다."
        ],
        "low": [
            f"아직 주교재 단원의 핵심 규칙이나 기본 패턴을 응용하는 데 서툴러, 1:1 밀착 복습을 통해 주요 어휘와 개념의 뼈대를 다지고 있습니다.",
            f"주교재 개념을 완전히 자기 것으로 소화하기까지 약간의 학습 정체기를 겪고 있어, 밀착 지도와 반복 드릴 학습을 집중 지원하고 있습니다.",
            f"주교재 풀이 시 오답이 다소 다량 발생하여 기본기를 다시 점검 중이며, 아이가 주눅 들지 않도록 세심하게 응원하며 이끌겠습니다."
        ]
    }
    
    # 부교재 전용 코멘트 뱅크 (주교재와 문장 구조 및 단어 선택을 완전히 다르게 설계)
    sub_bank = {
        "high": [
            f"주교재와 연계된 부교재의 확장 문항들을 막힘없이 소화해 내며, 응용 표현력과 과제 수행 능력이 매우 우수합니다.",
            f"부교재에 수록된 다채로운 연습 문제들을 뛰어난 몰입도로 훌륭히 풀어내어 복습 성취도 역시 최상위권을 유지하고 있습니다.",
            f"부교재를 활용한 자기주도적 문제 해결력이 무척 기특하며, 배운 문법과 작법 이론을 입체적으로 확장해 나가는 능력이 탁월합니다."
        ],
        "mid": [
            f"부교재 문항들을 차분하게 잘 따라오고 있으나, 유형이 조금만 바뀌어도 오답이 생기는 경향이 있어 워크북 피드백을 강화하고 있습니다.",
            f"부교재를 통한 개념 적용 연습을 성실히 수행 중이며, 문장 규칙 매칭 능력을 1:1 클리닉으로 조금 더 다듬어 완성도를 높이겠습니다.",
            f"부교재 기본 문항은 무난히 소화하지만 심화 응용 단계에서 다소 주저함이 보입니다. 반복 훈련을 통해 문제 적응력을 키우겠습니다."
        ],
        "low": [
            f"주교재 이론의 변형 적용이 수록된 부교재 풀이를 다소 어려워하여, 단계별 힌트 제공과 개인별 클리닉으로 솔루션을 제공하고 있습니다.",
            f"부교재 문장 쓰기나 규칙 훈련 등 절대적인 연습량 확보가 조금 더 필요해 보이며, 원내 과제 점검 시간을 늘려 꼼꼼히 케어하겠습니다.",
            f"부교재 문제에 스스로 접근하는 힘이 다소 부족한 상태입니다. 기초 유형 위주의 반복 성공 경험을 통해 자신감을 심어주겠습니다."
        ]
    }
    
    tier = "high" if score >= 90 else ("mid" if score >= 70 else "low")
    # 이름 길이와 점수를 조합한 고유 인덱스 선택 알고리즘 (매번 동일 학생에게는 고유하되, 주/부교재 문장은 절대 안 겹치게 설계)
    idx_p = (len(name) + score) % 3
    idx_s = (len(name) * score + 2) % 3
    
    return primary_bank[tier][idx_p] if book_type == "primary" else sub_bank[tier][idx_s]

UNDERSTAND_TEXTS = {"상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.", "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.", "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간과 복습 훈련이 조금 더 필요한 상태입니다."}
PRESENT_TEXTS = {"상 (Excellent)": "질문에 대한 발표와 참여도가 적극적이며, 자신감 넘치는 목소리로 반 전체 수업 분위기를 주도합니다.", "중 (Good)": "선생님의 질문에 성실하게 답변하며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다.", "하 (Needs Effort)": "내용을 알고 있더라도 발표 시 다소 수줍어하는 경향이 있어, 적극성을 끌어올리도록 격려 중입니다."}
FOCUS_TEXTS = {"상 (Excellent)": "수업 시간 내내 흔들림 없는 높은 몰입도를 보여주며, 지시 사항을 정확하게 이행하는 집중력이 돋보입니다.", "중 (Good)": "기본적인 수업 집중력을 잘 유지하고 있으며, 흐트러짐 없이 강사의 설명에 귀를 기울입니다.", "하 (Needs Effort)": "간혹 집중력이 흐려지는 순간이 관찰되어, 1:1 대면 질문과 밀착 케어를 통해 주의를 환기시키고 있습니다."}

DIAGNOSIS_DB = {
    "Phonics (파닉스)": {
        "유사 알파벳 형태 혼동": "대부분의 알파벳은 잘 인지하고 있으나, 간혹 모양이 비슷한 'b'와 'd', 'p'와 'q'를 헷탈리는 모습이 보입니다. 시각적인 단서나 쓰기 연습을 통해 헷갈리는 알파벳을 정확히 구별하고 내면화할 수 있도록 지도하겠습니다.",
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
st.subheader("📚 2. 교재별 성적표 및 학습 유닛 선택")
if "Phonics" in selected_level:
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("학습 교재", PHONICS_BOOKS)
    with col_m2: main_units = st.multiselect("평가 단원 (보통 3개 선택)", UNITS, default=["Unit 1", "Unit 2", "Unit 3"] if len(UNITS)>=3 else [], key="main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 90", key="main_score")
    sub_book, sub_units, sub_score = None, [], ""
else:
    st.markdown("**[주교재 성적]**")  # UI에서 Main 한글로 교정
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    with col_m1: main_book = st.selectbox("교재 선택", BOOK1_LIST, key="reg_main")
    with col_m2: main_units = st.multiselect("평가 단원 (보통 3개 선택)", UNITS, default=["Unit 1", "Unit 2", "Unit 3"] if len(UNITS)>=3 else [], key="reg_main_unit")
    with col_m3: main_score = st.text_input("점수", placeholder="예: 85", key="reg_main_score")
        
    st.markdown("**[부교재 성적]**")  # UI에서 Sub 한글로 교정
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1: sub_book = st.selectbox("교재 선택", ["선택안함"] + BOOK2_LIST, key="reg_sub")
    with col_s2:
        if sub_book != "선택안함": sub_units = st.multiselect("평가 단원", UNITS, key="reg_sub_unit")
        else: sub_units = []; st.write("부교재 없음")
    with col_s3:
        if sub_book != "선택안함": sub_score = st.text_input("점수", placeholder="예: 80", key="reg_sub_score")
        else: sub_score = ""

# --- 5. 이번 달 유닛별 성취 유형 및 상세 분석 ---
st.markdown("---")
st.subheader("🎯 3. 이번 달 유닛별 성취 유형 및 상세 분석")
st.caption("선택하신 유닛들을 기준으로 아이의 세부 이해도를 분류해 주는 마법의 내러티브 빌더입니다.")

achievement_type = st.radio(
    "💡 우리 아이는 이번 달 어떤 유형에 가깝나요?",
    [
        "🏆 1형: 모든 과제를 완벽하게 마스터하고 이해한 우수 학생",
        "🌿 2형: 대부분 잘 소화했으나 일부 단원에 미세 보완이 필요한 학생",
        "🌱 3형: 학습 정체기나 기초 부족으로 많은 단원에 세심한 밀착 케어가 필요한 학생"
    ]
)

type1_well = []
type2_well, type2_bad = [], []
type3_well, type3_bad = [], []

if not main_units:
    st.warning("⚠️ 위 2번 항목에서 '평가 단원'을 먼저 선택해 주셔야 세부 분석이 가능합니다.")
else:
    if "1형" in achievement_type:
        type1_well = st.multiselect("🥇 완벽하게 마스터하고 깊이 이해한 단원을 선택하세요 (복수 선택)", main_units, default=main_units)
    elif "2형" in achievement_type:
        col_t2_1, col_t2_2 = st.columns(2)
        with col_t2_1: type2_well = st.multiselect("🟩 높은 이해도를 보이며 잘한 단원 (복수 선택)", main_units)
        with col_t2_2: type2_bad = st.multiselect("🟥 미세하게 오답이 있거나 개념 보완이 필요한 단원 (복수 선택)", [u for u in main_units if u not in type2_well])
    elif "3형" in achievement_type:
        col_t3_1, col_t3_2 = st.columns(2)
        with col_t3_1: type3_well = st.multiselect("🟦 어려운 와중에도 기특하게 잘 따라와 준 단원 (복수 선택)", main_units)
        with col_t3_2: type3_bad = st.multiselect("🟧 아직 개념을 다루기 어려워하고 꼼꼼한 복습이 필요한 단원 (복수 선택)", [u for u in main_units if u not in type3_well])

# --- 6. 학생 성향 및 긍정 피드백 ---
st.subheader("📊 4. 수업 태도 및 성향 피드백")
col5, col6, col7 = st.columns(3)
with col5: rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6: rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7: rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

st.markdown("**[수업 시간 아이를 빛내주는 칭찬 성향 선택]**")
selected_traits = []
for category_name, traits in TRAITS_CATEGORIES.items():
    selected = st.multiselect(category_name, traits)
    selected_traits.extend(selected)

st.subheader("🔍 5. 영역별 보완점 및 성장 플랜")
analysis_areas = ["Phonics (파닉스)"] if "Phonics" in selected_level else ["Reading (독해/리딩)"]
if sub_book and sub_book != "선택안함":
    if "Grammar" in sub_book: analysis_areas.append("Grammar (문법)")
    elif "Writing" in sub_book: analysis_areas.append("Writing (영작)")

selected_weaknesses = {}
for area in analysis_areas:
    selected = st.multiselect(f"[{area}] 이번 달 미세 보완이 필요한 디테일", list(DIAGNOSIS_DB[area].keys()))
    if selected: selected_weaknesses[area] = selected

st.subheader("✍️ 6. 담당 강사 개별 피드백 및 클로징")
selected_template = st.selectbox("📌 마법의 코멘트 템플릿 선택 (수준별 격려)", list(TEACHER_TEMPLATES.keys()))
teacher_custom_feedback = st.text_area("✍️ 추가 개별 코멘트 (선택 사항)", placeholder="템플릿 내용 외에 덧붙이고 싶은 말씀이 있다면 자유롭게 입력해 주세요.")
st.markdown("---")
selected_closing = st.selectbox("💌 안내문 클로징 멘트 선택", list(CLOSING_MENT_DB.keys()))

# --- 7. 피드백 메세지 생성 로직 ---
if st.button("✨ 큐브어학원 프리미엄 피드백 생성"):
    if not selected_student:
        st.error("학생을 선택해 주세요.")
    elif not main_units:
        st.error("평가 단원을 최소 하나 이상 선택해 주세요.")
    else:
        # [💡 구글 시트 연동 자동화] 선택된 유닛별 목표 리스트 자동 동적 생성
        objective_list_text = ""
        for unit in main_units:
            obj = get_auto_objective(main_book, unit, df_books)
            objective_list_text += f" - {unit}: {obj}\n"
            
        main_units_str = ", ".join(main_units) if main_units else "단원 미지정"
        
        # [💡 엔진 업그레이드] 점수별 독립 문항 매칭 기반의 스코어 보드 작성
        main_comment = get_dynamic_score_comment("primary", main_score, selected_en_name)
        score_report = f"· 주교재: {main_book} ({main_units_str}) : {main_score}점 / 100점\n  → {main_comment}"
        
        if sub_book and sub_book != "선택안함": 
            sub_units_str = ", ".join(sub_units) if sub_units else "단원 미지정"
            sub_comment = get_dynamic_score_comment("sub", sub_score, selected_en_name)
            score_report += f"\n· 부교재: {sub_book} ({sub_units_str}) : {sub_score}점 / 100점\n  → {sub_comment}"

        # 성취 유형별 맞춤형 내러티브 생성
        objective_narrative = ""
        if "1형" in achievement_type:
            well_str = ", ".join(type1_well) if type1_well else "이번 달 전 단원"
            objective_narrative = f"이번 달 주요 핵심 과정인 **[{well_str}]** 영역의 개념과 규칙을 깊이 있게 완벽하게 이해하고 소화해 냈습니다. 오답에 대한 피드백도 스펀지처럼 빠르게 흡수하여 탁월한 성취를 보여주었습니다. 우리 {selected_en_name}(이)에게 앞으로도 영어 공부가 더욱 즐겁고 깊이 있는 유익한 수업이 될 수 있도록 늘 칭찬하며 최선으로 노력하겠습니다."
        
        elif "2형" in achievement_type:
            well_str = ", ".join(type2_well) if type2_well else "주요 학습"
            bad_str = ", ".join(type2_bad) if type2_bad else "일부 심화"
            objective_narrative = f"이번 달 과정 중 **[{well_str}]** 영역에서는 매우 높은 이해도를 보이며 안정적으로 과제를 수행해 냈습니다. 다만, 복습 과정 중 **[{bad_str}]** 부분에서는 개념적 규칙을 완벽히 정교하게 체화하는 데 있어 아주 미세하게 아쉬운 부분이 관찰되었습니다. 해당 단원은 다음 달에도 유기적인 연계 학습 및 꼼꼼한 반복 학습을 병행하여 부족한 틈새를 단단하게 다지고 완벽하게 채워가겠습니다."
        
        elif "3형" in achievement_type:
            well_str = ", ".join(type3_well) if type3_well else "기본 진도"
            bad_str = ", ".join(type3_bad) if type3_bad else "일부 영역"
            objective_narrative = f"이번 한 달 동안 다소 생소하고 어려울 수 있는 내용이었음에도 불구하고, **[{well_str}]** 부분은 지치지 않고 끝까지 기특하게 잘 따라와 주었습니다. 다만 학습 확장 단계인 **[{bad_str}]** 영역에서는 아직 규칙을 유연하게 적용하거나 소리를 정확하게 구별해 내는 데 다소 어려움을 보이고 있습니다. 수업 시간에 스스로 조금 힘들어하더라도 끝까지 강사의 설명에 집중하며 잘 따라오려는 예쁜 모습이 돋보이는 만큼, 밀착 클리닉을 통해 학습 자신감을 단단하게 회복하도록 돕겠습니다."

        # 태도 코멘트 생성
        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        traits_text = f"\n특히 {selected_en_name}(이)는 평소 학원에서 " + " ".join(selected_traits) if selected_traits else ""
        positive_section = f"- {u_sentence}\n- {p_sentence}\n- {f_sentence}{traits_text}"

        # 케어 플랜 생성
        care_plan_text = ""
        if selected_weaknesses:
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    care_plan_text += f"· 완벽한 도약을 위해 {area}의 [{w}] 부분을 미세하게 터치해 주는 단계가 필요합니다. 학원에서는 이를 위해 {plan}\n"
        if not care_plan_text: care_plan_text = f"· 현재 {selected_en_name}(이)는 모든 영역의 밸런스를 예쁘게 유지하고 있습니다.\n"

        # 마법의 코멘트 및 강사 피드백 결합
        custom_processed_text = ""
        if selected_template != "선택 안 함 (아래 직접 입력)":
            custom_processed_text += TEACHER_TEMPLATES[selected_template].format(name=selected_en_name) + " "
        if teacher_custom_feedback:
            custom_processed_text += refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 한 달간 {selected_en_name}(이)를 지도하며 선생님이 느낀 점은, 아이가 지닌 가능성과 성실함이 매우 기특하다는 것입니다. 앞으로도 든든한 페이스메이커가 되겠습니다."
        
        final_closing_ment = CLOSING_MENT_DB[selected_closing]

        # 최종 피드백 템플릿 출력
        st.session_state.generated_feedback = f"""
안녕하세요, 큐브어학원입니다. 
{selected_month} 한 달간 {selected_en_name}가 열심히 공부한 내용을 확인하는 월말평가가 있었습니다.  
{selected_en_name} 얼마나 성장했는지, 또 어떤 부분을 조금 더 챙겨주면 좋을지 꼼꼼히 살펴보았습니다. 
이번 평가를 통해 발견된 모습들과 앞으로의 지도 방향을 공유해 드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 영역별 평가 결과 (100점 만점 기준):
{score_report}


[1. 핵심 단원별 목표 성취 리포트]
이번 달 교재 학습을 통해 아이가 학습 했던 핵심 유닛별 목표와 달성도 분석입니다.

💡 [이번 달 유닛별 상세 학습 목표]
{objective_list_text.strip()}

💡 [단원별 실제 성취도 다이어리]
✔ {objective_narrative}


[2. 학생 성향 및 태도 리포트]
{positive_section}


[3. 큐브 케어 플랜]
다음 레벨을 위한 큐브만의 촘촘한 개별 솔루션입니다.
{care_plan_text}


[4. 담당 강사 개별 밀착 소견]
우리 {selected_en_name}는 {custom_processed_text.strip()}


{final_closing_ment}

- 큐브어학원 드림 -
        """.strip()
        st.success(f"{selected_month} 큐브어학원 명품 피드백 메세지가 성공적으로 빌드되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=800)
