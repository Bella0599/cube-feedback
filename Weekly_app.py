import streamlit as st
import pandas as pd

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")

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
    selected_room = st.sidebar.selectbox("🚪 1단계: 룸(Room) 선택", TARGET_ROOMS)
    
    if selected_room in all_rooms:
        df = all_rooms[selected_room]
        
        # [자동 진단] 만약 A열을 추가 안 했다면 경고 띄우기
        if "Level" in str(df.columns[0]) or "레벨" in str(df.columns[0]):
            st.error(f"🚨 '{selected_room}' 탭에 A열(주차)이 추가되지 않았습니다! 구글 시트를 확인해 주세요.")
            st.write("현재 파이썬이 인식한 1~3번째 열 제목:", list(df.columns[0:3]))
        else:
            col_week = df.columns[0]   # A열: 주차
            col_level = df.columns[2]  # C열: 레벨
            col_kor = df.columns[3]    # D열: 한글이름
            col_eng = df.columns[4]    # E열: 영어이름
            
            # 리포트가 있는 W열(22번 인덱스) 찾기 (안전장치 포함)
            if len(df.columns) > 22:
                col_report = df.columns[22]  
            else:
                col_report = df.columns[-1] # 열이 모자라면 맨 마지막 열 사용

            week_list = sorted(df[col_week].dropna().unique().astype(str))
            
            # 빈 값('nan')이 선택지에 나오는 것 방지
            week_list = [w for w in week_list if w.lower() != 'nan']
            
            if not week_list:
                st.warning(f"'{selected_room}'의 A열(주차)에 입력된 데이터가 없습니다.")
            else:
                selected_week = st.sidebar.selectbox("📅 2단계: 주차 선택", week_list)
                
                df_week = df[df[col_week].astype(str) == selected_week]
                class_list = df_week[col_level].dropna().unique()
                selected_class = st.sidebar.selectbox("🎯 3단계: 반 선택", class_list)
                
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
    st.error(f"데이터 로드 중 알 수 없는 오류가 발생했습니다.\n상세 오류: {e}")
