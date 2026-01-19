import requests
from bs4 import BeautifulSoup
import time
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform

# 1. 공통 헤더
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}


# --- 크롤링 함수 (기존과 동일) ---
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
    # 디시인사이드 실시간 베스트
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


# --- 워드클라우드 생성 함수 (화면에 띄우지 않고 객체만 반환) ---
def generate_wordcloud_obj(data_list):
    okt = Okt()
    noun_list = []

    # 불용어 설정 (뉴스용, 커뮤니티용 섞어서 처리)
    stop_words = {'속보', '충격', '오늘', '실시간', '근황', '이', '그', '저', '것', '수', '등', '들', '제', '명', '회', '개', '왜', '좀', '임',
                  '함'}

    for item in data_list:
        nouns = okt.nouns(item['title'])
        for noun in nouns:
            if len(noun) > 1 and noun not in stop_words:
                noun_list.append(noun)

    count = Counter(noun_list)
    tags = count.most_common(50)

    if not tags:
        return None

    # 폰트 설정
    if platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/malgun.ttf'
    elif platform.system() == 'Darwin':
        font_path = '/System/Library/Fonts/AppleGothic.ttf'
    else:
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=400,
        height=400,
        max_words=50
    )
    wc.generate_from_frequencies(dict(tags))
    return wc


# --- 메인 실행부 ---
if __name__ == "__main__":
    print("--- 🚀 데이터 수집 시작 ---")

    # 1. 데이터 각각 수집
    print("1. 네이버 뉴스 수집 중...")
    news_data = get_naver_news_headlines()

    print("2. 디시인사이드 수집 중... (잠시 대기)")
    time.sleep(1)
    community_data = get_community_best()

    print(f"✅ 수집 완료: 뉴스 {len(news_data)}개, 커뮤니티 {len(community_data)}개")

    # 2. 워드클라우드 객체 생성
    print("⏳ 워드클라우드 생성 중...")
    wc_news = generate_wordcloud_obj(news_data)
    wc_community = generate_wordcloud_obj(community_data)

    # 3. 화면 분할 출력 (Matplotlib Subplots)
    # 1행 2열짜리 차트를 만듭니다.
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 왼쪽: 네이버 뉴스
    if wc_news:
        axes[0].imshow(wc_news, interpolation='bilinear')
        axes[0].set_title("Naver News (Breaking)", fontsize=20)
    else:
        axes[0].text(0.5, 0.5, 'No Data', ha='center')
    axes[0].axis('off')

    # 오른쪽: 커뮤니티
    if wc_community:
        axes[1].imshow(wc_community, interpolation='bilinear')
        axes[1].set_title("DC Inside (Best)", fontsize=20)
    else:
        axes[1].text(0.5, 0.5, 'No Data', ha='center')
    axes[1].axis('off')

    print("✨ 결과 출력 완료!")
    plt.tight_layout()
    plt.show()