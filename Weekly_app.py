import streamlit as st
import pandas as pd

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("구글 시트와 실시간 연동되어 최신 리포트가 자동으로 표시됩니다.")

# 400 에러 해결을 위해 가장 안정적인 다운로드 포맷으로 주소를 변경했습니다.
CSV_URL = "https://docs.google.com/spreadsheets/d/1Om-TrhkCmuPNwdwj1S420SXeGr_pPQuA3pOwtI0orPM/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL, header=1) # 2번째 줄(행)을 제목으로 인식

try:
    with st.spinner('최신 데이터를 불러오는 중...'):
        df = load_data()
    
    # 열 위치 설정: B열(1), C열(2), D열(3), U열(20)
    col_level = df.columns[1]  
    col_kor = df.columns[2]    
    col_eng = df.columns[3]    
    col_report = df.columns[20] 

    # 클래스 목록 추출
    class_list = df[col_level].dropna().unique()
    st.divider()

    # 반 선택창
    selected_class = st.selectbox("🎯 리포트를 확인할 반을 선택하세요:", class_list)
    filtered_df = df[df[col_level] == selected_class]

    st.success(f"**{selected_class}** 반의 최신 리포트가 연동되었습니다. (총 {len(filtered_df)}명)")

    # 학생별 리포트 출력
    for index, row in filtered_df.iterrows():
        student_name = f"{row[col_eng]} ({row[col_kor]})"
        report_text = row[col_report]

        if pd.notna(report_text) and str(report_text).strip() != "":
            st.subheader(f"🧑‍🎓 {student_name}")
            st.code(report_text, language='text')

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다. 시트 공유 권한이 '링크가 있는 모든 사용자(뷰어)'인지 확인해주세요!\n오류내용: {e}")
