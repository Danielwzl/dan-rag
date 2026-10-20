安装python：https://www.python.org/downloads/
预装环境：pip install

存数据：
1. 把销售文件放入data/sales 文件夹里 
2. 运行：python -m ingestions.sales_ingest

跑数据：
1. 原料的总消耗：python -m querys.ingredients
2. 每种饮品的销售排名： python -m querys.sales


Prompt
帮我把可能是相同的饮品数据合并，并添加一个col作为标记是合并过的数据，最好再标记下总和是怎么计算出来的。有一些规则：
1.比如开头有大写的D和A表示为饮品是delivery和App平台点单的 
2.有一些缩写像BT(BLACK TEA), MGO(MANGO)等等
3.w/ 后面都是额外的topping，和没有w/的是一种饮料
4. 有注明oz的是和原饮料不同的饮料，不能合并，比如32 oz
5. 一种特例，Bubble Tea (L) Redemption和Pearl Milk Tea是一种
你根据规则自己判断，生成新的csv