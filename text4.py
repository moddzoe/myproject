import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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

# 插入商品数据到数据库 
def insert_product(cursor, name, img_url, price, release_date):
    sql = """
        INSERT INTO products (name, img_url, price, release_date)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (name, img_url, price, release_date))

# 主爬虫函数 
def scrape_conanshop():
    base_url = "https://conanshop.online/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all("li", class_="prd_lst_unit")

    conn = connect_to_db()
    cursor = conn.cursor()

    for item in items:
        try:
            # 商品图片
            img_tag = item.find("img", class_="prd_lst_img")
            img_url = img_tag["src"] if img_tag else "N/A"

            # 商品名称
            name_tag = item.find("span", class_="prd_lst_name").find("a")
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # 商品价格
            price_tag = item.find("span", class_="prd_lst_price")
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Release date 暂无，填 N/A
            release_date = "N/A"

            # 写入数据库
            insert_product(cursor, name, img_url, price, release_date)
            print(f"Inserted: {name}")

            time.sleep(1)  # 降低请求频率
        except Exception as e:
            print("Error processing item:", e)

    conn.commit()
    cursor.close()
    conn.close()
    print("All items saved.")

if __name__ == "__main__":
    scrape_conanshop()
