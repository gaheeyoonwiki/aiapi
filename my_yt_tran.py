# 유튜브 동영상 정보와 자막을 가져오기 위한 모듈

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from bs4 import BeautifulSoup

# 유튜브 동영상 제목 가져오는 함수
def get_youtube_title(video_url):
    r = requests.get(video_url)
    soup = BeautifulSoup(r.text, "lxml")
    title = soup.title.get_text()
    title = title.split("- YouTube")[0].strip()
    
    return title

# 비디오 URL에서 비디오 ID 추출하는 함수
def get_video_id(video_url):
    video_id = video_url.split('v=')[1][:11]
    
    return video_id 

# 유튜브 동영상 자막 가져오는 함수
def get_transcript_from_youtube(video_url, lang='en'):
    # 비디오 URL에서 비디오 ID 추출
    video_id = get_video_id(video_url)

    # 자막 리스트 가져오기
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
#     print(f"- 유튜브 비디오 ID: {video_id}")
#     for transcript in transcript_list:
#         print(f"- [자막 언어] {transcript.language}, [자막 언어 코드] {transcript.language_code}")

    # 자막 가져오기 (lang)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])

    text_formatter = TextFormatter() # Text 형식으로 출력 지정
    text_formatted = text_formatter.format_transcript(transcript)
    
    return text_formatted
