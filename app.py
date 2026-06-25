import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v21.0")
st.markdown("구글 시트 연동형 교재 DB 및 프리미엄 밀착 피드백 엔진")
st.divider()

# --- 1. 구글 시트 데이터 불러오기 ---
sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing" 

@st.cache_data(show_spinner="구글 시트에서 학생 명단을 연결 중입니다...")
def load_student_data(url):
    # 💡 팁 반영: &headers=1 파라미터 추가
    csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&headers=1&sheet=students"
    data = pd.read_csv(csv_url)
    
    # 띄어쓰기 문제 방지를 위해 컬럼명 앞뒤 공백 제거
    data.columns = data.columns.str.strip()
    
    # 디버깅: '레벨'과 '한국어이름' 열이 잘 들어왔는지 확인
    if '레벨' not in data.columns or '한국어이름' not in data.columns:
        raise ValueError(f"시트에서 '레벨' 또는 '한국어이름' 열을 찾지 못했습니다. 파이썬이 읽은 첫 줄(제목): {list(data.columns)}")
        
    data = data.dropna(subset=['레벨', '한국어이름'])
    return data
        
@st.cache_data(show_spinner="구글 시트에서 교재 학습목표 DB를 동기화 중입니다...")
def load_book_data(url):
    try:
        # 💡 팁 반영: &headers=1 파라미터 추가
        csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&headers=1&sheet=books"
        book_df = pd.read_csv(csv_url)
        
        # 띄어쓰기 문제 방지를 위해 컬럼명 앞뒤 공백 제거
        book_df.columns = book_df.columns.str.strip()
        
        book_df['교재'] = book_df['교재'].astype(str).str.strip()
        book_df['유닛'] = book_df['유닛'].astype(str).str.strip()
        book_df['학습목표'] = book_df['학습목표'].astype(str).str.strip()
        return book_df
    except Exception as e:
        st.warning(f"교재 DB를 불러오는 중 문제가 발생했습니다: {e}")
        return pd.DataFrame(columns=['교재', '유닛', '학습목표'])

try:
    df = load_student_data(sheet_url)
    df_books = load_book_data(sheet_url)
except Exception as e:
    st.error(f"구글 시트 연결 에러가 발생했습니다. 권한 및 탭 이름을 확인하세요. (상세 에러: {e})")
    st.stop()

if "generated_feedback" not in st.session_state:
    st.session_state.generated_feedback = ""

# --- 2. 데이터 및 템플릿 정의 ---
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

def get_auto_objective(book, unit, book_dataframe):
    if book_dataframe is not None and not book_dataframe.empty:
        filtered = book_dataframe[(book_dataframe['교재'] == str(book).strip()) & (book_dataframe['유닛'] == str(unit).strip())]
        if not filtered.empty:
            return filtered.iloc[0]['학습목표']
    return f"{book} {unit}의 핵심 Target 어휘 마스터 및 필수 규칙 문장 확장"

UNDERSTAND_TEXTS = {"상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.", "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.", "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간과 복습 훈련이 조금 더 필요한 상태입니다."}
PRESENT_TEXTS = {"상 (Excellent)": "질문에 대한 발표와 참여도가 적극적이며, 자신감 넘치는 목소리로 반 전체 수업 분위기를 주도합니다.", "중 (Good)": "선생님의 질문에 성실하게 답변하며, 자신에게 주어진 학습 역할을 무리 없이 잘 수행해냅니다.", "하 (Needs Effort)": "내용을 알고 있더라도 발표 시 다소 수줍어하는 경향이 있어, 적극성을 끌어올리도록 격려 중입니다."}
FOCUS_TEXTS = {"상 (Excellent)": "수업 시간 내내 흔들림 없는 높은 몰입도를 보여주며, 지시 사항을 정확하게 이행하는 집중력이 돋보입니다.", "중 (Good)": "기본적인 수업 집중력을 잘 유지하고 있으며, 흐트러짐 없이 강사의 설명에 귀를 기울입니다.", "하 (Needs Effort)": "간혹 집중력이 흐려지는 순간이 관찰되어, 1:1 대면 질문과 밀착 케어를 통해 주의를 환기시키고 있습니다."}

