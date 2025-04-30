import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pymysql

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

# 爬虫主逻辑
def scrape_and_store():
    base_url = "https://takaratomymall.jp"
    url = "https://takaratomymall.jp/shop/goods/search.aspx?search=x&keyword=conan&wovn=english"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    product_list = soup.find_all("li")

    conn = connect_to_db()
    cursor = conn.cursor()

    for item in product_list:
        link_tag = item.find("a", class_="tt_product2-6")
        if not link_tag:
            continue

        try:
            img_tag = item.find("p", class_="tt_product2-6__image").find("img")
            img_src = img_tag.get("data-src")
            img_url = urljoin(base_url, img_src)

            name_tag = item.find("div", class_="tt_product2-6__name")
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            price_tag = item.find("span", class_="tt_product2-6__priceText1")
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            release_info = item.find_all("p", class_="tt_product2-6__target")
            release_date = "N/A"
            for p in release_info:
                if "Release date:" in p.text:
                    release_date = p.get_text(strip=True).replace("Release date: ", "")

            # 插入数据库
            insert_product(cursor, name, img_url, price, release_date)
            print(f"Inserted: {name}")
        except Exception as e:
            print("Error parsing/inserting item:", e)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    scrape_and_store()
