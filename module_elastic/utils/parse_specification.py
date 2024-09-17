import re
from typing import Tuple
from configs import ELASTICH_SEARCH_CONFIG

def parse_specification_range(specification: str) -> Tuple[float, float]:
    """
    nếu thông số là giá thì xử lí và trả về khảng giá, nếu không thì trả về giá trị mặc định.
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


def get_keywords(specification: str)-> Tuple[str, str, str]:
    """
    Từ phần fewshot thông số kĩ thuật(VD: giá đắt nhất, công suất rẻ nhất...) trong câu hỏi của người dùng.
    Extract ra các thông tin cần thiết cho elastic search
    
    Args:
        specifications: str: phần fewshot từ câu hỏi của elastic search
    Returns:
        order: str: thứ tự sắp xếp của giá (tăng dần hoặc giảm dần) -> keyword để elastic search giảm hoặc tăng dấn của sản phẩm đó.
        word: str: từ khóa giá, công suất, khối lượng, dung tích
        specifications: str = "": thông số kĩ thuật
    """

    order, word= "asc", ""  # Default order
    cheap_keywords = ELASTICH_SEARCH_CONFIG.cheap_keywords
    expensive_keywords = ELASTICH_SEARCH_CONFIG.expensive_keywords

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