import streamlit as st
import pandas as pd

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("A열(주차) 도입으로 밀려난 구글 시트 구조에 맞춤 수정된 버전입니다.")

EXCEL_URL = "https://docs.google.com/spreadsheets/d/1DxGvm9hSX8I3AtkH0oOzzpcJFyJFYYs05R7vll6mqjE/export?format=xlsx"
TARGET_ROOMS = ["Mint_room", "Blue_room", "Pink_room"]

@st.cache_data(ttl=20) 
def load_data(url):
    return pd.read_excel(url, sheet_name=TARGET_ROOMS, header=1, engine='openpyxl')

if st.button("🔄 구글 시트 최신 내용 즉시 불러오기"):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner('데이터 분석 중...'):
        all_rooms = load_data(EXCEL_URL)
    
    st.sidebar.header("📍 3단계 필터 선택")
    
    # 1. 룸 선택 (시트 탭)
    selected_room = st.sidebar.selectbox("🚪 1단계: 룸(Room) 선택", TARGET_ROOMS)
    
    if selected_room in all_rooms:
        df = all_rooms[selected_room]
        
        # ⚠️ 열 삽입으로 인해 한 칸씩 밀린 인덱스를 정확하게 재설정합니다.
        col_week = df.columns[0]   # A열: 주차 (신설)
        col_level = df.columns[2]  # C열: 레벨 (기존 B열에서 밀림)
        col_kor = df.columns[3]    # D열: 한글이름 (기존 C열에서 밀림)
        col_eng = df.columns[4]    # E열: 영어이름 (기존 D열에서 밀림)
        
        # 기존 V열(21)에서 한 칸 밀린 W열(22)을 읽어옵니다.
        if len(df.columns) > 22:
            col_report = df.columns[22]  
        else:
            col_report = df.columns[-1]

        # 2. 주차 선택 (A열 필터)
        week_list = sorted(df[col_week].dropna().unique().astype(str))
        selected_week = st.sidebar.selectbox("📅 2단계: 주차 선택", week_list)
        
        # 3. 반 선택 (C열 필터)
        df_week = df[df[col_week].astype(str) == selected_week]
        class_list = df_week[col_level].dropna().unique()
        selected_class = st.sidebar.selectbox("🎯 3단계: 반 선택", class_list)
        
        # 최종 결과 필터링
        final_df = df_week[df_week[col_level] == selected_class]
        
        st.success(f"✅ **[{selected_week} / {selected_room} / {selected_class}]** 리포트 조회 완료")
        st.divider()

        displayed_count = 0
        for index, row in final_df.iterrows():
            report_text = row[col_report]
            if pd.notna(report_text) and str(report_text).strip() != "" and str(report_text).lower() != "nan":
                st.subheader(f"🧑‍🎓 {row[col_eng]} ({row[col_kor]})")
                st.code(str(report_text), language='text')
                displayed_count += 1
                
        if displayed_count == 0:
            st.info("💡 선택하신 주차와 반에는 작성된 리포트 내용이 없습니다.")

except Exception as e:
    st.error(f"데이터 로드 오류: {e}\n구글 시트 맨 왼쪽에 '주차' 열이 새로 추가되었는지 확인해 주세요.")
