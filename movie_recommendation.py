import numpy as np 
import pandas as pd
import json

# 영화 정보 데이터 가져오기
meta = pd.read_csv('the-movies-dataset/movies_metadata.csv')
# 영화 정보의 특정 컬럼만 가져오기
meta = meta[['id', 'original_title', 'original_language', 'genres', 'vote_average']]
# id 컬럼명 변경
meta = meta.rename(columns={'id':'movieId'})
# 언어가 en, ko인 것만 가져오기
meta[(meta['original_language'] == 'en') | (meta['original_language'] == 'ko')]

# 영화 평점데이터 가져오기
ratings = pd.read_csv('the-movies-dataset/ratings_small.csv')
# 영화 특정컬럼 가져오기
ratings = ratings[['userId', 'movieId', 'rating']]

# 영화데이터와 평점의 id 숫자형으로 변환
meta.movieId = pd.to_numeric(meta.movieId, errors='coerce')
ratings.movieId = pd.to_numeric(ratings.movieId, errors='coerce')

# 장르의 표시 변환
def parse_genres(genres_str):
    genres = json.loads(genres_str.replace('\'', '"'))
    
    genres_list = []
    for g in genres:
        genres_list.append(g['name'])

    return genres_list

meta['genres'] = meta['genres'].apply(parse_genres)

# 두데이터 조인
data = pd.merge(ratings, meta, on='movieId', how='inner')

# 피버테이블 만들기
matrix = data.pivot_table(index='userId', columns='original_title', values='rating')

# 계산
GENRE_WEIGHT = 0.1

def pearsonR(s1, s2):
    s1_c = s1 - s1.mean()
    s2_c = s2 - s2.mean()
    return np.sum(s1_c * s2_c) / np.sqrt(np.sum(s1_c ** 2) * np.sum(s2_c ** 2))

def recommend(input_movie, matrix, n, similar_genre=True):
    input_genres = meta[meta['original_title'] == input_movie]['genres'].iloc(0)[0]

    result = []
    for title in matrix.columns:
        if title == input_movie:
            continue

        # rating comparison
        cor = pearsonR(matrix[input_movie], matrix[title])
        
        # genre comparison
        if similar_genre and len(input_genres) > 0:
            temp_genres = meta[meta['original_title'] == title]['genres'].iloc(0)[0]

            same_count = np.sum(np.isin(input_genres, temp_genres))
            cor += (GENRE_WEIGHT * same_count)
        
        if np.isnan(cor):
            continue
        else:
            avg = meta[meta['original_title'] == title]['vote_average'].values[0]

            result.append((title, '{:.2f}'.format(cor), temp_genres, avg))
            
    result.sort(key=lambda r: r[1], reverse=True)
    return result[:n]

def result(input_movie) :
    recommend_result = recommend(input_movie, matrix, 10, similar_genre=True)
    
    return pd.DataFrame(recommend_result, columns = ['Title', 'Correlation', 'Genre', 'Avg'])

# print(result('올드보이'))