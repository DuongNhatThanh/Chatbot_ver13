import re
import ast
import pandas as pd
from typing import Dict, List, Tuple, Optional
from elasticsearch import Elasticsearch
from utils import timing_decorator
from module_elastic import init_elastic, find_closest_match, parse_specification_range, get_keywords
from logs.logger import set_logging_terminal
from configs.config_system import SYSTEM_CONFIG


NUMBER_SIZE_ELAS = SYSTEM_CONFIG.num_size_elas
DATAFRAME = pd.read_excel(SYSTEM_CONFIG.csv_all_product_directory)
INDEX_NAME = SYSTEM_CONFIG.index_name
MATCH_THRESHOLD = 75

def create_filter_range(field: str, value: str) -> Dict:
    """
    Hàm này tạo ra filter range cho câu query.

    Args:
        - field: tên field cần filter
        - value: giá trị cần filter
    Return:
        - trả về dictionary chứa thông tin filter range
    """
    min_value, max_value = parse_specification_range(value)
    range_filter = {
        "range": {
            field: {
                "gte": min_value,
                "lte": max_value
            }
        }
    }
    return range_filter

def create_elasticsearch_query(product: str, product_name: str, 
                         specifications: Optional[str] = None,
                         price: Optional[str] = None,
                         power: Optional[str] = None,
                         weight: Optional[str] = None,
                         volume: Optional[str] = None,) -> Dict:
    """
    Tạo ra câu query cho ElasticSearch.
    """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"group_product_name": product}},
                    {"match": {"group_name": product_name}}
                ]
            }
        },
        "size": NUMBER_SIZE_ELAS
    }

    if specifications:
        query['query']['bool']['must'].append({"match": {"specifications": specifications}})

    for field, value in [('lifecare_price', price), ('power', power), ('weight', weight), ('volume', volume)]:
        if value:  # Nếu có thông số cần filter
            print(value)
            order, word, _value = get_keywords(value)
            if word: # Nếu cần search lớn nhất, nhỏ nhất, min, max
                query["sort"] = [
                    {field: {"order": order}}
                ]
                value = _value
            query['query']['bool']['must'].append(create_filter_range(field, value))
    return query

def bulk_search_products(client: Elasticsearch, queries: List[Dict]) -> List[Dict]:
    """
    Hàm này dùng để search nhiều query trên elasticsearch.

    Args:
        - client: elasticsearch client
        - queries: list chứa các query cần search
    Return:
        - trả về list chứa kết quả search
    """
    body = []
    for query in queries:
        body.extend([{"index": INDEX_NAME}, query])
    
    results = client.msearch(body=body)
    return results['responses']

@timing_decorator
def search_db(demands: Dict)-> Tuple[str, List[Dict], int]:

    """
    Hàm này dùng để search thông tin sản phẩm trên elasticsearch.

    Args:
        - demands: dictionary chứa thông tin cần search
    Returns:
        - trả về câu trả lời, list chứa thông tin sản phẩm, và số lượng sản phẩm tìm thấy
    """

    client = init_elastic(DATAFRAME, INDEX_NAME)
    list_products = DATAFRAME['group_name'].unique()
    product_names = demands['object']
    prices = demands['price']

    queries = []
    for product_name, price in zip(product_names, prices):
        match_product, match_score = find_closest_match(product_name, list_products)

        if match_score < MATCH_THRESHOLD:
            set_logging_terminal().info(f"Không tìm thấy sản phẩm {product_name}")
            continue
        product = DATAFRAME[DATAFRAME['group_name'] == match_product]['group_product_name'].iloc[0]
    
        query = create_elasticsearch_query(
            product, product_name, demands.get('specifications'),
            price, demands.get('power'), demands.get('weight'), demands.get('volume')
        )

        print(query)

        queries.append(query)
    
    if not queries:
        return "", [], 0
    
    results = bulk_search_products(client, queries)
    out_text = ""
    products = []
    check = 2 if results[0]['hits']['hits'] else 0

    for product_name, result in zip(product_names, results):
        for i, hit in enumerate(result['hits']['hits'][:4]):
            product_details = hit['_source']
            out_text += format_product_output(i, product_details)
            products.append({
                "code": product_details['product_info_id'],
                "name": product_details['product_name'],
                "link": product_details['file_path']
            })

    return out_text, products, check

def format_product_output(index: int, product_details: Dict) -> str:
    return (f"\n{index + 1}. *{product_details['product_name']} - Mã: {product_details['product_code']}\n"
            f"  Thông số sản phẩm: {product_details['specification']}\n"
            f"  Giá tiền: {product_details['lifecare_price']:,.0f} đ*\n")