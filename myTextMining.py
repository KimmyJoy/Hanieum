import urllib.request
import json
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import re
import pandas as pd
import joblib
from konlpy.tag import Okt
import streamlit as st


# 상수 데이터 설정
const_FTmodel_name = 'tfidf_model.pkl'
const_SAModel_name = 'SA_LogR_model.pkl'
const_wordFreqRange = 80

#환경 변수에서 인증 정보 가져오기
client_id = st.secrets["NAVER_CLIENT_ID"]
client_secret = st.secrets["NAVER_CLIENT_SECRET"]
const_url = "https://openapi.naver.com/v1/search/blog.json?query=" # JSON 결과
const_start = 1
const_display = 100


#######################################################
# 네이버 뉴스를 검색하여, json형태로 검색 결과 return
# input : 검색어(String)
# output :
def searchNaverNews(keyword, start, display):
    # query string 생성
    encText = urllib.parse.quote(keyword)
    reqUrl = const_url + f"{encText}&start={start}&display={display}"

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


#############################################################
# 파이썬 객체에서 검색 결과를 정리해서 리스트에 추가하기
def setNewSearchResult(result_all_list, current_result):
    cur_index = 1
    if result_all_list != []:
        cur_index = result_all_list[-1]['index'] + 1
    for result in current_result['items']:
        result['index'] = cur_index
        result_all_list.append(result)
        cur_index += 1


#################################################
# Naver News Crawling 하여 list에 저장하기
def searchSetNaverNews(keyword):
    # 필요변수 초기화
    result_all = []  # 검색 결과 저장 변수
    start = const_start
    display = const_display

    # 네이버 뉴스를 검색하여 리스트로 저장
    result_json = searchNaverNews(keyword, start, display)  # 최초의 검색 실행
    # 응답데이터가 없을 때까지 반복
    while result_json != None:
        # 응답데이터를 리스트에 저장
        setNewSearchResult(result_all, result_json)
        # start 값 증가 (검색 결과 수만큼)
        start += result_json['display']
        # 네이버 뉴스 검색
        result_json = searchNaverNews(keyword, start, display)

    return result_all


#############################################################
# 리스트에 저장된 검색 결과를 json 파일로 저장하기
def saveSearchResult(filename, list_result_all):
    with open(filename, "w", encoding="utf8") as outfile:
        json_string = json.dumps(list_result_all, ensure_ascii=False, indent=4)
        outfile.write(json_string)
    print(f"{filename} Saved!!!!")


#################################################
# 상위 n개의 명사만 추출
def getHighFreqNouns(keyword, result_list, number, field):
# 본문만 추출하여 정제
    total_result = ''
    for item in result_list:
        clean_data = re.sub(r'[\W]', ' ', item['description'])
        total_result += clean_data
# 명사 추출
    okt = Okt()
    total_result_noun = okt.nouns(total_result)
# 빈도수 상위 number개 추출
    count = Counter(total_result_noun)
    most_freq_words = dict()
    for word, counts in count.most_common(number):
        if (word != keyword) and (len(word) > 1):
            most_freq_words[word] = counts
    return most_freq_words

#################################################
# wordcloud로 시각화
def setWordCloud(result_freq):
    font_path = "./customFonts/MALGUN.TTF"
    wordcloud = WordCloud(font_path, background_color="ivory", width=800, height=600)
    wordcloud_freq = wordcloud.generate_from_frequencies(result_freq)

    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.imshow(wordcloud_freq)
    plt.axis('off')
    plt.show()

##################################################
# input: 명사 추출시 제외할 키워드
def getMostFreqNouns(input_list, number, keyword):
    # 명사 추출
    okt = Okt()
    total_result_noun = okt.nouns(" ".join(input_list))

    # 상위 n개의 명사만 추출
    count = Counter(total_result_noun)
    result_freq = dict()
    for word, counts in count.most_common(number):
        if (word != keyword) and (len(word) > 1):
            result_freq[word] = counts

    return result_freq

#################################################
# 검색 결과에서 본문만 WordCloud 생성하기
# input : 검색어(String), 텍스트의 리스트(List)

def visualizeWordCloud_Korean(keyword, result_list, field=""):
    # 본문만 추출하여 정제
    '''
    total_result = ''
    for item in result_list:
        clean_data = re.sub(r'[\W]', ' ', item[field])
        total_result += clean_data
    '''
    if field:
        result_list = [item[field] for item in result_list]

    total_result = cleanInputData(result_list)
    result_freq = getMostFreqNouns(total_result, const_wordFreqRange, keyword)
    visualizeWordCloud(result_freq)


def visualizeWordCloud(result_freq):
    # wordcloud로 시각화
    font_path = "C:\Windows\Fonts\malgun.ttf"
    wordcloud = WordCloud(font_path, background_color="ivory", width=800, height=600)
    wordcloud_freq = wordcloud.generate_from_frequencies(result_freq)

    fig = plt.figure()
    plt.imshow(wordcloud_freq)
    plt.axis('off')
    plt.show()
    st.pyplot(fig)


