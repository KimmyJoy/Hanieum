import urllib.request
import json
import streamlit as st

#환경 변수에서 인증 정보 가져오기
client_id = st.secrets["NAVER_CLIENT_ID"]
client_secret = st.secrets["NAVER_CLIENT_SECRET"]
const_url = "https://openapi.naver.com/v1/search/movie.json?query=" # JSON 결과
const_start = 1
const_display = 100


# 네이버 영화를 검색하여, json형태로 검색 결과 return
# input : 검색어(String)
# output :
def searchNaverMovie(keyword, start=const_start, display=const_display):
    # query string 생성
    encText = urllib.parse.quote(keyword)
    reqUrl = const_url + f"{encText}&start={start}&display={display}"

    # Request 객체 생성
    request = urllib.request.Request(reqUrl)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    # Request 객체의 urlopen을 실행하여 Response 받기
    result_json = None

    # 네이버 서버로 요청 보내기
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

     # 요청 처리 결과 확인
    if(rescode == 200): # 성공
        response_body = response.read()
        result_json = json.loads(response_body.decode('utf-8')) # 응답 본문을 JSON 형태로 변환
        return result_json
    else: # 실패
        print(f"Error Code: {rescode}")
        return None