DIAGNOSIS_DB = {
    "Phonics (파닉스)": {
        "유사 알파벳 형태 혼동": "대부분의 알파벳은 잘 인지하고 있으나, 간혹 모양이 비슷한 'b'와 'd', 'p'와 'q'를 헷갈리는 모습이 보입니다. 시각적인 단서나 쓰기 연습을 통해 헷갈리는 알파벳을 정확히 구별하고 내면화할 수 있도록 지도하겠습니다.",
        "단모음 소리 구별 (a/e/i)": "자음의 소리는 잘 인지하나, 단모음(특히 'a'와 'e', 'e'와 'i')의 미세한 소리 차이를 구별하는 데 어려움을 느낄 때가 있습니다. 입 모양을 비교하며 정확한 모음 소리를 내고 듣는 연습을 강화하겠습니다.",
        "블렌딩(음가 조합) 속도 저하": "개별 알파벳의 소리는 정확히 알고 있지만, 이를 자연스럽게 연결하여 하나의 단어로 읽어내는 '블렌딩' 과정에서 시간이 조금 걸립니다. 소리를 끊지 않고 천천히 이어서 발음하는 훈련을 꾸준히 진행하겠습니다.",
        "첫 글자만 보고 유추하는 습관": "단어를 읽을 때 끝까지 조합하지 않고, 첫 글자나 옆의 그림만 보고 짐작해서 읽으려는 경향이 있습니다. 손가락으로 글자를 하나씩 짚어가며 끝까지 정확하게 읽는 습관을 들이도록 돕겠습니다.",
        "불규칙 사이트 워드 인지 부족": "파닉스 규칙이 적용되지 않는 자주 쓰이는 단어(the, is 등)를 파닉스 규칙대로 읽으려다 문장 읽기에서 막히는 경우가 있습니다. 눈으로 바로 보고 읽어내는 '사이트 워드' 반복 플래시카드 학습을 병행하겠습니다."
    },
    "Course Book (코스북/회화)": {
        "실생활 활용 및 롤플레이": "코스북 수업의 흐름을 아주 훌륭하게 따라오고 있습니다. 학원에서 배운 멋진 표현들을 아이가 입 밖으로 소리 내어 자신 있게 활용할 수 있도록, 롤플레이와 발화 유도를 꼼꼼하게 진행하고 있습니다.",
        "잦은 노출과 자연스러운 흡수": "새로운 표현과 단어를 익히는 중이라 다소 낯설어할 수 있는 시기입니다. 억지로 외우게 하기보다는, 수업 중 잦은 반복 노출과 즐거운 참여를 통해 아이가 스펀지처럼 자연스럽게 영어를 흡수하도록 지도하고 있습니다.",
        "스스로 말해보는 자신감": "배운 내용을 인지하고 이해하는 속도가 아주 빠릅니다! 이제는 알고 있는 것을 주도적으로 뽐내보는 자신감만 한 스푼 더해지면 완벽할 것 같습니다. 칭찬을 듬뿍 주며 스스로 말해보는 기회를 꼼꼼히 챙겨주고 있습니다.",
        "건강한 복습 습관 형성": "수업 시간에 반짝 빛나는 집중력을 집에서도 이어갈 수 있다면 실력이 배가 될 것입니다. 배운 표현을 집에서도 한 번 더 들여다보고 내 것으로 만드는 '건강한 복습 습관'이 예쁘게 자리 잡도록 곁에서 지속적으로 다독이겠습니다.",
        "적극적인 발화 연습": "선생님의 질문과 영어 지시어를 알아듣고 반응하는 속도가 나날이 좋아지고 있습니다. 이 긍정적인 에너지를 이어받아, 머릿속에 있는 영어를 주저 없이 입 밖으로 꺼내는 연습을 1:1로 이끌어내겠습니다."
    },
    "Reading (독해/리딩)": {
        "세부 내용 파악 훈련": "지문의 전체적인 핵심을 짚어내는 감각이 나날이 좋아지고 있습니다. 긴 호흡의 글 속에서 세밀한 정보까지 한 번에 쏙쏙 찾아낼 수 있도록, 문장 구석구석을 함께 살펴보는 밀착 리딩 연습을 더해가겠습니다.",
        "꼼꼼한 정보 탐색": "글을 읽고 정답을 찾아가는 과정이 참 기특합니다. 다만, 단서가 되는 중요한 정보를 가끔 놓칠 때가 있어, 곁에서 지문을 조금 더 꼼꼼하게 단서 위주로 체크하는 스캐닝 훈련을 세심하게 돕고 있습니다.",
        "흐름 이해와 디테일": "이야기의 전체적인 숲을 보는 흐름 이해도가 눈에 띄게 자랐습니다! 이제는 숲 안의 나무들, 즉 디테일한 세부 내용까지 정확하게 짚어내는 힘을 길러주기 위해 1:1 질문을 통해 꼼꼼히 확인하는 과정을 거치고 있습니다.",
        "어휘 추론과 독해력": "문맥 속에서 낯선 어휘를 만났을 때, 당황하지 않고 의미를 유추해보는 연습을 진행하고 있습니다. 아이가 텍스트에 대한 두려움을 없애고 풍부한 어휘력과 독해력을 동시에 가질 수 있도록 다채로운 지문으로 이끌겠습니다.",
        "정확도와 분석 습관": "현재 우리 아이에게는 문제를 빨리 푸는 것보다 문장을 바르게 이해하는 것이 훨씬 중요합니다. 글의 핵심을 차분하고 정확하게 분석해 내는 튼튼한 독해 습관이 온전히 자리 잡을 수 있도록 아이의 속도에 맞추어 세심하게 지도하고 있습니다."
    },
    "Grammar (문법)": {
        "개념 적용 연습": "수업 시간에 배우는 문법 개념을 끄덕이며 잘 이해하는 모습이 예쁩니다. 이제는 머리로 이해한 것을 실제 문제에 자신 있게 적용해 볼 수 있도록, 다양한 응용 문제를 곁에서 함께 풀이하며 활용 감각을 깨워주고 있습니다.",
        "규칙 점검 및 습관화": "문장을 만들 때 아는 문법 규칙을 한 번 더 스스로 점검하는 습관만 더해진다면 실력이 훌쩍 뛸 것입니다. 아이가 실수를 줄이고 스스로 성취감을 느낄 수 있도록, 따뜻한 격려와 함께 꾸준한 문장 드릴 학습을 진행 중입니다.",
        "복합 문장 구조 대비": "기초적인 문법 뼈대는 아주 탄탄하게 잘 잡혀 있습니다. 이를 바탕으로 조금 더 길고 복잡한 문장 구조도 겁내지 않고 유연하게 다뤄볼 수 있도록, 한 단계 수준을 높인 맞춤형 연습을 세심하게 이어가고 있습니다.",
        "잦은 실수 밀착 교정": "문제를 풀 때 간혹 작은 실수가 보이지만, 문법의 뼈대 자체는 아이의 머릿속에 아주 안정적으로 자리 잡아가고 있습니다. 헷갈리는 포인트를 정확히 짚어주어 100% 아이의 지식이 되도록 밀착 교정하고 있습니다.",
        "문장 응용력 키우기": "딱딱한 문법을 공식으로만 외우지 않고, 배운 규칙을 활용해 자신만의 문장으로 만들어보는 활동을 무척 잘해내고 있습니다. 영어가 실생활에서 어떻게 쓰이는지 자연스럽게 깨우치며 응용력을 넓혀가도록 돕겠습니다."
    },
    "Writing (영작)": {
        "생각을 엮어내는 정확성": "자신의 몽글몽글한 생각들을 영어 문장으로 담아내려는 노력이 정말 기특합니다. 이제는 그 생각들을 문법 규칙에 맞게 조금 더 정교하고 정확하게 엮어내는 방법을 곁에서 친절하게 가이드하고 있습니다.",
        "꼼꼼한 마무리와 자기 검수": "문장을 써 내려가는 거침없는 태도가 훌륭합니다. 다 쓴 후에는 대소문자나 마침표, 철자 등을 스스로 한 번 더 점검하는 '꼼꼼한 마무리의 힘'을 기를 수 있도록 밀착 첨삭을 진행하고 있습니다.",
        "문장 구조의 다양화": "글 속에 담긴 아이의 창의적인 아이디어와 발상이 매번 선생님을 미소 짓게 합니다. 이 멋진 생각들을 늘 쓰던 패턴이 아니라, 더 다채롭고 풍성한 문장 구조로 뽐낼 수 있도록 표현력을 확장해 주고 있습니다.",
        "배운 표현의 자연스러운 적용": "오늘 배운 단어와 문법을 어떻게든 자신의 글에 녹여내려는 학구적인 모습이 단연 돋보입니다. 이런 예쁜 시도가 조금 더 자연스럽고 세련된 영어식 표현으로 다듬어지도록 세심하게 첨삭하고 응원하겠습니다.",
        "수식어구 추가를 통한 문장 확장": "기본적인 뼈대를 갖춘 문장은 막힘없이 잘 만들어내고 있습니다. 여기에 '언제, 어디서, 왜'와 같은 수식어구를 살을 붙이듯 더하여, 단문도 풍성하고 디테일하게 늘려가는 심화 영작 훈련을 함께 진행하겠습니다."
    },
    "General (공통/학습태도)": {
        "문제를 비워두거나 건너뛰는 경우 (끈기 · 자신감 케어)": "아이는 문제를 해결하는 과정에서 신중하게 생각하는 장점이 있습니다. 다만 정답에 대한 확신이 부족하거나 어려운 문제를 만났을 때, 자신의 생각을 끝까지 표현하기보다 잠시 멈추거나 건너뛰는 모습이 보이기도 합니다. 앞으로는 틀리는 것을 두려워하기보다 스스로 아는 내용을 바탕으로 끝까지 도전해 보는 경험을 많이 쌓을 수 있도록 지도하겠습니다. 작은 성공 경험을 꾸준히 만들어 주어 자신감과 문제 해결력을 함께 키워나가겠습니다.",
        "보기 활용 및 옮겨 적기 실수 (관찰력 · 꼼꼼함 케어)": "아이는 문제의 내용을 이해하는 힘은 충분히 갖추고 있으나, 답을 작성하는 과정에서 서두르거나 꼼꼼하게 확인하지 못해 아쉬운 실수가 나타나는 경우가 있습니다. 특히 보기 속 단어를 활용하는 문제에서 알고 있는 내용임에도 작은 실수로 점수를 놓치는 경우가 있어, 문제를 푼 후 한 번 더 확인하는 습관을 기를 수 있도록 지도하고 있습니다. 앞으로도 정확성과 꼼꼼함을 함께 키워 아이의 실력이 결과로 자연스럽게 이어질 수 있도록 돕겠습니다.",
        "어휘량이 부족한 경우 (어휘 기초 체력 케어)": "아이는 새로운 내용을 이해하고 받아들이는 태도가 매우 좋으며 수업에도 꾸준히 참여하고 있습니다. 다만 영어 학습의 기초가 되는 어휘량이 조금 더 쌓인다면 독해와 문장 이해에서 한층 더 편안하게 학습할 수 있을 것으로 보입니다. 단어를 단순히 외우는 데 그치지 않고 다양한 문장과 활동 속에서 자연스럽게 익힐 수 있도록 반복 노출과 복습을 꾸준히 진행하며, 아이만의 탄탄한 어휘 기반을 만들어 가겠습니다."
    }
}

