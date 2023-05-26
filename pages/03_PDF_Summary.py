# PDF 문서를 요약하는 웹 앱

import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
import tiktoken
import textwrap

# OpenAI 라이브러리를 이용해 텍스트를 요약하는 함수
def summarize_text(user_text, lang="en"):
    # API 키 설정
    # openai.api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # 대회 메시지 정의
    if lang == "en":
        messages = [ 
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"Summarize the following \n {user_text}"}
        ]
    elif lang == "ko":
        messages = [ 
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"다음의 내용을 한글로 요약해 주세요 \n {user_text}"}
        ]
        
    # Chat API 호출
    response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=0.3 )
    
    summary = response["choices"][0]["message"]["content"]
    return summary

# 영어를 한글로 번역하는 함수
def traslate_english_to_korean_using_openAI(text):    
    # API 키 설정
    # openai.api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # 대화 메시지 정의
    content = f"Translate the following English sentences into Korean.\n {text}"
    messages = [ {"role": "user", "content": content} ]

    # Chat API 호출
    response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo", # 사용할 모델 선택 
                            messages=messages, # 전달할 메시지 지정
                            temperature=0.8, # 완성의 다양성을 조절하는 온도 설정
                            n=1 # 생성할 완성의 개수 지정
                            )

    # 응답 출력
    assistant_reply = response.choices[0].message['content'] # 첫 번째 응답 결과 가져오기
    
    return assistant_reply 

st.title("PDF 문서를 요약하는 웹 앱")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요.", type='pdf')

radio_selected_lang = st.radio('PDF 문서 언어', ['한국어', '영어'], index=1, horizontal=True)

if radio_selected_lang == '영어':
    checked = st.checkbox('한국어 번역 추가')
else:  
    checked = False # 체크박스 불필요
    
clicked = st.button('PDF 문서 요약')

if (uploaded_file is not None) and clicked:
    st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.") 
    reader = PdfReader(uploaded_file) # PDF 문서를 읽기
    
    text_summaries = []
    
    if radio_selected_lang == '한국어':
        lang = 'ko'
    elif radio_selected_lang == '영어':
        lang = 'en'
    else:
        lang = 'en'
        
    for page in reader.pages:
        page_text = page.extract_text() # 페이지의 텍스트 추출
        text_summary = summarize_text(page_text, lang)
        text_summaries.append(text_summary)
  
    # 페이지별 요약 리스트를 연결해 하나의 요약 문자열로 통합
    joined_summary = " ".join(text_summaries) 

    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_num = len(enc.encode(joined_summary)) # 텍스트 문자열의 토큰 개수 구하기

    max_token = 4096 # # gpt-3.5-turbo의 최대 요청 토큰(4096)
    esti_max_token = max_token - 96 # messages content에 사용한 텍스트를 고려해 설정
    
    if token_num < esti_max_token: # 설정한 토큰 보다 작을 때만 실행 가능
        # 하나로 통합한 요약문을 다시 요약 
        text_summary2 = summarize_text(joined_summary, lang)
        shorten_text_summary2 = textwrap.shorten(text_summary2, 250 ,placeholder=' [..이하 생략..]')
        
        st.write("- 최종 요약:", shorten_text_summary2) # 최종 요약문 출력 (축약)
        #st.write("- 최종 요약:", text_summary2) # 최종 요약문 출력

        if checked:
            trans_result = traslate_english_to_korean_using_openAI(text_summary2)
            shorten_trans_result = textwrap.shorten(trans_result, 200 ,placeholder=' [..이하 생략..]')
            st.write("- 한국어 요약:", shorten_trans_result) # 한글 번역문 출력 (축약)
            #st.write("- 한국어 요약:", trans_result) # 한글 번역문 출력
    else:
        st.write("- 통합한 요약문의 토큰 수가 커서 요약할 수 없습니다.")
