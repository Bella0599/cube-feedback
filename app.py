import streamlit as st
import pandas as pd

st.title("연결 상태 테스트")

sheet_url = "https://docs.google.com/spreadsheets/d/1xwfmM8VELPoMktF7pZugYZxSbf8SCSGo2Ur7DIFCT9E/edit?usp=sharing"
csv_url = sheet_url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=students"

try:
    st.write("데이터 가져오는 중...")
    data = pd.read_csv(csv_url)
    st.write("데이터 가져오기 성공!")
    st.dataframe(data.head()) # 데이터가 보이면 성공입니다.
except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("주소 확인: ", csv_url)
