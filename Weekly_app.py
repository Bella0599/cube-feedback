import streamlit as st
import pandas as pd

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("지정된 3개의 룸(Mint_room, Blue_room, Pink_room)에서 최신 리포트(V열)를 불러옵니다.")

EXCEL_URL = "https://docs.google.com/spreadsheets/d/1Om-TrhkCmuPNwdwj1S420SXeGr_pPQuA3pOwtI0orPM/export?format=xlsx"

# 대상 룸 고정
TARGET_ROOMS = ["Mint_room", "Blue_room", "Pink_room"]

@st.cache_data(ttl=20) 
def load_target_rooms(url):
    return pd.read_excel(url, sheet_name=TARGET_ROOMS, header=1)

if st.button("🔄 구글 시트 최신 내용 즉시 불러오기"):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner('구글 시트에서 데이터를 불러오는 중...'):
        all_rooms = load_target_rooms(EXCEL_URL)
    
    st.sidebar.header("📍 필터 선택")
    
    # 1단계: 룸 선택
    selected_room = st.sidebar.selectbox("🚪 1단계: 룸(Room) 선택", TARGET_ROOMS)
    
    if selected_room in all_rooms:
        df = all_rooms[selected_room]
        
        if df.empty:
            st.warning(f"'{selected_room}' 룸에 입력된 데이터가 없습니다.")
        else:
            col_level = df.columns[1]  # B열: 레벨
            col_kor = df.columns[2]    # C열: 한글이름
            col_eng = df.columns[3]    # D열: 영어이름
            
            # 원장님 요청: U열(20)에서 V열(21)의 정보로 변경
            if len(df.columns) > 21:
                col_report = df.columns[21]  # V열 (인덱스 21)
            else:
                col_report = df.columns[-1]

            class_list = df[col_level].dropna().unique()
            
            # 2단계: 반 선택
            selected_class = st.sidebar.selectbox("🎯 2단계: 반 선택", class_list)
            
            if selected_class:
                filtered_df = df[df[col_level] == selected_class]
                
                st.success(f"✅ **[{selected_room}] - {selected_class}** 반 리포트 연동 완료 (총 {len(filtered_df)}명)")
                st.divider()
                
                displayed_count = 0
                for index, row in filtered_df.iterrows():
                    kor_name = row[col_kor] if pd.notna(row[col_kor]) else ""
                    eng_name = row[col_eng] if pd.notna(row[col_eng]) else "이름없음"
                    student_title = f"🧑‍🎓 {eng_name} ({kor_name})" if kor_name else f"🧑‍🎓 {eng_name}"
                    
                    report_text = row[col_report]
                    
                    # V열 내용이 존재할 때만 화면에 나열
                    if pd.notna(report_text) and str(report_text).strip() != "" and str(report_text).strip().lower() != "nan":
                        st.subheader(student_title)
                        st.code(str(report_text), language='text')
                        displayed_count += 1
                
                if displayed_count == 0:
                    st.info("💡 이 반에는 아직 작성된 V열 내용이 없습니다.")
    else:
        st.error(f"구글 시트에 '{selected_room}' 탭이 존재하지 않습니다.")

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다. 오류 내용: {e}")
