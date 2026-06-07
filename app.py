import streamlit as st
import pandas as pd

st.set_page_config(page_title="큐브어학원 피드백 시스템", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 큐브어학원 월말평가 시스템 v22.2")
st.markdown("구글 시트 연동형 교재 DB 및 프리미엄 7대 성향 키워드 밀착 피드백 엔진 (부교재 확장판)")
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

# --- 2. 데이터 및 템플릿 정의 ---
PHONICS_BOOKS = ["Jungle Phonics 1", "Jungle Phonics 2", "Jungle Phonics 3", "Jungle Phonics 4"]
BOOK1_LIST = ["Wonderful World B1", "Wonderful World B2", "Wonderful World B3", "Wonderful World B4","English Starship Starter", "English Trophy 3","English Trophy 4","English Trophy 5","English Trophy 6", "Reading Trophy 1", "Reading Trophy 2", "Reading Trophy 3"]
BOOK2_LIST = ["Writing Monster 1","Writing Monster 2","Writing Monster 3", "ELT Grammar Starter 1","ELT Grammar Starter 2","ELT Grammar Starter 3", "Bricks Grammar 1","Bricks Grammar 2","Bricks Grammar 3","Bricks Grammar 4", "Vista 1"]
UNITS = [f"Unit {i}" for i in range(1, 13)]
MONTHS = [f"{i}월" for i in range(1, 13)]

PHONICS_TARGETS_DB = {
    "Jungle Phonics 1": [chr(i) for i in range(65, 91)], 
    "Jungle Phonics 2": ["an", "ap", "at", "ad", "ag", "am", "en", "et", "ed", "eg", "ib", "id", "ig", "in", "ip", "it", "ix", "ot", "op", "og", "ox", "ug", "up", "ud", "um", "ub", "un", "ut"], 
    "Jungle Phonics 3": ["ame", "ake", "ate", "ave", "ane", "ape", "ase", "ine", "ike", "ide", "ite", "ive", "ime", "ipe", "ole", "one", "ose", "ope", "ote", "ome", "une", "ule", "ube", "ute", "use"], 
    "Jungle Phonics 4": ["bl", "cl", "fl", "pl", "br", "cr", "fr", "pr", "sn", "sw", "nk", "ng", "sh", "ch", "wh", "ai", "ay", "ea", "ee", "oa", "ow", "oi", "oy", "oo", "ou", "ar", "or", "er", "ir", "ur"] 
}

# 부교재 전용 코멘트 DB 추가 (v22.2 신규)
SUB_BOOK_NARRATIVE_DB = {
    "high": {
        "문장 패턴 활용 우수": "학습한 문장 패턴과 핵심 어휘를 정확하게 이해하고 있으며, 이를 활용하여 문장을 완성하는 능력이 매우 우수합니다. 배운 내용을 자신의 것으로 자연스럽게 활용하는 모습이 인상적이며, 꾸준한 학습 태도가 좋은 결과로 이어지고 있습니다.",
        "쓰기 완성도 우수": "기본 문장 구조와 주요 표현을 안정적으로 활용하며 완성도 높은 쓰기 실력을 보여주고 있습니다. 철자와 문장 구성 또한 꼼꼼하게 관리하고 있어 앞으로 더욱 풍부한 표현력으로 성장할 모습이 기대됩니다."
    },
    "mid": {
        "기본기 안정화 단계": "학습한 문장 패턴과 주요 어휘를 전반적으로 잘 이해하고 있으며, 배운 내용을 활용하여 문장을 작성하는 능력이 꾸준히 향상되고 있습니다. 앞으로는 철자와 세부 표현까지 꼼꼼히 확인하는 습관을 더한다면 더욱 완성도 높은 결과를 보여줄 수 있을 것으로 기대됩니다.",
        "정확성 향상 단계": "기본 문장 구조와 핵심 단어를 안정적으로 활용하고 있으며, 쓰기에 대한 이해도도 좋은 편입니다. 현재는 정확성과 표현력을 조금씩 다듬어 가는 단계로, 반복 학습을 통해 더욱 자신감 있는 영어 쓰기가 가능할 것으로 보입니다."
    },
    "low": {
        "쓰기 기본기 형성 중": "학습한 단어와 문장 패턴을 익혀가는 과정에 있으며, 수업 시간에도 꾸준히 참여하며 배운 내용을 자신의 것으로 만들기 위해 노력하고 있습니다. 반복적인 쓰기 연습을 통해 핵심 표현을 더욱 자연스럽게 활용할 수 있도록 지도하겠습니다.",
        "자신감 성장 단계": "새로운 단어와 문장 구조를 차근차근 익혀가고 있으며, 영어로 표현하는 힘을 키워가는 중요한 과정에 있습니다. 아이의 학습 속도에 맞춘 반복 학습과 개별 피드백을 통해 자신감을 높이고 기본기를 더욱 탄탄하게 다질 수 있도록 돕겠습니다."
    }
}

def get_auto_objective(book, unit, book_dataframe):
    if book_dataframe is not None and not book_dataframe.empty:
        filtered = book_dataframe[(book_dataframe['교재'] == str(book).strip()) & (book_dataframe['유닛'] == str(unit).strip())]
        if not filtered.empty:
            return filtered.iloc[0]['학습목표']
    return f"{book} {unit}의 핵심 Target 어휘 마스터 및 필수 규칙 문장 확장"

UNDERSTAND_TEXTS = {"상 (Excellent)": "새로운 언어적 개념과 핵심 논리를 받아들이는 이해도가 매우 뛰어나, 진도가 막힘없이 매끄럽게 진행되고 있습니다.", "중 (Good)": "수업 내용을 차분하게 잘 따라오고 있으며, 지도를 통해 기본적인 개념을 안정적으로 소화해 나가고 있습니다.", "하 (Needs Effort)": "개념을 온전히 이해하고 자기 것으로 만드는 데 약간의 시간 및 복습 훈련이 조금 더 필요한 상태입니다."}
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
    "Course Book (코스북)": {
        "실생활 활용 및 롤플레이": "코스북 수업의 흐름을 아주 훌륭하게 따라오고 있습니다. 학원에서 배운 멋진 표현들을 아이가 입 밖으로 소리 내어 자신 있게 활용할 수 있도록, 롤플레이와 발화 유도를 꼼꼼하게 진행하고 있습니다.",
        "잦은 노출과 자연스러운 흡수": "새로운 표현과 단어를 익히는 중이라 다소 낯설어할 수 있는 시기입니다. 억지로 외우게 하기보다는, 수업 중 잦은 반복 노출과 즐거운 참여를 통해 아이가 스펀지처럼 자연스럽게 영어를 흡수하도록 지도하고 있습니다.",
        "스스로 말해보는 자신감": "배운 내용을 인지하고 이해하는 속도가 아주 빠릅니다! 이제는 알고 있는 것을 주도적으로 뽐내보는 자신감만 한 스푼 더해지면 완벽할 것 같습니다. 칭찬을 듬뿍 주며 스스로 말해보는 기회를 꼼꼼히 챙겨주고 있습니다.",
        "건강한 복습 습관 형성": "수업 시간에 반짝 빛나는 집중력을 집에서도 이어갈 수 있다면 실력이 배가 될 것입니다. 배운 표현을 집에서도 한 번 더 들여다보고 내 것으로 만드는 '건강한 복습 습관'이 예쁘게 자리 잡도록 곁에서 지속적으로 다독이겠습니다.",
        "적극적인 발화 연습": "선생님의 질문과 영어 지시어를 알아듣고 반응하는 속도가 나날이 좋아지고 있습니다. 이 긍정적인 에너지를 이어받아, 머릿속에 있는 영어를 주저 없이 입 밖으로 꺼내는 연습을 1:1로 이끌어내겠습니다."
    },
    "Reading (독해)": {
        "단어 빈칸 넣기": "배운 어휘를 활용하는 과정에서 일부 실수가 있었지만, 문맥을 통해 단어의 의미를 파악하려는 노력이 돋보였습니다. 다양한 예문과 독해 지문을 활용하여 단어의 쓰임을 자연스럽게 익힐 수 있도록 지도하겠습니다.",
        "영영풀이": "단어의 의미는 어느 정도 이해하고 있으나, 영어 설명과 연결하는 과정에서 어려움을 보이는 경우가 있었습니다. 단어를 단순 암기하는 것을 넘어 의미와 특징을 함께 이해할 수 있도록 지도하겠습니다.",
        "True / False": "지문의 전체적인 내용은 잘 이해하고 있으나, 세부 정보를 확인하는 과정에서 일부 실수가 있었습니다. 앞으로는 정답의 근거를 직접 찾는 연습을 통해 독해의 정확도를 높여가겠습니다.",
        "세부 내용 파악": "지문의 핵심 내용을 이해하는 힘이 꾸준히 성장하고 있습니다. 앞으로는 핵심 내용뿐만 아니라 세부 정보까지 함께 확인하는 연습을 통해 더욱 탄탄한 독해력을 기를 수 있도록 지도하겠습니다.",
        "어휘 추론과 독해력": "배운 어휘를 문장 속에서 정확하게 활용하는 힘을 기를 수 있도록, 문맥을 통해 단어의 의미를 추론하는 연습을 진행하고 있습니다. 앞으로도 다양한 지문을 접하며 어휘에 대한 이해를 넓히고, 자연스럽게 독해력까지 향상될 수 있도록 지도하겠습니다.",
        "문장 매칭하기" : "글의 흐름을 이해하는 능력은 점차 향상되고 있습니다. 다만 문장 간의 연결 관계를 파악하는 과정에서 아쉬운 부분이 있어, 문맥과 핵심 단서를 찾는 연습을 꾸준히 진행하겠습니다."
    },
    "Grammar (문법)": {
        "개념 적용 연습": "수업 시간에 배우는 문법 개념을 끄덕이며 잘 이해하는 모습이 예쁩니다. 이제는 머리로 이해한 것을 실제 문제에 자신 있게 적용해 볼 수 있도록, 다양한 응용 문제를 곁에서 함께 풀이하며 활용 감각을 깨워주고 있습니다.",
        "규칙 점검 및 습관화": "문장을 만들 때 아는 문법 규칙을 한 번 더 스스로 점검하는 습관만 더해진다면 실력이 훌쩍 뛸 것입니다. 아이가 실수를 줄이고 스스로 성취감을 느낄 수 있도록, 따뜻한 격려와 함께 꾸준한 문장 드릴 학습을 진행 중입니다.",
        "복합 문장 구조 대비": "기초적인 문법 뼈대는 아주 탄탄하게 잘 잡혀 있습니다. 이를 바탕으로 조금 더 길고 복잡한 문장 구조도 겁내지 않고 유연하게 다뤄볼 수 있도록, 한 단계 수준을 높인 맞춤형 연습을 세심하게 이어가고 있습니다.",
        "잦은 실수 밀착 교정": "문제를 풀 때 간혹 작은 실수가 보이지만, 문법의 뼈대 자체는 아이의 머릿속에 아주 안정적으로 자리 잡아가고 있습니다. 헷갈리는 포인트를 정확히 짚어주어 100% 아이의 지식이 되도록 밀착 교정하고 있습니다.",
        "단수 복수 실수 개선": "최근에는 문장의 의미를 이해하고 표현하는 능력이 꾸준히 향상되고 있습니다. 다만 명사의 단수·복수 형태를 적용하는 과정에서 세심한 확인이 필요한 모습이 보여, 문장 속 규칙을 스스로 점검하는 연습을 함께 진행하고 있습니다. 작은 부분까지 정확하게 표현하는 습관이 자리 잡을 수 있도록 지속적으로 지도하겠습니다."
    },
    "Writing (영작)": {
        "생각을 엮어내는 정확성": "자신의 생각들을 영어 문장으로 담아내려는 노력이 정말 기특합니다. 이제는 그 생각들을 문법 규칙에 맞게 조금 더 정교하고 정확하게 엮어내는 방법을 가이드하고 있습니다.",
        "꼼꼼한 마무리와 자기 검수": "문장을 써 내려가는 거침없는 태도가 훌륭합니다. 다 쓴 후에는 대소문자나 마침표, 철자 등을 스스로 한 번 더 점검하는 '꼼꼼한 마무리의 힘'을 기를 수 있도록 밀착 첨삭을 진행하고 있습니다.",
        "문장 구조의 다양화": "글 속에 담긴 아이의 창의적인 아이디어와 발상이 매번 선생님을 미소 짓게 합니다. 이 멋진 생각들을 늘 쓰던 패턴이 아니라, 더 다채롭고 풍성한 문장 구조으로 뽐낼 수 있도록 표현력을 확장해 주고 있습니다.",
        "배운 표현의 자연스러운 적용": "오늘 배운 단어와 문법을 어떻게든 자신의 글에 녹여내려는 학구적인 모습이 단연 돋보입니다. 이런 예쁜 시도가 조금 더 자연스럽고 세련된 영어식 표현으로 다듬어지도록 세심하게 첨삭하고 응원하겠습니다.",
        "수식어구 추가를 통한 문장 확장": "기본적인 뼈대를 갖춘 문장은 막힘없이 잘 만들어내고 있습니다. 여기에 '언제, 어디서, 왜'와 같은 수식어구를 살을 붙이듯 더하여, 단문도 풍성하고 디테일하게 늘려가는 심화 영작 훈련을 함께 진행하겠습니다."
    },
    "General (공통/학습태도)": {
        "문제를 비워두거나 건너뛰는 경우": "문제를 해결하는 과정에서 신중하게 생각하는 장점이 있습니다. 다만 정답에 대한 확신이 부족하거나 어려운 문제를 만났을 때, 자신의 생각을 끝까지 표현하기보다 잠시 멈추거나 건너뛰는 모습이 보이기도 합니다. 앞으로는 틀리는 것을 두려워하기보다 스스로 아는 내용을 바탕으로 끝까지 도전해 보는 경험을 많이 쌓을 수 있도록 지도하겠습니다. 작은 성공 경험을 꾸준히 만들어 주어 자신감과 문제 해결력을 함께 키워나가겠습니다.",
        "보기 활용 및 옮겨 적기 실수": "문제의 내용을 이해하는 힘은 충분히 갖추고 있으나, 답을 작성하는 과정에서 서두르거나 꼼꼼하게 확인하지 못해 아쉬운 실수가 나타나는 경우가 있습니다. 특히 보기 속 단어를 활용하는 문제에서 알고 있는 내용임에도 작은 실수로 점수를 놓치는 경우가 있어, 문제를 푼 후 한 번 더 확인하는 습관을 기를 수 있도록 지도하고 있습니다. 앞으로도 정확성과 꼼꼼함을 함께 키워 아이의 실력이 결과로 자연스럽게 이어질 수 있도록 돕겠습니다.",
        "어휘량이 부족한 경우": "새로운 내용을 이해하고 받아들이는 태도가 매우 좋으며 수업에도 꾸준히 참여하고 있습니다. 다만 영어 학습의 기초가 되는 어휘량이 조금 더 쌓인다면 독해와 문장 이해에서 한층 더 편안하게 학습할 수 있을 것으로 보입니다. 단어를 단순히 외우는 데 그치지 않고 다양한 문장과 활동 속에서 자연스럽게 익힐 수 있도록 반복 노출과 복습을 꾸준히 진행하며, 아이만의 탄탄한 어휘 기반을 만들어 가겠습니다."
    }
}

