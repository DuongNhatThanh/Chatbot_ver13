import re
import ast
import time
import logging
import pandas as pd
from typing import Dict
from elasticsearch import Elasticsearch
from elastic_search.indexing_db import init_elastic
from elastic_search.few_shot_sentence import find_closest_match
from utils import timing_decorator
from configs import ELASTICH_SEARCH_CONFIG, SYSTEM_CONFIG


number_size_elas = ELASTICH_SEARCH_CONFIG.num_size_elas
dataframe = pd.read_excel(SYSTEM_CONFIG.csv_all_product_directory)

def parse_price_range(price):
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k|kg|l|lít|kw|w|t|btu)?\b"
    print(pattern)
    min_price = 0
    max_price = 100000000
    for match in re.finditer(pattern, price, re.IGNORECASE):
        prefix = match.group('prefix') or ''
        number = float(match.group('number').replace(',', ''))
        unit = match.group('unit') or ''
        if unit.lower() == '':
            return min_price, max_price

        if unit.lower() in ['triệu','tr','t']:
            number *= 1000000
        elif unit.lower() in ['nghìn','k']:
            number *= 1000
        elif unit.lower() in ['kw']:
            number *= 1000

        if prefix.lower().strip() == 'dưới':
            max_price = min(max_price, number)
        elif prefix.lower().strip() == 'trên':
            min_price = min(max_price, number)
        elif prefix.lower().strip() == 'từ':
            min_price = min(max_price, number)
        elif prefix.lower().strip() == 'đến':
            max_price = max(min_price, number)
        else:  # Trường hợp không có từ khóa
            min_price = number * 0.8
            max_price = number * 1.2

    if min_price == float('inf'):
        min_price = 0
    print('min_price, max_price:',min_price, max_price)
    return min_price, max_price

def search_specifications(client, index_name, product, product_name, 
                          specifications, price, power, weight, volume):
    order = "asc"  # Default order
    cheap_keywords = ELASTICH_SEARCH_CONFIG.chep_keywords
    expensive_keywords = ELASTICH_SEARCH_CONFIG.expensive_keywords
    word = ""
    for keyword in cheap_keywords:
        if keyword in price.lower():
            order = "asc"
            word = keyword
            price = ""
    for keyword in expensive_keywords:
        if keyword in price.lower():
            order = "desc"
            word = keyword
            price = ""
    
    # Create the Elasticsearch query if a product is found
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "group_product_name": product
                        }
                    },
                    {
                        "match": {
                            "specification": specifications
                        }
                    },
                    {
                        "match": {
                            "group_name": product_name
                        }
                    }
                ]
            }
            },
        "size": number_size_elas,
    }

    if word:
        query["sort"] = [
            {"lifecare_price": {"order": order}}
        ]

    if price :
      min_price, max_price = parse_price_range(price)
      price_filter = {
          "range": {
              "lifecare_price": {
                  "gte": min_price,
                  "lte": max_price
              }
          }
      }
      query["query"]["bool"]["must"].append(price_filter)

    if power:
      min_power, max_power = parse_price_range(power)
      power_filter = {
          "range": {
              "power": {
                  "gte": min_power,
                  "lte": max_power
              }
          }
      }
      query["query"]["bool"]["must"].append(power_filter)

    if weight:
        min_weight, max_weight = parse_price_range(weight)
        weight_filter = {
            "range": {
                "weight": {
                    "gte": min_weight,
                    "lte": max_weight
                }
            }
        }
        query["query"]["bool"]["must"].append(weight_filter)

    if volume:
        min_volume, max_volume = parse_price_range(volume)
        volume_filter = {
            "range": {
                "volume": {
                    "gte": min_volume,
                    "lte": max_volume
                }
            }
        }
        query["query"]["bool"]["must"].append(volume_filter)
    # Execute the search query
    response = client.search(index=index_name, body=query)
    return response
       
