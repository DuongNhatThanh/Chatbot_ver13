
query = "bán cho anh điều hòa MDV 1 chiều với giá 10 triệu nhé"

######## TEST ELASTICSEARCH ########
# from module_elastic import search_db, classify_intent
# demands = classify_intent(question=query)
# response = search_db(demands=demands)
# print(response[0])

####### TEST CHAT MAIN ########
from source.chat import chat_with_history_copy
response = chat_with_history_copy(query=query)
print(response)

######## TEST TOOL SEARCH ########
# import source.tool_search
# query = "Obama sinh năm bao nhiêu" + " tiki"
# response = search_similar_product(query=query)
# print(response)

######### TEST ROUTER ########
# from source.router import decision_search_type

# query = "bán cho tôi điều hòa Daikin 1 chiều 9000 BTU không ?"
# response = decision_search_type(query=query)
# print(response)