TRAITS_DB = {
    "📚 수업 집중 및 태도": {
        "수업 몰입도 우수": "수업 중 설명이 시작되면 자연스럽게 시선과 집중이 수업으로 향하는 모습이 인상적이었습니다. 배운 내용을 놓치지 않으려는 태도가 꾸준히 보이며, 학습에 대한 성실함이 큰 강점으로 느껴집니다.",
        "주변에 흔들리지 않는 집중력": "활동이 진행되는 동안 주변 분위기에 쉽게 흔들리지 않고 자신의 학습에 집중하는 모습을 보여주었습니다. 차분하게 내용을 이해하고 정리해 나가는 모습에서 학습에 대한 책임감이 느껴졌습니다.",
        "끝까지 듣는 신중함": "새로운 내용을 배울 때도 교사의 설명을 끝까지 들은 후 문제를 해결하려는 습관이 잘 형성되어 있습니다. 성급하게 답을 찾기보다 이해하려고 노력하는 모습이 인상적입니다.",
        "꼼꼼한 필기 습관": "수업 시간에 배운 내용을 공책이나 교재에 꼼꼼하게 표시하며 따라오는 모습이 자주 보였습니다. 작은 부분도 놓치지 않으려는 태도가 꾸준한 성장으로 이어지고 있습니다.",
        "마무리 점검 습관": "문제를 해결할 때 답을 제출하기 전에 한 번 더 확인하는 습관이 잘 형성되어 있습니다. 꼼꼼한 학습 태도가 돋보입니다."
    },
    "🎤 발표 및 적극성": {
        "망설임 없는 답변": "질문을 받았을 때 망설이기보다 먼저 답해 보려는 적극적인 모습이 인상적이었습니다. 영어로 표현하는 과정 자체를 즐기는 모습이 자주 보입니다.",
        "새로운 표현 즉각 활용": "새로운 표현을 배우면 실제 말하기 활동에서 바로 활용해 보려는 적극성이 돋보였습니다. 영어를 사용하는 데 대한 자신감이 점점 자라고 있습니다.",
        "또렷한 의사 전달": "친구들 앞에서 발표할 때 자신의 생각을 또렷하게 전달하려는 모습이 인상적이었습니다. 표현력뿐 아니라 자신감도 함께 성장하고 있습니다.",
        "실수 두려워하지 않는 용기": "말하기 활동에서는 실수를 크게 의식하지 않고 자신 있게 표현하려고 노력하는 모습이 인상적이었습니다. 적극적인 참여가 영어 실력 향상으로 자연스럽게 이어질 수 있도록 돋보입니다.",
        "활기찬 수업 분위기 주도": "수업에 들어오는 순간부터 밝은 에너지로 교실 분위기를 활기차게 만들어 주고 있습니다. 적극적인 참여가 큰 장점입니다."
    },
    "🌟 리더십 및 협력": {
        "모둠 활동 분위기 메이커": "모둠 활동이 시작되면 친구들이 활동에 잘 참여할 수 있도록 자연스럽게 분위기를 이끌어 주는 모습을 보여주었습니다.",
        "어려워하는 친구 배려": "친구들이 어려워하는 부분이 있을 때 먼저 도와주거나 설명해 주려는 모습이 자주 보였습니다. 배려와 책임감이 함께 돋보이는 학생입니다.",
        "전체 참여 유도": "활동 중 자신의 역할을 충실히 수행할 뿐만 아니라 주변 친구들의 참여도 함께 이끌어 주는 모습이 인상적이었습니다.",
        "원활한 소통 능력": "모둠 활동에서 친구들과 원활하게 소통하며 긍정적인 분위기를 만들어 주고 있습니다.",
        "의견 조율과 존중": "친구들과 협력하는 과정에서 자신의 의견을 잘 전달하면서도 상대방의 의견을 존중하는 성숙한 모습을 보여주었습니다."
    },
    "💪 노력 및 끈기": {
        "포기하지 않는 끈기": "쉽지 않은 문제를 만나도 바로 포기하기보다 한 번 더 생각해 보려는 모습이 자주 보였습니다. 꾸준히 노력하는 태도가 매우 기특합니다.",
        "과정 중심의 학습": "정답을 맞히는 것보다 배우는 과정에 집중하려는 모습이 인상적이었습니다. 작은 성장도 소중하게 만들어 가고 있습니다.",
        "반복 학습을 통한 성장": "처음에는 어려워하던 내용도 반복 학습을 통해 차근차근 익혀 나가는 모습을 보여주었습니다.",
        "오답 재도전": "자신의 실수를 그냥 넘기지 않고 다시 확인하며 더 나은 결과를 만들기 위해 노력하는 모습이 인상적이었습니다.",
        "기복 없는 성실함": "특별한 기복 없이 안정적으로 학습을 이어가며 차곡차곡 실력을 쌓아가고 있습니다."
    },
    "📈 긍정 및 성장": {
        "참여도 눈부신 향상": "처음에는 조심스럽게 참여하던 활동도 이제는 훨씬 적극적으로 참여하는 모습을 보여주고 있습니다. 눈에 띄는 성장이 느껴집니다.",
        "이해도 및 활용도 증가": "배운 표현을 이해하는 속도와 활용하는 능력이 꾸준히 향상되고 있습니다. 학습에 대한 자신감도 함께 높아지고 있습니다.",
        "스스로 해결하는 힘": "이전에는 어려워하던 문제 유형도 스스로 해결하는 경우가 늘어나고 있습니다. 성장의 폭이 크게 느껴집니다.",
        "새로운 과제에 열린 태도": "새로운 활동이나 과제를 항상 긍정적인 태도로 받아들이며 즐겁게 참여하는 모습이 인상적이었습니다.",
        "실패를 두려워하지 않는 도전": "어려운 문제가 나와도 '한번 해볼게요!'라는 마음으로 도전하는 모습이 매우 기특했습니다."
    },
    "🧐 신중 및 차분함": {
        "신중한 답변": "수업 시간에는 다소 조용한 편이지만, 교사의 질문에 끝까지 생각하며 답하려는 모습이 인상적이었습니다. 자신의 속도로 차근차근 참여하며 성장하고 있습니다.",
        "점진적인 용기": "발표나 말하기 활동에서는 처음에 망설이는 모습도 있었지만, 최근에는 조금씩 용기를 내어 참여하는 모습이 보이고 있습니다. 작은 변화가 매우 기특하게 느껴집니다.",
        "내실 있는 학습": "눈에 띄게 표현하기보다는 차분히 수업을 따라오며 배운 내용을 자신의 것으로 만들어 가고 있습니다. 꾸준한 성장이 기대되는 학생입니다.",
        "이해 후 표현하는 꼼꼼함": "교사의 설명을 집중해서 듣고 이해한 뒤 조심스럽게 표현하는 모습이 자주 보였습니다. 신중하게 생각하는 태도가 큰 강점입니다.",
        "묵묵한 책임감": "활동 중에는 조용히 참여하지만 맡은 역할은 끝까지 책임감 있게 수행하는 모습을 보여주었습니다. 성실함이 돋보이는 학생입니다."
    },
    "🌈 감성 및 공감": {
        "깊이 있는 의미 파악": "수업 중 이야기나 활동의 의미를 깊이 있게 생각하며 자신만의 시각으로 표현하는 모습이 인상적이었습니다.",
        "타인에 대한 따뜻한 공감": "친구들의 감정이나 상황을 잘 이해하고 공감하는 따뜻한 모습을 자주 보여주었습니다.",
        "섬세한 표현력": "표현 활동에서 자신의 생각과 느낌을 섬세하게 담아내는 모습이 돋보였습니다.",
        "세심한 관찰력": "작은 변화도 잘 알아차리고 주변을 세심하게 살피는 모습이 인상적이었습니다.",
        "진정성 있는 참여": "풍부한 감성과 배려심을 바탕으로 수업 활동에 진정성 있게 참여하고 있습니다."
    }
}

