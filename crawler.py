import requests
from bs4 import BeautifulSoup
import time

# 1. 공통 헤더 설정 (브라우저인 척 속이기 위함)
# 봇 차단을 막기 위해 User-Agent를 설정하는 것이 필수입니다.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}


def get_naver_news_headlines():
    """
    네이버 뉴스 '속보(Breaking News)' 섹션의 헤드라인을 가져옵니다.
    """
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001"  # 속보 페이지
    data_list = []

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 리스트 영역 선택 (HTML 구조 분석 결과)
        # headline 기사와 일반 기사가 섞여 있어서 두 그룹을 모두 찾습니다.
        articles = soup.select('.type06_headline li dl') + soup.select('.type06 li dl')

        print(f"✅ 네이버 뉴스 수집 중... ({len(articles)}개 발견)")

        for article in articles:
            # a 태그 찾기 (제목과 링크가 들어있음)
            link_tag = article.select_one('dt:not(.photo) a')  # 사진 없는 dt 태그 우선
            if link_tag is None:
                link_tag = article.select_one('dt.photo a')  # 없으면 사진 있는 태그

            if link_tag:
                title = link_tag.text.strip()
                link = link_tag['href']

                # 내용이 비어있지 않은 경우만 추가
                if title:
                    data_list.append({'source': 'Naver News', 'title': title, 'link': link})

    except Exception as e:
        print(f"❌ 네이버 뉴스 크롤링 에러: {e}")

    return data_list


def get_community_best():
    """
    디시인사이드 '실시간 베스트' 게시판 제목을 가져옵니다.
    (커뮤니티는 HTML 구조가 자주 바뀌므로 주의 필요)
    """
    url = "https://gall.dcinside.com/board/lists/?id=dcbest&list_num=100&sort_type=N&search_head=1&page=1"
    data_list = []

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 게시글 리스트 선택 (tr 태그 중 class가 ub-content 인 것)
        posts = soup.select('.gall_list .ub-content')

        print(f"✅ 커뮤니티 수집 중... ({len(posts)}개 발견)")

        for post in posts:
            title_tag = post.select_one('.gall_tit a')
            if title_tag:
                title = title_tag.text.strip()
                link = "https://gall.dcinside.com/board/lists/?id=dcbest&list_num=100&sort_type=N&search_head=1&page=1" + title_tag['href']

                if title:
                    data_list.append({'source': 'Community', 'title': title, 'link': link})

    except Exception as e:
        print(f"❌ 커뮤니티 크롤링 에러: {e}")

    return data_list


# --- 메인 실행부 ---
if __name__ == "__main__":
    print("--- 🚀 데이터 수집 시작 ---")

    # 1. 뉴스 수집
    news_data = get_naver_news_headlines()

    # 2. 커뮤니티 수집
    # (서버 부하를 줄이기 위해 잠시 대기)
    time.sleep(1)
    community_data = get_community_best()

    # 3. 결과 합치기
    all_data = news_data + community_data

    print("\n--- 📊 수집 결과 (상위 10개만 출력) ---")
    for idx, item in enumerate(all_data[:10], 1):
        print(f"[{idx}] [{item['source']}] {item['title']}")

    print(f"\n총 {len(all_data)}개의 데이터를 수집했습니다.")