TRAITS_CATEGORIES = {
    "🥇 우수 학생 추천 (도약과 주도성 칭찬)": ["스피킹과 리스닝에서 탁월한 감각을 보이며 능동적으로 수업에 참여하고, 배운 내용을 완전히 자기 것으로 만드는 흡수력이 뛰어납니다.", "자기주도적 학습 능력이 탁월하여 과제 완성도가 매우 높고, 반 전체의 학업 분위기를 긍정적으로 주도합니다."],
    "🥈 보통 학생 추천 (성실함과 안정적 성장 칭찬)": ["수업 내용을 차분하고 성실하게 따라오며, 지도를 통해 기본적인 개념을 안정적으로 소화해 내는 뚝심이 있습니다.", "학습 태도가 매우 올바르며 피드백을 주면 스펀지처럼 흡수하여, 틀린 문제를 끝까지 해결하려는 끈기가 돋보입니다."],
    "🥉 격려가 필요한 학생 추천 (기특한 노력과 잠재력 칭찬)": ["어려운 과제나 생소한 개념이 주어지더라도 포기하지 않고 끝까지 성실하게 완료하려는 예쁜 태도와 기특한 도전 정신을 가지고 있습니다.", "수업 시간 동안 차분하고 정돈된 태도로 강사의 설명에 성실히 귀를 기울이며, 조금씩 자신만의 학습 페이스를 단단하게 빌드업해 가고 있습니다."]
}

