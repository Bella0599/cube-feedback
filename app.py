def load_students_data(url):
    csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=students"
    
    # 💡 디버깅: 파이썬이 가져온 '원문'이 무엇인지 바로 확인
    import requests
    response = requests.get(csv_url)
    st.write("--- 파이썬이 받아온 원문 시작 ---")
    st.text(response.text[:500]) # 가져온 데이터의 앞부분 500자만 출력
    st.write("--- 파이썬이 받아온 원문 끝 ---")
    
    # 여기서 원문에 '<!DOCTYPE html>' 같은 글자가 보인다면? 
    # -> 구글이 로그인 페이지를 띄운 것입니다. (권한/게시 문제)
    
    data = pd.read_csv(csv_url)
    data.columns = data.columns.str.strip()
    return data
