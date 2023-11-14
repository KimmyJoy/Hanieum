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
def searchNaverMovie(keyword, display=const_display, start=const_start):
    # query string 생성
    encText = urllib.parse.quote(keyword)
    reqUrl = const_url + f"{encText}&display={display}&start={start}"

    # Request 객체 생성
    request = urllib.request.Request(reqUrl)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

   # Request 객체의 urlopen을 실행하여 Response 받기
    result_json = None
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        # Response 객체에서 검색 결과 얻어서 json으로 변환하기
        if (rescode == 200):
            response_body = response.read()
            response_body_dec = response_body.decode('utf-8')
            result_json = json.loads(response_body_dec)
    except Exception as e:
        print(e)
        print(f"Error :{reqUrl}")

    # 검색이 진행되는 상황 logging 하기
    if (result_json != None):
        print(f"{keyword} [{start}] : Search Request Succes")
    else:
        print(f"{keyword} [{start}] : Error~~~~~~~")

    # JSON 형태의 검색 결과 return하기
    return result_json