######################################################################################


def okt_tokenizer(text):
    okt = Okt()
    tokens = okt.morphs(text)
    return tokens

def main_old():
    tfidf_model = joblib.load('tfidf_model.pkl')
    SA_LogR_model = joblib.load('SA_LogR_model.pkl')

    # Crawling 데이터 로딩하기
    filename = "블루베리_news.json"
    temp_df = pd.read_json(filename)
    news_df = temp_df.loc[:,['description']]

    # 입력 문장 전처리
    sub_func = lambda x: re.sub(r'[^ㄱ-ㅣ가-힣\s]+', ' ', x)
    news_df.loc[:, 'description'] = news_df.loc[:, 'description'].apply(sub_func)

    # Feature Vector 생성
    news_desc_tfidf = tfidf_model.transform(news_df.loc[:, 'description'])

    # 감성 분석 모델 적용 -> 감성 분석
    news_desc_predict = SA_LogR_model.predict(news_desc_tfidf)

    # 예측값 출력
    news_df.loc[:, 'description_SA'] = news_desc_predict
    # 해당 키워드에 대한 긍정 뉴스와 부정 뉴스의 비율 출력하기
    # rate_good_title = round((news_df['title_SA'].value_counts()[0] / len(news_df['title_SA'])) * 100, 2)
    # rate_bad_title = round((news_df['title_SA'].value_counts()[1] / len(news_df['title_SA'])) * 100, 2)

    # print(f'[제목]긍정적 : {rate_good_title}%')
    # print(f'[제목]부정적 : {rate_bad_title}%')

    rate_good_desc = round((news_df['description_SA'].value_counts()[0] / len(news_df['description_SA'])) * 100, 2)
    rate_bad_desc = round((news_df['description_SA'].value_counts()[0] / len(news_df['description_SA'])) * 100, 2)

    print(f'[내용]긍정적 : {rate_good_desc}% 얘맞아?')
    print(f'[내용]부정적 : {rate_bad_desc}%')

    return


############################################
# input : 한글+문자+숫자... 원본 리스트
# output : 한글만 남긴 리스트
def cleanInputData(target_list):
    # 입력 문장 전처리
    sub_func = lambda x: re.sub(r'[^ㄱ-ㅣ가-힣\s]+', ' ', x)
    clean_list = list(map(sub_func, target_list))
    # print(clean_list)
    return clean_list


####################################################
# input : 입력 데이터, Feature 추출 model의 파일명
def getFeatureVector(input_list, filename):
    # 모델 loading
    tfidf_model = joblib.load(filename)
    # Feature vector 생성
    feature_vector = tfidf_model.transform(input_list)
    return feature_vector



#############################################
# input : 특징벡터(List), 감성인식 예측모델 파일이름(String)
# output : 분석결과(List)
def predictSentiment(feature_vector, filename):
    SA_LogR_model = joblib.load(filename)

    #감성 분석 모델 적용 -> 감성 분석 예측값 출력
    predict_result = SA_LogR_model.predict(feature_vector)
    return predict_result

############################################
# input : 분석 대상 텍스트 리스트
# output : 감성 분석 결과
def sentimentAnalysis_ko(target_list):
    clean_list = cleanInputData(target_list)
    feature_vector = getFeatureVector(clean_list, const_FTmodel_name)
    predict_result = predictSentiment(feature_vector, const_SAModel_name)
    return predict_result

#############################################
#input : file, 데이터를 추출할 컬럼명
#ouput : list
def loadSavedData_JSON(filename, filed):
    # Crawling 데이터 로딩하기
    # filename = "블루베리_news.json"
    data = pd.read_json(filename)
    # return data.loc[:,['description']]
    return list(data[filed])

##########################################################
# input : 예측 결과(List)
# output : 긍/부정 결과 출력
def visualizeSA_Text(predict_result):
    num_total = len(predict_result)
    num_good = sum(predict_result) # good은 다 1이니까.
    num_bad = num_total - num_good # 1빼면 다 0이니까.

    rate_good_desc = round(num_good / num_total * 100, 2)
    rate_bad_desc = round(num_bad / num_total * 100, 2)
    print(f'전체 : {num_total}건 중,')
    print(f'    [내용]긍정적 : {rate_good_desc}% ({num_good}건)')
    print(f'    [내용]부정적 : {rate_bad_desc}% ({num_bad}건)')
    return [num_good, num_bad]

def visualizeSA_WordCloud(keyword, data_list, predict_list):
    # 긍정/부정 기사 따로 분류하여 리스트 생성
    positive_list = []
    negative_list = []
    for i in range(len(data_list)):
        if predict_list[i]:
            positive_list.append(data_list[i])
        else:
            negative_list.append(data_list[i])
    # visualizeWordCloud_Korean(keyword, positive_list)
    # visualizeWordCloud_Korean(keyword, negative_list)

    return [positive_list, negative_list]


def getTargetStringList(input_json_list, field):
    return [item[field] for item in input_json_list]

