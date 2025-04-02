const path = require('path');  // 处理文件路径（系统兼容）
const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const { Translate } = require('@google-cloud/translate').v2;


const app = express();
const port = 3000;

// 启用 CORS，允许前端访问
app.use(cors());
app.use(express.json()); // 启用 JSON 解析

// 初始化 Google 翻译
const translate = new Translate({ key: 'AIzaSyCmA-hK_iLybiwoKghnh7SvB2-Y63iftgE' });  // 👈 这里填你的 API Key

// 翻译接口
app.get('/api/translate', async (req, res) => {
  const text = req.query.text;  // 从前端获取要翻译的文本
  const targetLang = req.query.lang; // 目标语言，例如 "zh"、"ja"、"en"

  try {
      const [translation] = await translate.translate(text, targetLang);
      res.json({ translatedText: translation });  // 返回翻译结果
  } catch (error) {
      res.status(500).json({ error: '翻译失败', details: error });
  }
});

// 启动服务器
app.listen(4000, () => console.log('服务器运行在 http://localhost:4000'));

// 创建 MySQL 数据库连接
const db = mysql.createConnection({
  host: 'localhost',   // 数据库服务器地址（本地就是 localhost）
  user: 'root',        // 你的 MySQL 用户名
  password: '',        // 你的 MySQL 密码（如果改过这里也要改）
  database: 'spider_db', // 你的数据库名称
  socketPath: '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
});

// 连接到数据库
db.connect(err => {
  if (err) {
    console.error('无法连接到数据库:', err);
    return;
  }
  console.log('数据库连接成功');
});

// 允许跨域访问
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// 获取所有产品
app.get('/api/products', (req, res) => {
  db.query('SELECT * FROM products', (err, results) => {
    if (err) {
      res.status(500).send('数据库查询失败');
      return;
    }
    res.json(results);  // 返回 JSON 数据
  });
});

// 点赞功能：用户点击点赞时增加点赞数
app.post('/api/like/:id', (req, res) => {
  const productId = req.params.id;

  if (isNaN(productId)) {
      return res.status(400).json({ success: false, message: "无效的产品 ID" });
  }

  //点赞+1
  db.query('UPDATE products SET likes = likes + 1 WHERE id = ?', [productId], (err, result) => {
      if (err) {
          console.error("数据库点赞更新失败:", err);
          return res.status(500).json({ success: false, message: '点赞失败' });
      }

      if (result.affectedRows === 0) {
          return res.status(404).json({ success: false, message: "产品未找到" });
      }

      //获取更新的点赞数
      db.query('SELECT likes FROM products WHERE id = ?', [productId], (err, results) => {
          if (err) {
              console.error("查询点赞数失败:", err);
              return res.status(500).json({ success: false, message: '查询点赞数失败' });
          }
          if (results.length === 0) {
              return res.status(404).json({ success: false, message: "产品未找到" });
          }

          const newLikeCount = results[0].likes; // 获取更新后的点赞数
          res.json({ success: true, newLikeCount });
      });
  });
});




// 获取点赞排行榜（按点赞数降序排列，取前10名）
app.get('/api/ranking', (req, res) => {
  db.query('SELECT name, likes, image_url, price FROM products ORDER BY likes DESC LIMIT 10', (err, results) => {
    if (err) {
      res.status(500).send('查询排行榜失败');
      return;
    }
    console.log(results); // 在终端打印结果，看看 image_url 是否返回
    res.json(results);  // 返回排序后的排行榜数据
  });
});

app.get('/api/translate', (req, res) => {
  res.json({
      title: res.__('title'),
      productList: res.__('productList'),
      ranking: res.__('ranking'),
      price: res.__('price'),
      like: res.__('like')
  });
});


// 启动服务器
app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
});

