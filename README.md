安装python：https://www.python.org/downloads/
预装环境：pip install

存数据：
1. 把销售文件放入data/sales 文件夹里 
2. 运行：python -m ingestions.sales_ingest

跑数据：
1. 原料的总消耗：python -m querys.ingredients
2. 每种饮品的销售排名： python -m querys.sales