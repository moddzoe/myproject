
import re
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pymysql

# MySQL数据库连接函数
def connect_to_db():
    return pymysql.connect(
        host='localhost',  # 数据库主机地址
        user='root',       # 用户名
        password='',  # 密码
        database='spider_db', # 数据库名
        charset='utf8mb4'   # 字符集
    )

# 创建数据库表
def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price VARCHAR(100),
            release_date VARCHAR(100),
            image_url TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# 插入产品数据
def insert_product(name, price, release_date, image_url):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # 先删除 30 天前的旧数据
        delete_old_products(cursor)

        sql = '''
        INSERT INTO products (name, price, release_date, image_url)
        VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (name, price, release_date, image_url))
        conn.commit()
        print(" 数据插入成功")
    except pymysql.MySQLError as e:
        print(f" 数据插入失败: {e}")
    finally:
        cursor.close()
        conn.close()


def delete_old_products(cursor):
    try:
        sql = "DELETE FROM products WHERE created_at < NOW() - INTERVAL 30 DAY"
        cursor.execute(sql)
        print(f"已删除 30 天前的数据")
    except pymysql.MySQLError as e:
        print(f"删除旧数据失败: {e}")


# 价格格式化函数
def format_price(price_str):
    match = re.search(r'(\d[\d,]*)', price_str)
    return match.group(1).replace(',', '') if match else "N/A"

# 发售日期格式化函数
def format_release_date(date_str):
    match = re.search(r'(\d{4})年(\d{2})月', date_str)
    return f"{match.group(1)}-{match.group(2)}" if match else "N/A"

# 解析产品详情
def parse_product(product_url):
    print(f"\n正在获取产品详情：{product_url}")
    
    try:
        req_detail = Request(product_url, headers={'User-Agent': 'Mozilla/5.0'})
        product_html = urlopen(req_detail).read()
        product_soup = BeautifulSoup(product_html, 'html.parser')

        # 提取产品图片
        product_img = "N/A"
        product_img_tag = product_soup.find("div", class_="item_image_selected")
        if product_img_tag:
            img_tag = product_img_tag.find("img")
            if img_tag and img_tag.get('src'):
                product_img = img_tag['src']

        # 提取产品名称
        product_name = "N/A"
        product_name_tag = product_soup.find("div", class_="item_overview_detail")
        if product_name_tag:
            h1_tag = product_name_tag.find("h1")
            if h1_tag:
                product_name = h1_tag.get_text(strip=True)

        # 提取产品价格
        product_price = "N/A"
        product_price_tag = product_soup.find("p", class_="price new_price")
        if product_price_tag:
            product_price = format_price(product_price_tag.get_text(strip=True))

        # 提取产品发售日期
        product_date = "N/A"
        product_date_tag = product_soup.find("span", class_="num")
        if product_date_tag:
            product_date = format_release_date(product_date_tag.get_text(strip=True))

        # 输出爬取信息
        print(f"产品名称：{product_name}")
        print(f"产品价格：{product_price}")
        print(f"产品发售：{product_date}")
        print(f"产品图片：{product_img}")

        # 存入数据库
        insert_product(product_name, product_price, product_date, product_img)

    except Exception as e:
        print(f"获取 {product_url} 时发生错误: {e}")

# 创建数据库表（只需要执行一次）
create_table()

year = 2024
month = 11

# 遍历页码（假设有 29 页）
for i in range(1, 30):
    list_url = (f'https://www.animate-onlineshop.jp/products/list.php?smt=Conan&ss=9&sl=80'
                f'&ssy={year}&ssm={month}&nd[]=7&nf=1&pageno={i}')
    print(f"\n正在处理列表页: {list_url}")
    
    # 请求列表页
    req = Request(list_url, headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    
    # 提取所有产品详情链接
    product_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/pn/" in href:
            full_url = ("https://www.animate-onlineshop.jp" + href) if href.startswith("/") else href
            product_links.add(full_url)
    
    print(f"在第 {i} 页找到 {len(product_links)} 个产品链接。")
    
    # 遍历产品链接爬取详情
    for product_url in product_links:
        parse_product(product_url)
        time.sleep(0.5)
    
    time.sleep(1)