TEACHER_TEMPLATES = {
    "선택 안 함 (아래 직접 입력)": "",
    "🌱 [기초/격려] 과정 중심의 응원 (태도 칭찬)": "지금 당장 눈에 보이는 큰 점수보다 중요한 건 {name}(이)가 포기하지 않고 영어를 대하는 태도입니다. 기초를 다지는 지금의 시간이 훗날 {name}(이)가 영어를 즐길 수 있는 가장 든든한 밑거름이 될 거예요. {name}(이)의 속도에 맞춰, 저도 포기하지 않고 끝까지 함께 걷겠습니다.",
    "🌿 [중간/도약] 성실함 인정과 확신": "수업에 임하는 {name}(이)의 모습에서 매달 깊은 신뢰를 느낍니다. 성실함은 그 무엇보다 강력한 실력입니다. 지금처럼 기본기를 착실히 다져간다면, 머지않아 더 높은 도약의 순간을 맞이하게 될 것이라 확신합니다.",
    "🌳 [우수/심화] 더 높은 곳을 향한 심화 도전": "현재 실력에 안주하지 않고 더 깊이 있는 내용을 이해하려는 {name}(이)의 열정이 참 멋집니다. 이제는 조금 더 난도가 높은 심화 과정으로 아이의 가능성을 넓혀보려 합니다. 아이의 잠재력이 더 넓은 세상에서 활짝 피어날 수 있도록 이끌겠습니다."
}

