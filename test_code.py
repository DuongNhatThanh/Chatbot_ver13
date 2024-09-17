# from source.generater import chat_with_history_copy
from module_elastic import (
    classify_intent,
    search_db
)

query = "bán cho tôi điều hòa có giá lớn nhất."
demands = classify_intent(query)
print(demands)
response, _, _ = search_db(demands=demands)
# context = get_context(query="bán cho tôi điều hòa 10 triệu", db_name="Cau_hoi_thuong_gap")
# print(context)
# response = chat_with_history_copy(query)
# print(response)
