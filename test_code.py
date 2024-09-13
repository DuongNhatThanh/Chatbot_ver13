from source.generater import chat_with_history_copy
from elastic_search.few_shot_sentence import classify_intent
from elastic_search.retrieval import search_db


query = "bán cho tôi điều hòa có công suất 12000 BTU"
demands = classify_intent(query)

response = search_db(demands=demands)
print(response)


# context = get_context(query="bán cho tôi điều hòa 10 triệu", db_name="Cau_hoi_thuong_gap")
# print(context)
# response = chat_with_history_copy(query)
# print(response)