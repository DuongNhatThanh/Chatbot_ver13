import re
import ast
import time
import logging
import pandas as pd
from typing import Dict
from elasticsearch import Elasticsearch
from module_elastic import (
    init_elastic,
    find_closest_match,
    parse_specification_range,
    get_keywords
)
from utils import timing_decorator
from configs import ELASTICH_SEARCH_CONFIG, SYSTEM_CONFIG


number_size_elas = ELASTICH_SEARCH_CONFIG.num_size_elas
dataframe = pd.read_excel(SYSTEM_CONFIG.csv_all_product_directory)

def search_specifications(client, index_name, product, product_name, 
                          specifications, price, power, weight, volume):
    
    """
    Search các thông số kĩ thuật khác ngoài 4 thông số cơ bản: price, power, weight, volume.
    """
    order = "asc"  # Default order
    cheap_keywords = ELASTICH_SEARCH_CONFIG.cheap_keywords
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
      min_price, max_price = parse_specification_range(price)
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
      min_power, max_power = parse_specification_range(power)
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
        min_weight, max_weight = parse_specification_range(weight)
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
        min_volume, max_volume = parse_specification_range(volume)
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
       
def search_values(client, index_name, product, product_name, 
                  price, power, weight, volume):
    """
    Search các thông số của price, power, weight, volume và có thể search các giá trị min max của các thông số này.
    Args:
        client: Elasticsearch client
        index_name: Tên index
        product: Tên sản phẩm
        product_name: Tên sản phẩm
        price: Giá tiền
        power: Công suất
        weight: Khối lượng
        volume: Dung tích
    Returns:
        response: Kết quả tìm kiếm từ elasticsearch
    """
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

    print(power)

    # Add specifications-based filters
    if price is not None:
        order, word, _price = get_keywords(price)
        if word:
            query["sort"] = [
                {"lifecare_price": {"order": order}}
            ]
        min_price, max_price = parse_specification_range(_price)
        price_filter = {
            "range": {
                "lifecare_price": {
                    "gte": min_price,
                    "lte": max_price
                }
            }
        }
        query["query"]["bool"]["must"].append(price_filter)

    if power is not None:
        order, word, _power = get_keywords(power)
        print(order)
        if word:
            query["sort"] = [
                {"lifecare_price": {"order": order}}
            ]

        min_power, max_power = parse_specification_range(_power)
        power_filter = {
            "range": {
                "power": {
                    "gte": min_power,
                    "lte": max_power
                }
            }
        }
        query["query"]["bool"]["must"].append(power_filter)

    if weight is not None:
        order, word, _weight = get_keywords(weight)
        if word:
            query["sort"] = [
                {"lifecare_price": {"order": order}}
            ]

        min_weight, max_weight = parse_specification_range(_weight)
        weight_filter = {
            "range": {
                "weight": {
                    "gte": min_weight,
                    "lte": max_weight
                }
            }
        }
        query["query"]["bool"]["must"].append(weight_filter)

    if volume is not None:
        order, word, _volume = get_keywords(volume)
        if word:
            query["sort"] = [
                {"lifecare_price": {"order": order}}
            ]
        min_volume, max_volume = parse_specification_range(_volume)
        volume_filter = {
            "range": {
                "volume": {
                    "gte": min_volume,
                    "lte": max_volume
                }
            }
        }
        query["query"]["bool"]["must"].append(volume_filter)


    response = client.search(index=index_name, body=query)

    return response

def search_quantity(client, index_name, product, product_name,value, power, weight, volume):

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
                                "product_name": product_name
                            }
                        }
                    ]
                }
                },
            "size": 100,
            }
    if value :
      print("check value", value)
      min_price, max_price = parse_specification_range(value)
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
      min_power, max_power = parse_specification_range(power)
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
        min_weight, max_weight = parse_specification_range(weight)
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
        min_volume, max_volume = parse_specification_range(volume)
        print(min_volume, max_volume)
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
    print(query)
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
    # return check_match_product
    check_match_product = find_closest_match(demands['object'][0], list_product)
    
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
        print("=" * 50, power)
        weight = demands['weight']
        volume = demands['volume']
        specifications = demands['specifications']

    print('------check object----', product_names)
    result = []
    for product_name, price in zip(product_names, prices):
        product_match = find_closest_match(product_name, list_product)[0]
        print("=====product_match====",product_match, product_name)
        result_df = dataframe[dataframe['group_name'] == product_match]
        product = result_df['group_product_name'].tolist()[0]
        # full option specifications, giá, công suất, khối lượng, dung tích
        if specifications and (price or power or weight or volume) or specifications:
            print('---specifications---', specifications)
            # Count quantity each group name
            if len([specifications]) > 1:
                resp = search_specifications(client, index_name, product, product_name, specifications, price, power, weight, volume)
                check = 2 
            elif price or power or weight or volume:
                resp = search_values(client, index_name, product, product_name, price,  power, weight, volume)
                check = 2 
            else:
                resp = search_product(client, index_name, product_name)
                check = 2
            
        elif price or power or weight or volume:
            print('---price---', price)
            resp = search_values(client, index_name, product, product_name,price,  power, weight, volume)
            check = 2 
        else:
            print('---product---', product_name)
            resp = search_product(client, index_name, product_name)
            check = 2

        result.append(resp)

    for product_name, product in zip(product_names, result):
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
    logging.info(f'======== elasticsearch output ==========:\n{out_text}')
    print('======== elasticsearch output ==========:\n', out_text)
    return out_text, products, check