import urllib.request
import json

def searchTmdbMovie(keyword, api_key):
    # TMDb 영화 검색 API URL
    url = "https://api.themoviedb.org/3/search/movie"

    # 요청 파라미터
    params = {
        "api_key": api_key,
        "query": keyword,
        "language": "ko-KR"  # 언어 설정
    }

    # URL에 요청 파라미터 추가
    url += "?" + urllib.parse.urlencode(params)

    # API 요청
    with urllib.request.urlopen(url) as response:
        # 응답 확인
        if response.getcode() == 200:
            # JSON 파싱
            data = json.loads(response.read())
            # 검색 결과 반환
            return data["results"]
        else:
            print("Error:", response.getcode())
            return None