def search_prices(client, index_name, product, product_name, 
                  price, power, weight, volume):
    order = "asc"  # Default order
    cheap_keywords = ELASTICH_SEARCH_CONFIG.chep_keywords
    expensive_keywords = ELASTICH_SEARCH_CONFIG.expensive_keywords
    word = ""
    for keyword in cheap_keywords:
        if keyword in price.lower():
            order = "asc"
            word = keyword
            price = ""
    for keyword in expensive_keywords:
        if keyword in price.lower():
            order = "desc"
            word = keyword
            price = ""
    # Build the base query
    # Create the Elasticsearch query if a product is found
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "group_name": product_name
                        }
                    },
                    {
                        "match": {
                            "group_product_name": product
                        }
                    }
                ]
            }
        },
        "size": number_size_elas
    }

    if word:
        query["sort"] = [
            {"lifecare_price": {"order": order}}
        ]

    # Add specifications-based filters
    if price:
        min_price, max_price = parse_price_range(price)
        price_filter = {
            "range": {
                "lifecare_price": {
                    "gte": min_price,
                    "lte": max_price
                }
            }
        }
        query["query"]["bool"]["must"].append(price_filter)

    if power:
        min_power, max_power = parse_price_range(power)
        power_filter = {
            "range": {
                "power": {
                    "gte": min_power,
                    "lte": max_power
                }
            }
        }
        query["query"]["bool"]["must"].append(power_filter)

    if weight:
        min_weight, max_weight = parse_price_range(weight)
        weight_filter = {
            "range": {
                "weight": {
                    "gte": min_weight,
                    "lte": max_weight
                }
            }
        }
        query["query"]["bool"]["must"].append(weight_filter)

    if volume:
        min_volume, max_volume = parse_price_range(volume)
        volume_filter = {
            "range": {
                "volume": {
                    "gte": min_volume,
                    "lte": max_volume
                }
            }
        }
        query["query"]["bool"]["must"].append(volume_filter)


    res = client.search(index=index_name, body=query)

    return res

def search_quantity(client: Elasticsearch, index_name: str, product, product_name, 
                    price, power, weight, volume):
    query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "group_product_name": product
                            }
                        },
                        {
                            "match": {
                                "group_name": product_name
                            }
                        }
                    ]
                }
                },
            "size": 100,
            }
    if price:
        min_price, max_price = parse_price_range(price)
        price_filter = {
            "range": {
                "lifecare_price": {
                    "gte": min_price,
                    "lte": max_price
                }
            }
        }
        query["query"]["bool"]["must"].append(price_filter)

    if power:
        min_power, max_power = parse_price_range(power)
        power_filter = {
            "range": {
                "power": {
                    "gte": min_power,
                    "lte": max_power
                }
            }
        }
        query["query"]["bool"]["must"].append(power_filter)

    if weight:
        min_weight, max_weight = parse_price_range(weight)
        weight_filter = {
            "range": {
                "weight": {
                    "gte": min_weight,
                    "lte": max_weight
                }
            }
        }
        query["query"]["bool"]["must"].append(weight_filter)

    if volume:
        min_volume, max_volume = parse_price_range(volume)
        volume_filter = {
            "range": {
                "volume": {
                    "gte": min_volume,
                    "lte": max_volume
                }
            }
        }
        query["query"]["bool"]["must"].append(volume_filter)
    res = client.search(index=index_name, body=query)
    return res

def search_product(client, index_name, product_name):
    query = {
        "query": {
            "bool": {
                "must": [
                    
                    {
                        "match": {
                            "product_name": product_name
                        }
                    }
                ]
            }
        }
    }


    res = client.search(index=index_name, body=query)
    return res