TEACHER_TEMPLATES = {
    "선택 안 함 (아래 직접 입력)": "",
    "🌱 [기초/격려] 과정 중심의 응원 (태도 칭찬)": "지금 당장 눈에 보이는 큰 점수보다 중요한 건 {name}가 포기하지 않고 영어를 대하는 태도입니다. 기초를 다지는 지금의 시간이 훗날 {name}가 영어를 즐길 수 있는 가장 든든한 밑거름이 될 거예요. {name}의 속도에 맞춰, 저도 포기하지 않고 끝까지 함께 걷겠습니다.",
    "🌿 [중간/도약] 성실함 인정과 확신": "수업에 임하는 {name}의 모습에서 매달 깊은 신뢰를 느낍니다. 성실함은 그 무엇보다 강력한 실력입니다. 지금처럼 기본기를 착실히 다져간다면, 머지않아 더 높은 도약의 순간을 맞이하게 될 것이라 확신합니다.",
    "🌳 [우수/심화] 더 높은 곳을 향한 심화 도전": "현재 실력에 안주하지 않고 더 깊이 있는 내용을 이해하려는 {name}의 열정이 참 멋집니다. 이제는 조금 더 난도가 높은 심화 과정으로 아이의 가능성을 넓혀보려 합니다. 아이의 잠재력이 더 넓은 세상에서 활짝 피어날 수 있도록 이끌겠습니다."
}

