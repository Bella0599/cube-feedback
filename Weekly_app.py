import streamlit as st
import pandas as pd

# 웹 페이지 기본 설정
st.set_page_config(page_title="주간 리포트 자동 발송 시스템", page_icon="📋", layout="centered")

st.title("📋 주간 리포트 자동 복사기")
st.markdown("구글 시트에서 다운로드한 **엑셀 파일(.xlsx)**을 올려주세요. 반을 선택하면 복사 버튼이 생성됩니다.")

# 1. 파일 업로드 창 생성
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=['xlsx'])

if uploaded_file is not None:
    # 2. 엑셀 데이터 읽기 
    # (주의: 구글 시트의 2행이 헤더, 3행부터 데이터라고 가정하여 header=1 로 설정)
    try:
        df = pd.read_excel(uploaded_file, header=1)
        
        # 엑셀 열 이름 매핑 (원장님 시트 상황에 맞게 컬럼명을 수정하세요)
        # 예: B열='Level', C열='한글이름', D열='영어이름', U열='최종리포트'
        col_level = df.columns[1]  # B열 (인덱스 1)
        col_kor = df.columns[2]    # C열 (인덱스 2)
        col_eng = df.columns[3]    # D열 (인덱스 3)
        col_report = df.columns[20] # U열 (인덱스 20)

        # 빈 레벨(결측치) 제외하고 존재하는 반 이름만 목록으로 추출
        class_list = df[col_level].dropna().unique()

        st.divider()

        # 3. 반 선택 드롭다운
        selected_class = st.selectbox("🎯 리포트를 확인할 반을 선택하세요:", class_list)

        # 4. 선택한 반의 학생들만 필터링
        filtered_df = df[df[col_level] == selected_class]

        st.success(f"**{selected_class}** 반의 리포트가 준비되었습니다. (총 {len(filtered_df)}명)")

        # 5. 학생별 리포트 출력 (자동 복사 버튼 포함)
        for index, row in filtered_df.iterrows():
            student_name = f"{row[col_eng]} ({row[col_kor]})"
            report_text = row[col_report]

            # 리포트 내용이 비어있지 않은 경우에만 출력
            if pd.notna(report_text) and str(report_text).strip() != "":
                st.subheader(f"🧑‍🎓 {student_name}")
                
                # 핵심: st.code를 사용하면 우측 상단에 복사(Copy) 버튼이 자동 생성됨
                st.code(report_text, language='text')

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다. 시트 양식을 확인해주세요.\n오류 내용: {e}")
else:
    st.info("👆 위 영역에 구글 시트에서 다운받은 엑셀 파일을 드래그 앤 드롭 하세요.")