@timing_decorator
def search_db(demands: Dict):
    #init 
    out_text = ""
    products, product_names = [], []
    product_dict = {}
    index_name = ELASTICH_SEARCH_CONFIG.index_name
    # client = init_elastic(df,index_name, ELASTIC_HOST)
    client = init_elastic(dataframe, index_name)
    list_product = dataframe['group_name'].unique()
    check_match_product = find_closest_match(demands['object'][0], list_product)
    # return check_match_product

    print('check_match_product',check_match_product)
    if check_match_product[1] < 75: # nếu độ match < 75 thì không tìm được sản phẩm
        check = 0
        return out_text, products, check
    else:
        product_names = demands['object']
        # if else fill độ dài sản phẩm = độ dài giá
        if isinstance(demands['price'], list):
            prices = demands['price']*len(demands['object'])
        else:
            prices = ast.literal_eval(demands['price'])*len(demands['object'])
        power = demands['power']
        weight = demands['weight']
        volume = demands['volume']
        specifications = demands['specifications']

    t1 = time.time()
    print('------check object----', product_names)
    result = []
    for product_name, price in zip(product_names, prices):
        product_match = find_closest_match(product_name, list_product)[0]
        print("=====product_match====",product_match, product_name)
        result_df = dataframe[dataframe['group_name'] == product_match]
        product = result_df['group_product_name'].tolist()[0]
        # full option specifications, giá, công suất, khối lượng, dung tích
        if specifications and (price or power or weight or volume) or specifications:
            # Count quantity each group name
            if len([specifications]) > 1:
                resp = search_specifications(client, index_name, product, product_name, specifications, price, power, weight, volume)
                check = 2 
            elif price or power or weight or volume:
                resp = search_prices(client, index_name, product, product_name, price,  power, weight, volume)
                check = 2 
            else:
                resp = search_product(client, index_name, product_name)
                check = 2
            
        elif price or power or weight or volume:
            resp = search_prices(client, index_name, product, product_name,price,  power, weight, volume)
            check = 2 
        else:
            resp = search_product(client, index_name, product_name)
            check = 2

        result.append(resp)

    for product_name, product in zip(product_names, result):
        s_name = product_name
        # Check query is None
        if product['hits']['hits'] == [] and check != 0:
            out_text += ""
            break
        cnt = 0
        quantity_name = ""
        for i, hit in enumerate(product['hits']['hits']):
            check_score = hit.get('_score')
            product_details = hit['_source']
            product =  {
                "code" : "",
                "name" : "",
                "link" : ""
            }
            if check_score is None or float(check_score) >= 2.5:
                cnt+=1
                if check == 2:
                    if len(product_names) > 1 and i < 2:
                        out_text += f"\n{i + 1}. *{product_details['product_name']} - Mã: {product_details['product_code']}\n"
                        out_text += f"  Thông số sản phẩm: {product_details['specification']}\n"
                        out_text +=  " - Giá tiền: {:,.0f} đ*\n".format(product_details['lifecare_price'])
                        product = {
                            "code": product_details['product_info_id'],
                            "name": product_details['product_name'],
                            "link": product_details['file_path']
                        }
                    elif len(product_names) == 1 and i < 4:
                        out_text += f"\n{i + 1}. *{product_details['product_name']} - Mã: {product_details['product_code']}\n"
                        out_text += f"  Thông số sản phẩm: {product_details['specification']}\n"
                        out_text +=  " - Giá tiền: {:,.0f} đ*\n".format(product_details['lifecare_price'])
                        product = {
                            "code": product_details['product_info_id'],
                            "name": product_details['product_name'],
                            "link": product_details['file_path']
                        }
                        product_dict[f'{i+1}'] = product_details['product_name']
                elif check == 1 and i < 3:
                    quantity_name +=f"  {product_details['product_name']} - Mã: {product_details['product_code']}\n"
                    # quantity_name +=  " -  Giá tiền: {:,.0f} đ*\n".format(product_details['lifecare_price'])
                    quantity_name += f"  Thông số sản phẩm: {product_details['specification']}\n"
                    quantity_name +=  " - Giá tiền: {:,.0f} đ\n".format(product_details['lifecare_price'])
                    # quantity_name += f"  Mã kho: {product_details['product_code']}\n"
                    product = {
                            "code": product_details['product_info_id'],
                            "name": product_details['product_name'],
                            "link": product_details['file_path']
                        }
                if len(products) < 10 and product['code'] != "":
                    products.append(product)
        if check == 1:
            out_text += f"---Hiện có {cnt} sản phẩm là:"
            out_text += quantity_name
            out_text += f"...còn nữa. Hãy trả lời là có {cnt} sản phẩm!"
    print("-----time elastic search-------:",time.time() - t1)
    logging.info(f'======== elasticsearch output ==========:\n{out_text}')
    print('======== elasticsearch output ==========:\n', out_text)
    return out_text, products, check