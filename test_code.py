# from source.chat import chat_with_history_copy
from module_elastic import (
    classify_intent,
    search_db
)
query = "bán cho tôi điều hòa có công suất 9000BTU"
# response = chat_with_history_copy(query)
# print(response)
demands = classify_intent(query)
print(demands)
response, _, _ = search_db(demands=demands)
print(response)
# context = get_context(query="bán cho tôi điều hòa 10 triệu", db_name="Cau_hoi_thuong_gap")
# print(context)
# response = chat_with_history_copy(query)
# print(response)

# from source.router import call_function
# import re
# results = call_function(query)
# parameters = results['arguments']

# def parse_string_to_dict(input_string: str) -> dict:
#     pairs = input_string.replace('{', '').replace('}', '').replace('"', '').strip().split(',')
#     results = {}
#     current_key = None
#     for pair in pairs:
#         if ':' in pair:
#             key, value = pair.split(":")
#             current_key = key.strip()
#             results[current_key] = [value.strip()]
#         else:
#             if current_key is not None:
#                 results[current_key].append(pair.strip())

#     # chuyển các value có 1 giá trị về dạng string
#     for key in results:
#         if len(results[key]) == 1:
#             results[key] = results[key][0]
    
#     return results
# print(parse_string_to_dict(parameters))

# dict = {'object': '', 'price': '', 'power': '', 'weight': '', 'volume': '', 'specifications': ''}
# for key, value in parameters.items():
#     dict[key] = value

# print(dict)
# results = classify_intent(query)
# print(type(results['price']))