# OpenAI + 챗봇 사용 웹 앱

import streamlit as st
from streamlit_chat import message
import openai
import os

# OPenAI API 키 설정
# openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 세션 상태 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = [] # 응답을 위해 생성. 빈 리스트로 초기화

if 'past' not in st.session_state:
    st.session_state['past'] = [] # 사용자 입력을 위해 생성. 빈 리스트로 초기화
    
# OpenAI 라이브러리의 ChatCompletion을 이용해 질문에 대한 응답 얻기 
def response_from_openAI(user_query):
    
    # 과일 관련 정보 생성
    prince_info = """
            - 판매하는 과일의 종류: 딸기, 배, 사과, 포도.
            - 딸기: 1Kg에 5000원, 배: 2개에 4000원, 사과: 1 box에 30000원, 포도: 5 송이 10000원.
            - 박스는 box와 같은 단위로 사과를 세는 단위이다. 송이는 포도를 세는 단위이다.
            - 전체 합계가 5만원 (=50000원)을 이상이면 무료 배달(배송)이 가능하다. """

    # system의 content에 입력할 내용 생성
    system_content = f"""아래의 과일 정보를 이용해 과일 가격 이야기해 줘.
                과일 정보: {prince_info}
                만약 과일 정보가 없으면 '그런 과일은 판매하지 않습니다'라고 답해줘."""

    # OpenAI 라이브러리 활용 (Chat 완성). system의 content에 필요한 정보를 입력함
    response = openai.ChatCompletion.create(
                        messages=[
                            {'role': 'system', 'content': system_content},
                            {'role': 'user', 'content': user_query},
                        ],
                        model="gpt-3.5-turbo",
                        temperature=0.1 
    )
    
    return response['choices'][0]['message']['content']

st.title("OpenAI + 스트림릿챗 활용 챗봇")

input_text = st.text_input("당신: ","안녕하세요.", key="input")

# 텍스트 입력이 있으면 수행
if input_text: 
    output = response_from_openAI(input_text) 
    
    st.session_state.past.append(input_text)  # 리스트 뒤에 요소 추가
    st.session_state.generated.append(output) # 리스트 뒤에 요소 추가
    
# st.session_state['generated']가 빈 리스트가 아니면 수행
if st.session_state['generated']: 
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i)+'_user')
        message(st.session_state["generated"][i], key=str(i))