CLOSING_MENT_DB = {
    "🤝 [협력 강조형] 신뢰와 파트너십을 강조할 때": "아이의 성장은 저와 학부모님의 따뜻한 관심이 함께 모일 때 더욱 빛이 난다고 믿습니다. 우리 아이가 영어를 통해 더 넓은 세상을 꿈꿀 수 있도록, 저 또한 최선을 다해 지도하겠습니다. 늘 믿고 맡겨주셔서 진심으로 감사합니다.",
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

# --- 4. 교재별 성적표 및 범위 설정 ---
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
selected_sub_narrative = ""

if not primary_units:
    st.warning("⚠️ 위 2번 항목에서 '평가 단원' 또는 'Target 음가'를 먼저 선택해 주셔야 세부 분석이 가능합니다.")
else:
    p_score_num = parse_score(primary_score)
    label_subject = "음가/알파벳" if is_phonics else "단원"
    
    # 주교재 로직
    if is_phonics and test_range == "Final Test (Unit 1-8)":
        st.markdown(f"🏆 **주교재 분석 유형 : 🌟 파닉스 Final Test**")
        type2_bad = st.multiselect(f"🟧 개별 맞춤 복습이 조금 더 필요한 {label_subject} (없으면 비워두세요)", primary_units)
    else:
        if p_score_num >= 90:
            st.markdown(f"🏆 **주교재 분석 유형 : 상위권 (90점 이상)**")
            type1_well = st.multiselect(f"🥇 완벽하게 마스터하고 깊이 이해한 {label_subject}", primary_units, default=primary_units)
        elif p_score_num >= 75:
            st.markdown(f"📈 **주교재 분석 유형 : 중위권 (75점 ~ 89점)**")
            col_t2_1, col_t2_2 = st.columns(2)
            with col_t2_1: type2_well = st.multiselect(f"🟩 높은 이해도를 보이며 잘한 {label_subject}", primary_units)
            with col_t2_2: type2_bad = st.multiselect(f"🟥 미세 보완이 필요한 {label_subject}", [u for u in primary_units if u not in type2_well])
        else:
            st.markdown(f"🌱 **주교재 분석 유형 : 집중 케어권 (74점 이하)**")
            col_t3_1, col_t3_2 = st.columns(2)
            with col_t3_1: type3_well = st.multiselect(f"🟦 어려운 와중에도 기특하게 잘 따라와 준 {label_subject}", primary_units)
            with col_t3_2: type3_bad = st.multiselect(f"🟧 복습과 정교화 케어가 필요한 {label_subject}", [u for u in primary_units if u not in type3_well])

    # 부교재 맞춤형 선택 로직 (v22.2 신규)
    if not is_phonics and sub_book and sub_book != "선택안함":
        st.markdown("---")
        s_score_num = parse_score(sub_score)
        if s_score_num >= 90:
            st.markdown(f"🏆 **부교재 분석 유형 : 상위권 (90점 이상)**")
            sub_opt = st.radio("부교재 성취도 코멘트 선택", list(SUB_BOOK_NARRATIVE_DB["high"].keys()))
            selected_sub_narrative = SUB_BOOK_NARRATIVE_DB["high"][sub_opt]
        elif s_score_num >= 75:
            st.markdown(f"📈 **부교재 분석 유형 : 중위권 (70점 ~ 89점)**")
            sub_opt = st.radio("부교재 성취도 코멘트 선택", list(SUB_BOOK_NARRATIVE_DB["mid"].keys()))
            selected_sub_narrative = SUB_BOOK_NARRATIVE_DB["mid"][sub_opt]
        else:
            st.markdown(f"🌱 **부교재 분석 유형 : 집중 케어권 (69점 이하)**")
            sub_opt = st.radio("부교재 성취도 코멘트 선택", list(SUB_BOOK_NARRATIVE_DB["low"].keys()))
            selected_sub_narrative = SUB_BOOK_NARRATIVE_DB["low"][sub_opt]

# --- 6. 학생 성향 및 긍정 피드백 ---
st.subheader("📊 4. 수업 태도 및 성향 피드백")
col5, col6, col7 = st.columns(3)
with col5: rating_understand = st.selectbox("수업 이해도", list(UNDERSTAND_TEXTS.keys()))
with col6: rating_present = st.selectbox("발표 및 참여", list(PRESENT_TEXTS.keys()))
with col7: rating_focus = st.selectbox("집중도", list(FOCUS_TEXTS.keys()))

st.markdown("**[수업 시간 아이를 빛내주는 칭찬 성향 선택]**")
selected_traits = []

with st.expander("✨ 아이의 7대 핵심 성향별 키워드 코멘트 선택 (복수 선택 가능)"):
    st.caption("선택지에는 요약된 키워드만 보이며, 최종 성적표에는 정성스러운 긴 문장으로 자동 변환되어 입력됩니다.")
    for category, items in TRAITS_DB.items():
        selected_keys = st.multiselect(f"🔹 {category}", list(items.keys()), key=f"trait_{category}")
        for key in selected_keys:
            selected_traits.append(items[key])

st.subheader("🔍 5. 영역별 보완점 및 큐브 케어 플랜")
st.caption("학생에게 필요한 맞춤형 피드백을 영역별로 자유롭게 선택해 주세요. (다중 선택 가능)")

if is_phonics:
    available_areas = ["Phonics (파닉스)", "General (공통/학습태도)"]
else:
    available_areas = ["Course Book (코스북)", "Reading (독해)", "Grammar (문법)", "Writing (영작)", "General (공통/학습태도)"]

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
            objective_list_text += f" - 학습 목표: {primary_book} 핵심 어휘 습득 및 발화 훈련"
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
                            objective_list_text += f"   - 평가 진행 단원: {', '.join(selected_in_cluster)}\n"
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
            primary_narrative = f"이번 파닉스 Final Test(Unit 1-8)를 통해 종합적으로 점검한 결과, 1단원부터 8단원까지의 전체적인 음가와 규칙을 훌륭하게 마스터하고 뛰어난 언어적 이해도를 보여주었습니다. 포기하지 않고 성실하게 전체 단원을 마무리한 {selected_en_name}를 크게 칭찬해 주고 싶습니다! "
            if bad_str:
                primary_narrative += f" 다음 단계 도약을 위해, 복습 시 {bad_str}영역의 미세한 발음 및 규칙 적용 부분만 조금 더 신경 써서 섬세하게 보완하겠습니다."
            else:
                primary_narrative += "모든 영역에서 빈틈없는 완벽한 성취를 보여주었으며, 이 단단한 기초를 바탕으로 다음 레벨에서도 흔들림 없이 훌륭한 모습을 이어갈 것이라 확신합니다."
        else:
            if p_score_num >= 90:
                well_str = ", ".join(type1_well) if type1_well else f"이번 달 전 {target_word}"
                primary_narrative = f"이번 달 주요 핵심 과정인 {well_str}영역의 개념과 규칙을 깊이 있게 완벽하게 이해하고 소화해 냈습니다. 우리 {selected_en_name}에게 앞으로도 영어 공부가 더욱 즐겁고 깊이 있는 수업이 될 수 있도록 늘 칭찬하며 최선으로 노력하겠습니다."
            elif p_score_num >= 75:
                well_str = ", ".join(type2_well) if type2_well else "주요 학습"
                bad_str = ", ".join(type2_bad) if type2_bad else f"일부 {target_word}"
                primary_narrative = f"이번 달 과정 중 {well_str}영역에서 매우 높은 이해도를 보이며 안정적으로 과제를 수행해 냈습니다. 다만, {bad_str} 부분에서는 개념적 규칙을 완벽히 정교하게 체화하는 데 있어 아주 미세하게 아쉬운 부분이 관찰되었습니다. 해당 영역은 다음 달에도 유기적인 연계 학습 및 꼼꼼한 반복 학습을 병행하여 부족한 틈새를 단단하게 다지고 완벽하게 채워가겠습니다."
            else:
                well_str = ", ".join(type3_well) if type3_well else "기본 진도"
                bad_str = ", ".join(type3_bad) if type3_bad else f"일부 {target_word}"
                primary_narrative = f"이번 달 새로 배운 과정이 다소 어려울 수 있는 내용이었음에도 불구하고, {well_str}부분을 끝까지 잘 따라와 주었습니다. 또한 수업 시간에 설명을 집중해서 들으며 이해하려고 노력하는 모습이 돋보였습니다. 작은 성공 경험들이 쌓이며 점차 자신감을 얻어가고 있습니다."

        sub_narrative = ""
        # 부교재 서술 로직 업데이트 (선택된 내용 반영)
        if sub_book and sub_book != "선택안함":
            if selected_sub_narrative:
                sub_narrative = f"\n\n또한, {sub_book} 학습 과정에서도 유의미한 성장이 있었습니다. {selected_sub_narrative}"
                
        objective_narrative = primary_narrative + sub_narrative

        u_sentence = UNDERSTAND_TEXTS[rating_understand]
        p_sentence = PRESENT_TEXTS[rating_present]
        f_sentence = FOCUS_TEXTS[rating_focus]
        
        traits_text = ""
        if selected_traits:
            traits_text = "\n" + "\n".join([f"- {trait}" for trait in selected_traits])
            
        positive_section = f"- {u_sentence}\n- {p_sentence}\n- {f_sentence}{traits_text}"

        care_plan_text = ""
        if selected_weaknesses:
            for area, weaknesses in selected_weaknesses.items():
                for w in weaknesses:
                    plan = DIAGNOSIS_DB[area][w]
                    care_plan_text += f" [{area} - {w}]\n  {plan}\n\n"
        if not care_plan_text: care_plan_text = f"· 현재 {selected_en_name}는 모든 학습 영역을 균형 있게 소화하며 안정적인 학습 흐름을 유지하고 있습니다. 눈에 띄는 강점만큼이나 꾸준함과 성실함이 돋보이며, 차근차근 실력을 쌓아가고 있는 모습이 인상적입니다.\n"

        custom_processed_text = ""
        if selected_template != "선택 안 함 (아래 직접 입력)":
            custom_processed_text += TEACHER_TEMPLATES[selected_template].format(name=selected_en_name) + " "
        if teacher_custom_feedback:
            custom_processed_text += refine_teacher_feedback(teacher_custom_feedback.strip(), selected_en_name)
        if not custom_processed_text.strip():
            custom_processed_text = f"이번 한 달 동안 {selected_en_name}와 함께하며, 매 수업 성실하게 참여하고 조금씩 성장해 나가는 모습이 매우 인상적이었습니다. 앞으로도 아이의 강점을 더욱 키우고 자신감을 쌓아갈 수 있도록 든든한 학습 파트너가 되어 함께하겠습니다."
        
        final_closing_ment = CLOSING_MENT_DB[selected_closing]

        st.session_state.generated_feedback = f"""
안녕하세요, 큐브어학원입니다.
{selected_month} 동안 {selected_en_name}가 보여준 노력과 성장을 확인하는 월말평가가 진행되었습니다.
이번 평가는 단순히 점수를 확인하는 것을 넘어, 아이의 학습 과정과 성장 모습을 살펴보고 앞으로의 발전 방향을 함께 계획하는 과정입니다.
아래 내용을 통해 {selected_en_name}의 학습 성과와 앞으로의 지도 방향을 안내해 드립니다.

■ 현재 레벨: {selected_level}
■ 학생 이름: {selected_en_name} ({selected_kr_name})
■ 평가 결과 (100점 만점 기준):
{score_report}


[1. 핵심 단원별 목표 성취 리포트]
이번 달 교재 학습을 통해 아이가 학습 했던 핵심 유닛별 목표와 달성도 분석입니다.

💡 [이번 달 상세 학습 목표 및 범위]
{objective_list_text.strip()}

💡 [단원별 실제 성취도 다이어리]
{objective_narrative}


[2. 학생 성향 및 태도 리포트]
{positive_section}


[3. 큐브 영역별 밀착 케어 플랜]
{care_plan_text.strip()}


[4. 담당 강사 개별 밀착 소견]
{custom_processed_text.strip()}


{final_closing_ment}

- 큐브어학원 드림 -
        """.strip()
        st.success(f"{selected_month} 큐브어학원 명품 피드백 메세지가 성공적으로 빌드되었습니다!")

if st.session_state.generated_feedback:
    st.divider()
    st.text_area("📋 완성된 피드백 (마우스로 클릭하여 전체 복사 가능)", value=st.session_state.generated_feedback, height=800)
