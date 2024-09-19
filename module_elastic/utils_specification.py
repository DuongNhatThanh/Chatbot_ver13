import re
import ast
from fuzzywuzzy import fuzz, process
from typing import Tuple, Dict, List
from configs import SYSTEM_CONFIG, ELASTIC_SEARCH_CONFIG

def parse_specification_range(specification: str) -> Tuple[float, float]:
    """
    Nếu thông số là giá thì xử lí và trả về khảng giá, nếu không thì trả về giá trị mặc định.
    Args:
        - specification: thông số kĩ thuật cần xử lí
    Returns:
        - trả về min_value, max_value; khoảng cần tìm kiếm của thông số kĩ thuật
    """
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k|kg|l|lít|kw|w|t|btu)?\b"
    min_value = 0
    max_value = 100000000
    for match in re.finditer(pattern, specification, re.IGNORECASE):
        prefix = match.group('prefix') or ''
        number = float(match.group('number').replace(',', ''))
        unit = match.group('unit') or ''
        if unit.lower() == '':
            return min_value, max_value # nếu không phải giá thì trả về giá trị mặc định

        if unit.lower() in ['triệu','tr','t']:
            number *= 1000000
        elif unit.lower() in ['nghìn','k']:
            number *= 1000
        elif unit.lower() in ['kw']:
            number *= 1000

        if prefix.lower().strip() == 'dưới':
            max_value = min(max_value, number)
        elif prefix.lower().strip() == 'trên':
            min_value = min(max_value, number)
        elif prefix.lower().strip() == 'từ':
            min_value = min(max_value, number)
        elif prefix.lower().strip() == 'đến':
            max_value = max(min_value, number)
        else:  # Trường hợp không có từ khóa
            min_value = number * 0.8
            max_value = number * 1.2

    if min_value == float('inf'):
        min_value = 0
    print('min_value, max_value:',min_value, max_value)
    return min_value, max_value


def parse_string_to_dict(input_string: str) -> Dict:
    
    """
    Nhận string từ function calling trả về, xử lí string và đưa về dạng dictionary chứa thông tin của các thông số kĩ thuật.
    Dictionary này sẽ là đầu vào cho hàm search_db trong module_elastic/query_engine.py
    Args:
        - input_string: string trả về từ function calling
    Return:
        - trả về dictionary chứa thông tin của các thông số kĩ thuật 
    """

    results = ast.literal_eval(input_string)
    specifications_pairs = {'object': '', 'price': '', 'power': '', 'weight': '', 'volume': '', 'specifications': ''}
    for key, value in results.items():
        specifications_pairs[key] = value
    
    for key, value in specifications_pairs.items():
        if key == 'object': # chuyển object thành list
            specifications_pairs[key] = [x.strip() for x in value.split(',')]
        if key == 'price': # chuyển price thành list
            specifications_pairs[key] = [specifications_pairs[key]]

    # Đưa price có số lượng bằng số lượng object
    specifications_pairs['price'] = specifications_pairs['price'] * len(specifications_pairs['object']) if len(specifications_pairs['price']) == 1 else specifications_pairs['price']
    return specifications_pairs


def get_keywords(specification: str)-> Tuple[str, str, str]:
    """
    Từ các thông số kĩ thuật do function calling extract ra, nếu có các cụm như: giá đắt nhất, công suất rẻ nhất...).
    Extract ra phần order, word, specification để đưa vào câu query của elastic search.
    
    Args:
        specifications: str: phần fewshot từ câu hỏi của elastic search
    Returns:
        order: str: thứ tự sắp xếp của giá (tăng dần hoặc giảm dần) -> keyword để elastic search giảm hoặc tăng dấn của sản phẩm đó.
        word: str: từ khóa giá, công suất, khối lượng, dung tích
        specifications: str = "": thông số kĩ thuật
    """

    order, word = "asc", ""  # Default order
    cheap_keywords = ELASTIC_SEARCH_CONFIG.cheap_keywords
    expensive_keywords = ELASTIC_SEARCH_CONFIG.expensive_keywords

    for keyword in cheap_keywords:
        if keyword in specification.lower():
            order = "asc"
            word = keyword
            specification = ""
    for keyword in expensive_keywords:
        if keyword in specification.lower():
            order = "desc"
            word = keyword
            specification = ""
    return order, word, specification


def find_closest_match(query: str, list_product: List[str]) -> List:
    """
    Hàm này dùng để tìm sản phẩm gần giống nhất với câu query của người dùng trong list_product.
    Args:
        - query: câu query của người dùng
        - list_product: list chứa tên các sản phẩm
    Returns:
        - trả về tên sản phẩm gần giống nhất và độ match
    """
    match = process.extractOne(query, list_product, scorer=fuzz.partial_ratio)
    print(f"Có phải bạn tìm kiếm sản phẩm {match[0]}")
    print("Độ match:", match[1])
    # if match[1] >= 60:
    #     return match[0]
    # else:
    #     return 0
    return match
    