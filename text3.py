import requests
from bs4 import BeautifulSoup
import pymysql
import time

# 数据库连接函数
def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='spider_db',
        charset='utf8mb4'
    )

# 插入数据到数据库
def insert_product(cursor, name, img_url, price, release_date):
    sql = """
        INSERT INTO products (name, img_url, price, release_date)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (name, img_url, price, release_date))

# 从详情页获取价格
def get_price_from_detail_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        # 尝试提取价格（你可以根据实际结构调整下面这行）
        price_tag = soup.find("span", class_="woocommerce-Price-amount")
        if price_tag:
            return price_tag.get_text(strip=True)
    except Exception as e:
        print("Error fetching price:", e)
    return "N/A"

# 爬取主函数
def scrape_and_store():
    url = "https://j-hobby.net/?catego=&nentuki=&s=conan&sr=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.find_all("article", class_="post")

    conn = connect_to_db()
    cursor = conn.cursor()

    for article in articles:
        try:
            # 图片链接
            img_tag = article.find("div", class_="waku-img-top").find("img")
            img_url = img_tag["src"] if img_tag else "N/A"

            # 商品名称
            title_tag = article.find("h1", class_="entry-title").find("a")
            name = title_tag.text.strip() if title_tag else "N/A"

            # 商品详情页链接
            detail_url = title_tag["href"] if title_tag else None

            # 发布时间 / Release date
            time_tag = article.find("time", class_="entry-date")
            release_date = time_tag.text.strip() if time_tag else "N/A"

            # 获取价格（从详情页）
            price = get_price_from_detail_page(detail_url) if detail_url else "N/A"

            # 插入数据库
            insert_product(cursor, name, img_url, price, release_date)
            print(f"Inserted: {name}")

            time.sleep(1)  # 暂停1秒，避免过快请求
        except Exception as e:
            print("Error processing item:", e)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    scrape_and_store()
