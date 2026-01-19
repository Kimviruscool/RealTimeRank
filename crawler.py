import requests
from bs4 import BeautifulSoup
import time
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform

# 1. 공통 헤더 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}


# --- (기존 작성하신 크롤링 함수들) ---
def get_naver_news_headlines():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001"
    data_list = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.type06_headline li dl') + soup.select('.type06 li dl')
        for article in articles:
            link_tag = article.select_one('dt:not(.photo) a') or article.select_one('dt.photo a')
            if link_tag:
                title = link_tag.text.strip()
                if title:
                    data_list.append({'source': 'Naver News', 'title': title})
    except Exception as e:
        print(f"❌ 네이버 뉴스 에러: {e}")
    return data_list


def get_community_best():
    url = "https://gall.dcinside.com/board/lists/?id=dcbest&list_num=100&sort_type=N&search_head=1&page=1"
    data_list = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.select('.gall_list .ub-content')
        for post in posts:
            title_tag = post.select_one('.gall_tit a')
            if title_tag:
                title = title_tag.text.strip()
                if title:
                    data_list.append({'source': 'Community', 'title': title})
    except Exception as e:
        print(f"❌ 커뮤니티 에러: {e}")
    return data_list


# --- 2. 분석 및 시각화 함수 (새로 추가됨) ---
def analyze_and_visualize(data_list):
    print("\n⏳ 형태소 분석 및 워드클라우드 생성 중...")

    okt = Okt()
    noun_list = []

    # 2-1. 불용어 리스트 (분석 결과 보면서 계속 추가해야 함)
    stop_words = {'속보', '충격', '오늘', '실시간', '근황', '이', '그', '저', '것', '수', '등', '들', '제', '명', '회', '개'}

    for item in data_list:
        title = item['title']
        # 명사 추출
        nouns = okt.nouns(title)

        for noun in nouns:
            # 한 글자 제외 및 불용어 제외
            if len(noun) > 1 and noun not in stop_words:
                noun_list.append(noun)

    # 빈도수 계산
    count = Counter(noun_list)
    tags = count.most_common(50)  # 상위 50개만

    if not tags:
        print("❌ 추출된 명사가 없습니다.")
        return

    print("🔥 상위 키워드 TOP 10:", tags[:10])

    # 2-2. 한글 폰트 설정 (OS에 따라 경로가 다름)
    if platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/malgun.ttf'  # 윈도우 맑은고딕
    elif platform.system() == 'Darwin':
        font_path = '/System/Library/Fonts/AppleGothic.ttf'  # 맥 애플고딕
    else:
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # 리눅스(나눔고딕)

    # 2-3. 워드클라우드 생성
    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800,
        height=600,
        max_words=50
    )

    # 빈도수 기반으로 생성
    wc.generate_from_frequencies(dict(tags))

    # 2-4. 이미지 출력
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')  # X, Y축 눈금 제거
    plt.show()


# --- 메인 실행부 ---
if __name__ == "__main__":
    print("--- 🚀 데이터 수집 시작 ---")

    news_data = get_naver_news_headlines()
    time.sleep(1)  # 차단 방지 딜레이
    community_data = get_community_best()

    all_data = news_data + community_data

    print(f"✅ 총 {len(all_data)}개의 제목 수집 완료.")

    # 분석 및 시각화 실행
    analyze_and_visualize(all_data)