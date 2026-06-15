import streamlit as st
import pandas as pd

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("구글 시트와 실시간 연동되어 최신 리포트가 자동으로 표시됩니다.")

# 👉 여기에 복사한 구글 시트 주소를 붙여넣으세요! (따옴표 안에)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Om-TrhkCmuPNwdwj1S420SXeGr_pPQuA3pOwtI0orPM/edit?usp=sharing"

@st.cache_data(ttl=60) # 1분 주기로 최신 데이터 갱신 (너무 잦은 새로고침 방지)
def load_google_sheet(url):
    # 구글 시트 접속 주소를 CSV 다운로드 주소로 자동 변환
    csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit" in csv_url:
        csv_url = csv_url.replace("/edit", "/export?format=csv")
        
    # 구글 시트의 2번째 줄(행)이 제목(헤더)이라고 가정 (header=1)
    df = pd.read_csv(csv_url, header=1)
    return df

# URL이 기본값이 아니면 실행
if SHEET_URL != "https://docs.google.com/spreadsheets/d/여기에_복사한_주소_전체를_넣어주세요/edit#gid=0":
    try:
        with st.spinner('구글 시트에서 최신 데이터를 불러오는 중...'):
            df = load_google_sheet(SHEET_URL)
        
        # 열 위치 매핑 (원장님 시트 열 위치에 맞게 수정 가능)
        col_level = df.columns[1]  # B열
        col_kor = df.columns[2]    # C열
        col_eng = df.columns[3]    # D열
        col_report = df.columns[20] # U열

        # 빈 레벨(결측치) 제외
        class_list = df[col_level].dropna().unique()

        st.divider()

        # 반 선택 드롭다운
        selected_class = st.selectbox("🎯 리포트를 확인할 반을 선택하세요:", class_list)

        # 선택한 반 학생들만 필터링
        filtered_df = df[df[col_level] == selected_class]

        st.success(f"**{selected_class}** 반의 최신 리포트가 연동되었습니다. (총 {len(filtered_df)}명)")

        # 학생별 리포트 출력 및 복사 버튼
        for index, row in filtered_df.iterrows():
            student_name = f"{row[col_eng]} ({row[col_kor]})"
            report_text = row[col_report]

            # 리포트 내용이 비어있지 않은 경우에만 표시
            if pd.notna(report_text) and str(report_text).strip() != "":
                st.subheader(f"🧑‍🎓 {student_name}")
                st.code(report_text, language='text')

    except Exception as e:
        st.error(f"데이터를 불러오지 못했습니다. 시트 주소나 공유 권한 설정을 다시 확인해주세요.\n오류 내용: {e}")
else:
    st.info("👆 파이썬 코드(app.py) 10번째 줄에 구글 시트 주소(SHEET_URL)를 먼저 입력해주세요!")
