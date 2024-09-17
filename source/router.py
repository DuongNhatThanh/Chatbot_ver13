import openai
from utils.prompt import PROMP_CALLING


def extract_product_els(product_name, price, power, weight, volume, specifications):
    '''
    Bạn là chuyên gia phân tích dữ liệu lấy thông tin từ "Input" và trả về đầy đủ các thông tin bên dưới:
    Inputs:
        product_name (str): Tên của sản phẩm
        price (str): Giá của sản phẩm
        power (str): Công suất của sản phẩm
        weight (str): Khối lượng của sản phẩm
        volume (str): Thể tích của sản phẩm
        specifications (str): Thông tin khác của sản phẩm
    '''

def extract_product_text(input_text):
    '''
    Bạn là chuyên gia phân tích dữ liệu lấy thông tin từ "Input" và trả về đúng thông tin bên dưới:
    Inputs:
        input_text (str): Toàn bộ nội dung văn bản đầu vào
    '''

def extract_similarity(similarity_product):
    '''
    Bạn là chuyên gia phân tích dữ liệu lấy thông tin từ "Input" và trả về thông tin về sản phẩm tương tự
    Inputs:
        similarity_product (str): Nếu trong câu có từ "sản phẩm tương tự" hay "tương tự" thì giá trị của similarity_product bằng "sản phẩm tương tự" còn nếu trong câu không có từ "sản phẩm tương tự" thì bằng ""
    '''


# Defining how we want ChatGPT to call our custom functions
my_custom_functions = [
    {
        'name': 'extract_product_els',
        'description': 'Nhận thông tin "Input" từ nội dung văn bản đầu vào sau đó phải trả ra tất cả những thông tin tôi cho ở dưới. Chú ý phỉa trả ra tất cả các giá trị bên dưới.',
        'parameters': {
            'type': 'object',
            'properties': {
                'product_name': {
                    'type': 'string',
                    'description': 'Hãy lấy tên của sản phẩm có trong câu hỏi, nếu từ 2 sản phẩm trở lên thì ví dụ như : "product_name":"đèn năng lượng", "điều hòa".'
                },
                'price': {
                    'type': 'string',
                    'description': 'Hãy lấy giá của sản phẩm có trong câu hỏi nếu không có thì "price" = "" , trường hợp "giá rẻ" hoặc "giá đắt nhất" thì lấy nguyên các cụm đó.'
                },
                'power': {
                    'type': 'string',
                    'description': 'Hãy lấy công suất của sản phẩm có trong câu hỏi nếu không có thì "power" = "" , trường hợp "công suất nhỏ nhất" hoặc "công suất lớn nhất" thì lấy nguyên các cụm đó.'
                },
                'weight': {
                    'type': 'string',
                    'description': 'Hãy lấy khối lượng của sản phẩm có trong câu hỏi nếu không có thì "weight" = "" , trường hợp "khối lượng nhỏ nhất" hoặc "khối lượng lớn nhất" thì lấy nguyên các cụm đó.'
                },
                'volume': {
                    'type': 'string',
                    'description': 'Hãy lấy khối lượng của sản phẩm có trong câu hỏi nếu không có thì "volume" = "" , trường hợp "thể tích nhỏ nhất" hoặc "thể tích lớn nhất" thì lấy nguyên các cụm đó.'
                },
                'specifications': {
                    'type': 'string',
                    'description': 'Hãy lấy những thông tin khác của sản phâm'
                }
            }
        }
    },
    {
        'name': 'extract_product_text',
        'description': 'Nhận thông tin "Input" từ nội dung văn bản đầu vào sau đó phải trả đúng thông tin tôi cho ở dưới',
        'parameters': {
            'type': 'object',
            'properties': {
                'input_text': {
                    'type': 'string',
                    'description': 'Trả ra toàn bộ nội dung văn bản đầu vào'
                }
            }
        }
    },
    {
        'name': 'extract_similarity',
        'description': 'Nhận thông tin "Input" từ nội dung văn bản đầu vào sau đó phải trả ra thông tin tôi cho ở dưới',
        'parameters': {
            'type': 'object',
            'properties': {
                'similarity_product': {
                    'type': 'string',
                    'description': 'Nếu trong câu có từ "sản phẩm tương tự" thì giá trị của inventory bằng "sản phẩm tương tự" còn nếu trong câu không có từ "sản phẩm tương tự" thì bằng ""'
                }
            }
        }
    }
]



def call_funcion(input: str) -> str:
    """
    Sử dụng function calling để gọi các hàm custom và phân loại câu hỏi của người dùng.
    Args:
        - input: câu hỏi của người dùng
    Return:
        - function_called: tên hàm được gọi
    """

    openai_response = openai.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {'role': 'system', 'content': PROMP_CALLING},
            {'role': 'user', 'content': input}
        ],
        functions = my_custom_functions,
        function_call = 'auto'
    )

    TEMP = openai_response.choices[0].message
    if TEMP.content is not None:
        return "LLM_predict"
    else:
        function_called = TEMP.function_call.name
        return function_called
    
if __name__ == "__main__":
    print(call_funcion("Tôi muốn mua điều hòa 10 triệu"))