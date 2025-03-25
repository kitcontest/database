from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector  # MySQL 연결을 위한 라이브러리
import time
from selenium.webdriver.common.keys import Keys

# 크롤링한 데이터를 데이터베이스에 저장하기 위해 MySQL 연결 설정
db_connection = mysql.connector.connect(
    host="127.0.0.1",  # MariaDB 서버 주소
    user="root",        # 사용자명
    password="1111",    # 비밀번호
    database="Team"     # 사용할 데이터베이스
)

cursor = db_connection.cursor()

# 캠퍼스픽 공모전 페이지 URL만 추가
contest_url = "https://www.campuspick.com/contest"

# 크롤링할 URL 리스트
url_list = [contest_url]

# 크롬창을 띄우는 코드
driver = webdriver.Chrome()

for url in url_list:
    # url 접속
    driver.get(url)
    # 로딩이 다 되기 위해서 3초 기다려주기
    time.sleep(3)

    # 자동 스크롤 제한 시간 (3분)
    start_time = time.time()

    # 페이지가 끝까지 로드될 때까지 스크롤을 반복적으로 내림
    last_height = driver.execute_script("return document.body.scrollHeight")

    # 크롤링할 게시물 개수 제한 (50개로 설정)
    max_posts = 50
    crawled_posts = 0

    while True:
        # 스크롤을 최하단으로 내림
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 페이지 로딩을 위해 잠시 대기
        time.sleep(2)

        # 새로운 페이지의 높이를 가져옴
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 더 이상 스크롤할 곳이 없다면 종료
        if new_height == last_height:
            break

        last_height = new_height

        # 크롤링한 데이터를 처리하는 부분
        lis = driver.find_elements(By.XPATH, '//*[@class="list"]/*[@class="item"]')

        for li in lis:
            if crawled_posts >= max_posts:
                print(f"{max_posts}개의 게시물을 크롤링하여 종료합니다.")
                break  # 게시물 개수 제한에 도달하면 크롤링 종료

            try:
                # 상세 페이지 URL을 추출 (href 속성에서 'id' 값 추출)
                detail_page_url = li.find_element(By.XPATH, './/a').get_attribute("href")
                # 상대 경로가 있을 경우 전체 URL로 변환
                if detail_page_url.startswith("/"):
                    detail_page_url = "https://www.campuspick.com" + detail_page_url

                # 마감기한을 가져와서 마감된 게시물인지 확인
                if li.find_elements(By.XPATH, './/*[@class="dday highlight"]'):
                    due_date = li.find_element(By.XPATH, './/*[@class="dday highlight"]').text
                    if "마감" in due_date:
                        print("마감된 게시물은 가져오지 않습니다")
                        continue  # 마감된 게시물은 건너뛰기
                else:
                    print("마감기한이 없습니다")

                # 키워드
                keywords = li.find_elements(By.XPATH, './/*[@class="badges"]/span')
                keyword_list = [keyword.text for keyword in keywords]
                keyword_str = ",".join(keyword_list)

                # 활동명
                title = li.find_element(By.XPATH, './/h2').text
                # 주최
                company = li.find_element(By.XPATH, './/*[@class="company"]').text
                # 조회수 (쉼표 제거 후 숫자로 변환)
                view_count = li.find_element(By.XPATH, './/*[@class="viewcount"]').text
                view_count = int(view_count.replace(",", ""))  # 쉼표 제거 후 숫자형으로 변환
                # 썸네일 이미지 URL
                thumbnail_url = li.find_element(By.XPATH, './/figure').get_attribute("data-image")

                # 상세 페이지에서 추가 정보 크롤링
                driver.get(detail_page_url)  # 상세 페이지로 이동
                time.sleep(3)  # 페이지가 로딩될 때까지 대기

                # 상세 페이지에서 공모전 설명 크롤링
                description = driver.find_element(By.XPATH, '//*[@class="description"]').text

                # 데이터베이스에 삽입 쿼리
                insert_query = """
                INSERT INTO Contests (keywords, title, company, due_date, view_count, thumbnail_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query, (keyword_str, title, company, due_date, view_count, thumbnail_url, description))

                db_connection.commit()  # 변경사항 커밋

                crawled_posts += 1

                # 페이지 이동 후 처음으로 돌아가기
                driver.back()  # 이전 페이지로 돌아감
                time.sleep(2)  # 이전 페이지가 로드될 때까지 대기

            except Exception as e:
                print(f"Error while extracting data: {e}")
                continue  # 오류가 나면 해당 항목은 건너뛰기

        if crawled_posts >= max_posts:
            break  # 최대 게시물 개수에 도달하면 종료

# 크롬 드라이버 종료
driver.quit()

# 데이터베이스 연결 종료
cursor.close()
db_connection.close()
