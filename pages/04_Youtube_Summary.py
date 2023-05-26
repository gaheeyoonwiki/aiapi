# 유튜브 동영상을 요약하고 번역하는 웹 앱

import my_yt_tran # 유튜브 동영상 정보와 자막을 가져오기 위한 모듈 임포트
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import streamlit as st
import openai
import os
import tiktoken
import requests
from bs4 import BeautifulSoup
import textwrap
import deepl

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

def traslate_english_to_korean_using_deepL(text):   
    # auth_key = os.environ["DEEPL_AUTH_KEY"] # Deepl 인증 키
    auth_key = st.secrets["DEEPL_AUTH_KEY"]
    
    translator = deepl.Translator(auth_key) # translator 객체를 생성

    result = translator.translate_text(text, target_lang="KO") # 번역 결과 객체를 result 변수에 할당
    
    return result.text

# 사이드바 화면
def clear_text_input():
     st.session_state['input'] = ""
    
st.sidebar.title("요약 설정 ")
input_text = st.sidebar.text_input("유튜브 동영상 URL을 입력하세요.", key="input")

clicked_for_clear = st.sidebar.button('URL 입력 내용 지우기',  on_click=clear_text_input)

radio_selected_lang = st.sidebar.radio('유튜브 동영상 언어 선택', ['한국어', '영어'], index=1, horizontal=True)
    
if radio_selected_lang == '영어': 
    radio_selected_tran = st.sidebar.radio('번역 방법 선택', ['OpenAI'], index=0, horizontal=True)

clicked = st.sidebar.button('동영상 내용 요약')

# 메인(Main) 화면
st.title("유튜브 동영상 요약")

# 텍스트 입력이 있으면 수행
if input_text and clicked: 
    
    video_url = input_text.strip()
    
    if radio_selected_lang == '한국어':
        lang = 'ko'
    elif radio_selected_lang == '영어':
        lang = 'en'
    else:
        lang = 'en'    
    
    # 유튜브 동영상 플레이
    st.video(video_url, format='video/mp4') # st.video(video_url) 도 동일

    # 유튜브 동영상 제목 가져오기
    yt_title = my_yt_tran.get_youtube_title(video_url)
    st.write("[제목]", yt_title) # 유튜브 동영상 제목 출력
    
    # 유트브 동영상 자막 가져오기
    yt_transcript = my_yt_tran.get_transcript_from_youtube(video_url, lang)

    # 자막 텍스트의 토큰 수 계산
    enc = tiktoken.get_encoding("cl100k_base")
    # enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

    encoded_list = enc.encode(yt_transcript) # 텍스트 인코딩해 인코딩 리스트 생성
    token_num= len(encoded_list)   # 토큰 개수

    max_token = 4000 # gpt-3.5-turbo 모델을 이용할 경우로 가정해 지정

    divide_num = int(token_num/max_token) + 1 # 정수로 만들기 위해 int() 1을 더함
    divide_char_num = int(len(yt_transcript) / divide_num) # 대략적인 나눌 문자 개수 
    divide_width = divide_char_num + 20 # wrap() 함수로 텍스트 나눌 때 여유분 고려해 20 더함

    divided_yt_transcripts = textwrap.wrap(yt_transcript, width=divide_width) 
    
    summaries = []
    for divided_yt_transcript in divided_yt_transcripts:
        summary = summarize_text(divided_yt_transcript, lang) # 첫 페이지 요약
        summaries.append(summary)
    
    yt_summary = " ".join(summaries)
    shorten_yt_summary = textwrap.shorten(yt_summary, 250 ,placeholder=' [..이하 생략..]')
    
    st.write("유튜브 동영상 내용 요약 중입니다. 잠시만 기다려 주세요.") 
    
    st.write("- 자막 요약(축약):", shorten_yt_summary) # 최종 요약문 출력 (축약)
    # st.write("- 자막 요약:", yt_summary) # 최종 요약문 출력

    if radio_selected_lang == '영어': 
        if radio_selected_tran == 'OpenAI':
            trans_result = traslate_english_to_korean_using_openAI(yt_summary)
        elif radio_selected_tran == 'DeepL':
            trans_result = traslate_english_to_korean_using_deepL(yt_summary)

        shorten_trans_result = textwrap.shorten(trans_result, 150 ,placeholder=' [..이하 생략..]')
        st.write("- 자막 요약(축약):", shorten_trans_result) # 한글 번역문 출력 (축약)
        #st.write("- 한국어 요약:", translated_result) # 한글 번역문 출력