CLOSING_MENT_DB = {
    "🤝 [협력 강조형] 신뢰와 파트너십을 강조할 때": "아이의 성장은 강사인 저와 학부모님의 따뜻한 관심이 함께 모일 때 더욱 빛이 난다고 믿습니다. 우리 아이가 영어를 통해 더 넓은 세상을 꿈꿀 수 있도록, 저 또한 최선을 다해 지도하겠습니다. 늘 믿고 맡겨주셔서 진심으로 감사합니다.",
    "🌱 [성장 중시형] 과정의 소중함을 강조할 때": "시험 점수라는 결과보다, 아이가 영어를 대하는 태도가 얼마나 긍정적으로 변화하고 있는지에 더 주목해 주시면 좋겠습니다. 그 성장의 과정을 곁에서 꼼꼼히 기록하고 이끌겠습니다. 아이가 즐겁게 영어를 즐길 수 있도록 가정에서도 많은 격려 부탁드립니다.",
    "🛡️ [안심 전달형] 정성과 책임을 강조할 때": "매시간 아이들의 눈높이에서 가장 필요한 것이 무엇인지 고민하며 수업하고 있습니다. 아이가 영어 때문에 힘들지 않게, 오히려 영어로 자신감을 얻을 수 있도록 세심하게 지도하겠습니다. 시험 결과에 대해 궁금하신 점은 언제든 편하게 연락해 주세요. 감사합니다."
}

def refine_teacher_feedback(raw_text, name):
    if not raw_text: return ""
    return raw_text

def parse_score(score_str):
    try:
        return int(score_str)
    except:
        return 90

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
st.subheader("📚 2. 교재별 성적표 및 범위 설정")

is_phonics = "Phonics" in selected_level
primary_units = []
test_range = ""

if is_phonics:
    st.markdown("**[주교재(파닉스) 성적]**")
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1: primary_book = st.selectbox("학습 교재", PHONICS_BOOKS, key="phonics_book_select")
    with col_p2: test_range = st.selectbox("평가 범위 선택", ["Midterm Test (Unit 1-4)", "Final Test (Unit 1-8)"], key="phonics_test_range")
    with col_p3: primary_score = st.text_input("점수", placeholder="예: 90", key="primary_score_val")
    
    phonics_options = PHONICS_TARGETS_DB.get(primary_book, [])
    if test_range == "Final Test (Unit 1-8)":
        primary_units = st.multiselect("학습 및 점검한 Target 음가/알파벳", phonics_options, default=phonics_options)
    else:
        primary_units = st.multiselect("이번 달 주요 성취 Target 음가", phonics_options, default=phonics_options[:4] if len(phonics_options) >= 4 else phonics_options)
    
    sub_book, sub_units, sub_score = None, [], ""
