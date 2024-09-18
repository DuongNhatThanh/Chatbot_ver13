from source.chat import chat_with_history_copy
from module_elastic import (
    search_db, parse_string_to_dict
)
query = "bán cho tôi điều hòa có công suất 9000BTU"
response = chat_with_history_copy(query)
print(response)
# context = get_context(query="bán cho tôi điều hòa 10 triệu", db_name="Cau_hoi_thuong_gap")
# print(context)
# response = chat_with_history_copy(query)
# print(response)

# from source.router import call_function
# results = call_function(query)
# response = results['arguments']
# demands = parse_string_to_dict(response)
# print(demands)


# response, _, _ = search_db(demands=demands)
# print(response)
