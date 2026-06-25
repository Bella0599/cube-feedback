import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("지정된 3개의 룸(Mint_room, Blue_room, Pink_room)에서 최신 리포트를 주르륵 나열합니다.")

# 구글 시트 주소
EXCEL_URL = "https://docs.google.com/spreadsheets/d/1DxGvm9hSX8I3AtkH0oOzzpcJFyJFYYs05R7vll6mqjE/export?format=xlsx"

# 🌟 딱 이 3개 룸 이름만 가져오도록 리스트를 고정합니다.
TARGET_ROOMS = ["Mint_room", "Blue_room", "Pink_room"]

@st.cache_data(ttl=20) 
def load_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if b"html" in response.content[:150].lower() or b"sign in" in response.content[:500].lower():
        raise PermissionError("구글 시트의 공유 권한이 '링크가 있는 모든 사용자(뷰어)'로 설정되어 있는지 꼭 확인해 주세요.")
        
    excel_file = pd.ExcelFile(io.BytesIO(response.content), engine='openpyxl')
    all_sheet_names = excel_file.sheet_names
    result = {}
    
    # 시트 전체 탭 중 지정한 3개의 룸만 필터링해서 분석합니다.
    for sheet_name in TARGET_ROOMS:
        if sheet_name in all_sheet_names:
            df_raw = excel_file.parse(sheet_name=sheet_name, header=None)
            
            header_idx = 0
            for i in range(min(5, len(df_raw))):
                row_str = " ".join(df_raw.iloc[i].dropna().astype(str).tolist()).lower()
                if '주차' in row_str or 'level' in row_str or 'name' in row_str:
                    header_idx = i
                    break
                    
            result[sheet_name] = excel_file.parse(sheet_name=sheet_name, header=header_idx)
    return result

if st.button("🔄 구글 시트 최신 내용 즉시 불러오기"):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner('구글 시트에서 데이터를 안전하게 불러오는 중...'):
        all_rooms = load_data(EXCEL_URL)
    
    st.sidebar.header("📍 3단계 필터 선택")
    
    available_rooms = list(all_rooms.keys())
    
    if not available_rooms:
        st.error("구글 시트에서 Mint_room, Blue_room, Pink_room 탭을 찾지 못했습니다. 구글 시트 하단의 탭 이름을 다시 확인해 주세요.")
    else:
        # 1단계: 지정한 3개 룸만 선택지에 노출됩니다.
        selected_room = st.sidebar.selectbox("🚪 1단계: 룸(Room) 선택", available_rooms)
        
        df = all_rooms[selected_room]
        
        col_week = None
        col_level = None
        col_kor = None
        col_eng = None
        col_report = None

        for col in df.columns:
            c_str = str(col).strip().lower()
            if 'report' in c_str or '리포트' in c_str:
                col_report = col
            elif '주차' in c_str or 'week' in c_str:
                col_week = col
            elif 'level' in c_str or '레벨' in c_str or 'class' in c_str:
                col_level = col
            elif '(k)' in c_str or '한글' in c_str:
                col_kor = col
            elif '(e)' in c_str or '영어' in c_str:
                col_eng = col

        if not col_week: col_week = df.columns[0]
        if not col_level: col_level = df.columns[2] if len(df.columns) > 2 else df.columns[0]
        if not col_kor: col_kor = df.columns[3] if len(df.columns) > 3 else df.columns[0]
        if not col_eng: col_eng = df.columns[4] if len(df.columns) > 4 else df.columns[0]
        
        if not col_report:
            for col in df.columns:
                sample_vals = df[col].dropna().astype(str).tolist()
                if any(s.startswith('■') for s in sample_vals[:5]):
                    col_report = col
                    break
            if not col_report:
                col_report = df.columns[22] if len(df.columns) > 22 else df.columns[-1]

        # 2단계: 주차 선택
        fixed_weeks = ["1주차", "2주차", "3주차", "4주차", "5주차"]
        selected_week = st.sidebar.selectbox("📅 2단계: 주차 선택", fixed_weeks)
        
        search_keyword = selected_week.replace("차", "").strip()
        df_week = df[df[col_week].astype(str).str.contains(search_keyword, na=False)]
        
        # 3단계: 반 선택
        class_list = df_week[col_level].dropna().unique()
        
        if len(class_list) == 0:
            st.sidebar.warning(f"{selected_week}에 입력된 학생 데이터가 없습니다.")
        else:
            selected_class = st.sidebar.selectbox("🎯 3단계: 반 선택", class_list)
            
            if selected_class:
                final_df = df_week[df_week[col_level] == selected_class]
                
                st.success(f"✅ **[{selected_week} / {selected_room} / {selected_class}]** 리포트 자동 추출 완료 (총 {len(final_df)}명)")
                st.divider()

                displayed_count = 0
                for index, row in final_df.iterrows():
                    report_text = row[col_report]
                    if pd.notna(report_text) and str(report_text).strip() != "" and str(report_text).lower() != "nan":
                        kor_name = row[col_kor] if pd.notna(row[col_kor]) else ""
                        eng_name = row[col_eng] if pd.notna(row[col_eng]) else "이름없음"
                        
                        st.subheader(f"🧑‍🎓 {eng_name} ({kor_name})")
                        st.code(str(report_text), language='text')
                        displayed_count += 1
                        
                if displayed_count == 0:
                    st.info(f"💡 {selected_week} {selected_class} 반에는 작성된 리포트 내용이 없습니다.")

except PermissionError as pe:
    st.error(f"🔓 권한 오류: {pe}")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다.\n오류 내용: {e}")
