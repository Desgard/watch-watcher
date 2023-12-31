import re
import json
from datetime import datetime


def parse_watch_info(info_str):
    # 正则表达式模式
    url_pattern = r'https?://[^\s]+'
    watch_id_pattern = r'\b\d+\b'
    date_pattern = r'\b\d{4}\.\d{1,2}\b'
    condition_pattern = r'未使用|新品|中古'  # 根据实际情况调整
    additional_info_pattern = r'フルセット'  # 根据实际情况调整
    price_pattern = r'金額\d+万?'

    # 使用正则表达式查找匹配项
    url = re.search(url_pattern, info_str)
    watch_id = re.search(watch_id_pattern, info_str)
    date_str = re.search(date_pattern, info_str)
    condition = re.search(condition_pattern, info_str)
    additional_info = re.search(additional_info_pattern, info_str)
    price_str = re.search(price_pattern, info_str)

    # 解析和转换
    date_obj = datetime.strptime(date_str.group(), "%Y.%m").date() if date_str else None
    price = None
    if price_str:
        price_num = int(re.sub(r'\D', '', price_str.group()))
        if '万' in price_str.group():
            price = price_num * 10000
        else:
            price = price_num

    return {
        "url": url.group() if url else None,
        "id": watch_id.group() if watch_id else None,
        "date": date_obj,
        "condition": condition.group() if condition else None,
        "note": additional_info.group() if additional_info else None,
        "price": price
    }


if __name__ == "__main__":
    pass

test = """https://www.chrono24.jp/patekphilippe/patek-philippe-nautilus-5712-white-gold-leather-5712g-001-like-new-2019-full-set--id26625810.htm
5712G-001
2017年
中古
フルセット
金額995万

納期3.4日
    """
print(str(json.dumps(parse_watch_info(test))))