else:
    st.markdown("**[주교재 성적]**")
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1: primary_book = st.selectbox("교재 선택", BOOK1_LIST, key="reg_primary")
    with col_p2: primary_units = st.multiselect("평가 단원", UNITS, default=["Unit 1", "Unit 2", "Unit 3"] if len(UNITS)>=3 else [], key="reg_primary_unit")
    with col_p3: primary_score = st.text_input("점수", placeholder="예: 85", key="reg_primary_score")
        
    st.markdown("**[부교재 성적]**")
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
st.subheader("🎯 3. 이번 달 상세 성취도 다이어리 빌더")
st.caption("입력하신 교재 및 점수를 기반으로 내러티브 엔진이 성취 대상을 자동 분류합니다.")

type1_well, type2_well, type2_bad, type3_well, type3_bad = [], [], [], [], []

if not primary_units:
    st.warning("⚠️ 위 2번 항목에서 '평가 단원' 또는 'Target 음가'를 먼저 선택해 주셔야 세부 분석이 가능합니다.")
else:
    p_score_num = parse_score(primary_score)
    label_subject = "음가/알파벳" if is_phonics else "단원"
    
    if is_phonics and test_range == "Final Test (Unit 1-8)":
        st.markdown(f"🏆 **주교재 분석 유형 : 🌟 파닉스 Final Test**")
        type2_bad = st.multiselect(f"🟧 개별 맞춤 복습이 조금 더 필요한 {label_subject} (없으면 비워두세요)", primary_units)
    else:
        if p_score_num >= 90:
            st.markdown(f"🏆 **주교재 분석 유형 : 상위권 (90점 이상)**")
            type1_well = st.multiselect(f"🥇 완벽하게 마스터하고 깊이 이해한 {label_subject}", primary_units, default=primary_units)
        elif p_score_num >= 75:
            st.markdown(f"🌿 **주교재 분석 유형 : 중위권 (75점 ~ 89점)**")
            col_t2_1, col_t2_2 = st.columns(2)
            with col_t2_1: type2_well = st.multiselect(f"🟩 높은 이해도를 보이며 잘한 {label_subject}", primary_units)
            with col_t2_2: type2_bad = st.multiselect(f"🟥 미세 보완이 필요한 {label_subject}", [u for u in primary_units if u not in type2_well])
        else:
            st.markdown(f"🌱 **주교재 분석 유형 : 집중 케어권 (74점 이하)**")
            col_t3_1, col_t3_2 = st.columns(2)
            with col_t3_1: type3_well = st.multiselect(f"🟦 어려운 와중에도 기특하게 잘 따라와 준 {label_subject}", primary_units)
            with col_t3_2: type3_bad = st.multiselect(f"🟧 복습과 정교화 케어가 필요한 {label_subject}", [u for u in primary_units if u not in type3_well])

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

st.subheader("🔍 5. 영역별 보완점 및 큐브 케어 플랜")
st.caption("학생에게 필요한 맞춤형 피드백을 영역별로 자유롭게 선택해 주세요. (다중 선택 가능)")

if is_phonics:
    available_areas = ["Phonics (파닉스)", "General (공통/학습태도)"]
else:
    available_areas = ["Course Book (코스북/회화)", "Reading (독해/리딩)", "Grammar (문법)", "Writing (영작)", "General (공통/학습태도)"]

