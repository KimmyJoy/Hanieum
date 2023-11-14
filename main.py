import streamlit as st
import myTextMining as tm
from myTextMining import okt_tokenizer
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import movie_recommendation as mr
import movie_details as md
import pandas as pd

keyword = ''

with st.sidebar:
        keyword = st.text_input("검색어를 입력하세요 :").strip()
        choice = option_menu("Menu", ["영화추천", "긍부정 분석기", "영화 상세정보"],
                                icons=['kanban', 'bi bi-robot', 'bi bi-file-earmark-richtext'],
                                menu_icon="app-indicator", default_index=0,
                                styles={
                "container": {"padding": "4!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
                "nav-link-selected": {"background-color": "#08c7b4"},
                }
        )

if keyword == '' :
        st.write('좌측 검색란에 검색어를 입력해주세요.')
else :

        if choice == '영화 상세정보' :
                st.title('영화 상세정보')
                st.subheader(f'{keyword}의 상세정보입니다.')
                with st.spinner('Wait for it...'):
                        # TMDb 영화 검색 API 호출
                        results = md.searchTmdbMovie(keyword, st.secrets["api_key"])
                       # 검색 결과 출력
                        if results is not None and len(results) > 0:
                                for movie in results:
                                        #마크 다운으로 영화 정보 출력
                                        st.markdown(f"**제목:** {movie['title']}")
                                        st.markdown(f"**개봉 날짜:** {movie['release_date']}")
                                        st.markdown(f"**평점:** {movie['vote_average']}")
                                        st.markdown(f"**요약:** {movie['overview']}")

                                        # 영화 포스터 출력
                                        if movie["poster_path"] is not None:
                                           st.image("https://image.tmdb.org/t/p/w500" + movie["poster_path"], width=480)

                                        st.markdown("<hr/>", unsafe_allow_html=True)
                        else:
                             st.write("검색 결과가 없습니다.")
                             
        elif choice == '영화추천':
                st.title('영화추천페이지')
                st.subheader(f'{keyword}와(과) 연관도가 높은 영화 10개 입니다.')
                with st.spinner('Wait for it...'):
                        result_df = mr.result(keyword)
                        plt.rcParams['font.family'] = 'Malgun Gothic'
                        # label = '영화제목','평점'
                        fig, ax = plt.subplots(figsize=(4, 3))
                        plt.xlim(0, 10)
                        ax.barh(result_df['Title'], result_df['Avg'], color='red')
                        # ax.hist(mr.result(keyword)['Avg'], bins=10, color='skyblue')
                        st.pyplot(fig)
                        # st.table(result_df)
                        # 데이터 프레임 활용 시 내림차순 오름차순 변경 및 장르를 보기 쉽게 바꿔줌
                        st.dataframe(result_df)


        elif choice == '긍부정 분석기' :
                st.title('네이버 블로그 긍부정 분석기')
                ####################### main #####################
                # 검색어 입력받기
                # Naver News Crawling 하기
                with st.spinner('Wait for it...'):
                        result_all_list = tm.searchSetNaverNews('영화 ' + keyword)

                        target_list = tm.getTargetStringList(result_all_list, 'description')
                        predict_result = tm.sentimentAnalysis_ko(target_list)

                        plt.rcParams['font.family'] = 'Malgun Gothic'
                        labels = '긍정적', '부정적'
                        sizes = tm.visualizeSA_Text(predict_result)
                        fig1, ax1 = plt.subplots(figsize = (7,3))
                        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                        st.subheader(keyword +'의 긍부정 비율')
                        st.pyplot(fig1)

                        a_result = []
                        b_result = []

                        

                        for idx, val in enumerate(predict_result):
                                if len(a_result) < 3 and val == 1 :
                                        for result in result_all_list:
                                                if result.get('index') == idx +1:
                                                        a_result.append(result)
                                if len(b_result) < 3 and val == 0 :
                                        for result in result_all_list:
                                                if result.get('index') == idx +1:
                                                        b_result.append(result)
                                        
                        
                        c_result = tm.visualizeSA_WordCloud(keyword, target_list, predict_result)

                        tab1, tab2 = st.tabs(['긍정적인 게시글' , '부정적인 게시글'])
                        with tab1:
                                col1,col2 = st.columns([3,2])
                                with col1 :
                                        for result in a_result:
                                                modified_title = result.get('title').replace('<b>', '').replace('</b>', '')
                                                st.write(f'[{modified_title}]({result.get("link")})')
                                                st.write(result.get('postdate'))
                                                st.markdown("""---""")
                                with col2 :
                                        tm.visualizeWordCloud_Korean(keyword, c_result[0])
                        with tab2:
                                col3,col4 = st.columns([3,2])
                                with col3 :
                                        for result in b_result:
                                                modified_title = result.get('title').replace('<b>', '').replace('</b>', '')
                                                st.write(f'[{modified_title}]({result.get("link")})')
                                                st.write(result.get('postdate'))
                                                st.markdown("""---""")         
                                with col4 :
                                        tm.visualizeWordCloud_Korean(keyword, c_result[1])  