selected_weaknesses = {}
for area in available_areas:
    selected = st.multiselect(f"📌 [{area}] 밀착 케어 항목 선택", list(DIAGNOSIS_DB[area].keys()))
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
    elif not primary_units:
        st.error("평가 단원 및 Target 음가를 최소 하나 이상 선택해 주세요.")
    else:
        objective_list_text = ""
        if is_phonics:
            objective_list_text += f" - 평가 범위 유형: {test_range}\n"
            if test_range != "Final Test (Unit 1-8)":
                objective_list_text += f" - 중점 점검 음가: {', '.join(primary_units)}\n"
            objective_list_text += f" - 학습 목표: {primary_book} 기반의 핵심 타겟 발화 메커니즘 훈련 및 음가 직관력 인지"
            score_report = f"· {primary_book} ({test_range}) : {primary_score}점 / 100점"
        else:
            if "Wonderful World" in primary_book:
                clusters = [
                    {"name": "Unit 1-3", "units": ["Unit 1", "Unit 2", "Unit 3"]},
                    {"name": "Unit 4-6", "units": ["Unit 4", "Unit 5", "Unit 6"]},
                    {"name": "Unit 7-9", "units": ["Unit 7", "Unit 8", "Unit 9"]},
                    {"name": "Unit 10-12", "units": ["Unit 10", "Unit 11", "Unit 12"]}
                ]
                for cluster in clusters:
                    selected_in_cluster = [u for u in primary_units if u in cluster["units"]]
                    if selected_in_cluster:
                        theme_key = f"{cluster['name']} 대주제"
                        theme_row = df_books[(df_books['교재'] == str(primary_book).strip()) & (df_books['유닛'] == theme_key)]
                        if not theme_row.empty:
                            big_theme = theme_row.iloc[0]['학습목표']
                            objective_list_text += f" ■ 대주제 [{cluster['name']}]: {big_theme}\n"
                        else:
                            objective_list_text += f" ■ 대주제 [{cluster['name']}]: (구글 시트 books 탭에 '{theme_key}' 항목을 추가해 주세요)\n"
                        for u in selected_in_cluster:
                            obj = get_auto_objective(primary_book, u, df_books)
                            objective_list_text += f"   - {u}: {obj}\n"
            else:
                for unit in primary_units:
                    obj = get_auto_objective(primary_book, unit, df_books)
                    objective_list_text += f" - {unit}: {obj}\n"
            primary_units_str = ", ".join(primary_units) if primary_units else "단원 미지정"
            score_report = f"· {primary_book} ({primary_units_str}) : {primary_score}점 / 100점"
            
        if sub_book and sub_book != "선택안함": 
            sub_units_str = ", ".join(sub_units) if sub_units else "단원 미지정"
            score_report += f"\n· {sub_book} ({sub_units_str}) : {sub_score}점 / 100점"

        p_score_num = parse_score(primary_score)
        primary_narrative = ""
        target_word = "음가" if is_phonics else "단원"
        
        if is_phonics and test_range == "Final Test (Unit 1-8)":
            bad_str = ", ".join(type2_bad) if type2_bad else ""
            primary_narrative = f"이번 파닉스 Final Test(Unit 1-8)를 통해 그동안 배운 긴 호흡의 과정을 종합적으로 점검한 결과, 1단원부터 8단원까지의 전체적인 음가와 규칙을 훌륭하게 마스터하고 뛰어난 언어적 이해도를 보여주었습니다. 포기하지 않고 성실하게 전체 단원을 마무리한 {selected_en_name}(이)를 크게 칭찬해 주고 싶습니다! "
            if bad_str:
                primary_narrative += f"다만, 더 완벽하고 단단한 다음 단계 도약을 위해 복습 시 **[{bad_str}]** 영역의 미세한 발음 및 규칙 적용 부분만 조금 더 신경 써서 1:1로 섬세하게 보완하겠습니다."
            else:
                primary_narrative += "모든 영역에서 빈틈없는 완벽한 성취를 보여주었으며, 이 단단한 기초를 바탕으로 다음 레벨에서도 흔들림 없이 훌륭한 모습을 이어갈 것이라 확신합니다."
        else:
            if p_score_num >= 90:
                well_str = ", ".join(type1_well) if type1_well else f"이번 달 전 {target_word}"
                primary_narrative = f"이번 달 주요 핵심 과정인 **[{well_str}]** 영역의 개념과 규칙을 깊이 있게 완벽하게 이해하고 소화해 냈습니다. 오답에 대한 피드백도 스펀지처럼 빠르게 흡수하여 탁월한 성취를 보여주었습니다. 우리 {selected_en_name}(이)에게 앞으로도 영어 공부가 더욱 즐겁고 깊이 있는 수업이 될 수 있도록 늘 칭찬하며 최선으로 노력하겠습니다."
            elif p_score_num >= 75:
                well_str = ", ".join(type2_well) if type2_well else "주요 학습"
                bad_str = ", ".join(type2_bad) if type2_bad else f"일부 {target_word}"
                primary_narrative = f"이번 달 과정 중 **[{well_str}]** 영역에서는 매우 높은 이해도를 보이며 안정적으로 과제를 수행해 냈습니다. 다만, 복습 과정 중 **[{bad_str}]** 부분에서는 개념적 규칙을 완벽히 정교하게 체화하는 데 있어 아주 미세하게 아쉬운 부분이 관찰되었습니다. 해당 영역은 다음 달에도 유기적인 연계 학습 및 꼼꼼한 반복 학습을 병행하여 부족한 틈새를 단단하게 다지고 완벽하게 채워가겠습니다."
            else:
                well_str = ", ".join(type3_well) if type3_well else "기본 진도"
                bad_str = ", ".join(type3_bad) if type3_bad else f"일부 {target_word}"
                primary_narrative = f"이번 한 달 동안 다소 생소하고 어려울 수 있는 내용이었음에도 불구하고, **[{well_str}]** 부분은 지치지 않고 끝까지 기특하게 잘 따라와 주었습니다. 다만 학습 확장 단계인 **[{bad_str}]** 영역에서는 아직 규칙을 유연하게 적용하거나 소리를 정확하게 구별해 내는 데 다소 어려움을 보이고 있습니다. 수업 시간에 스스로 조금 힘들어하더라도 끝까지 강사의 설명에 집중하며 잘 따라오려는 예쁜 모습이 돋보이는 만큼, 밀착 클리닉을 통해 학습 자신감을 단단하게 회복하도록 돕겠습니다."

        sub_narrative = ""
        if sub_book and sub_book != "선택안함":
            s_score_num = parse_score(sub_score)
            if s_score_num >= 90:
                sub_narrative = f"\n\n또한, 연계 과정인 부교재 **[{sub_book}]** 학습에서도 흔들림 없는 최상위권의 감각을 증명했습니다. 응용 표현 능력이 매우 뛰어나며, 배운 표현 요소를 유연하게 확장하여 주도적으로 활용하는 능력이 단연 돋보입니다."
            elif s_score_num >= 75:
                sub_narrative = f"\n\n또한, 부교재 **[{sub_book}]**를 활용한 심화 및 문장 확장 학습 과정을 성실하게 수행해 나가고 있습니다. 성적 자체는 무난하고 안정적이나, 특정 취약 패턴에서 자잘한 실수가 발생하지 않도록 오답 분석을 통해 단단하게 교정해 가겠습니다."
            else:
                sub_narrative = f"\n\n또한, 부교재 **[{sub_book}]** 학습 과정에서 일부 고난도 문형이나 생소한 문법 규칙을 다루는 데 다소 부담을 느끼는 상태입니다. 개념적 정체기를 잘 극복할 수 있도록 진도를 유연하게 조절하고 밀착 가이드를 제공하여 부담을 덜어주도록 하겠습니다."

        objective_narrative = primary_narrative + sub_narrative

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
                    care_plan_text += f"✔️ [{area} - {w}]\n  {plan}\n\n"
        if not care_plan_text: care_plan_text = f"· 현재 {selected_en_name}(이)는 모든 영역의 밸런스를 예쁘게 유지하고 있습니다.\n"

        custom_processed_text = ""
        if selected_template != "선택 안 함 (아래 직접 입력)":
            custom_processed_text += TEACHER_TEMPLATES[selected_template].format(name=selected_en_name) + " "
        if teacher_custom_feedback:
            custom_processed_text += refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 한 달간 {selected_en_name}(이)를 지도하며 선생님이 느낀 점은, 아이가 지닌 가능성과 성실함이 매우 기특하다는 것입니다. 앞으로도 든든한 페이스메이커가 되겠습니다."
        
        final_closing_ment = CLOSING_MENT_DB[selected_closing]

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

💡 [이번 달 상세 학습 목표 및 범위]
{objective_list_text.strip()}

💡 [단원별 실제 성취도 다이어리]
✔ {objective_narrative}


[2. 학생 성향 및 태도 리포트]
{positive_section}


[3. 큐브 영역별 밀착 케어 플랜]
아이의 더 큰 도약을 위한 큐브어학원만의 세심한 개별 솔루션입니다.

{care_plan_text.strip()}


[4. 담당 강사 개별 밀착 소견]
우리 {selected_en_name}는 {custom_processed_text.strip()}


{final_closing_ment}

- 큐브어학원 드림 -
        """.strip()
        st.success(f"{selected_month} 큐브어학원 명품 피드백 메세지가 성공적으로 빌드되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=800)
