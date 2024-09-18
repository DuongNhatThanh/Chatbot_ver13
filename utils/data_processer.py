import os
import csv
from typing import List
from configs.config_system import LoadConfig
from langchain_core.documents import Document

APP_CFG = LoadConfig()

def csv2txt_product(csv_link: str) -> List[Document]:
    """
    Hàm này để chuyển đổi file CSV thành file văn bản TXT. 
    Với mỗi hàng trong file CSV sản phấm, chuyển thành đoạn 1 text.
    """
    data_text = []
    with open(csv_link, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Lấy thông tin từ mỗi hàng của file CSV
            product_name = row['product_name'] 
            product_code = row['product_code'] 
            specification = row['specification'] 
            product_info = row['product_info'] 
            lifecare_price = row['lifecare_price'] 
            # In ra văn bản theo định dạng mong muốn
            s1 = f"Sản phẩm: {product_name} có mã sản phẩm là: {product_code}, có giá: {lifecare_price}"
            s2 = f"Sản phẩm: {product_name} có mô tả sản phẩm là:{product_info}"
            s3 = f"Sản phẩm: {product_name} có thông số kỹ thuật là:{specification}"
            data_text.append(Document(s1 + "\n" + s2 + "\n" + s3 + "\n"))
    return data_text


def csv2text_question(csv_link: str) -> List[Document]:

    """
    Hàm này để chuyển đổi file CSV thành file văn bản TXT. 
    Với mỗi hàng trong file CSV về câu hỏi thường gặp, chuyển thành đoạn 1 text.
    """

    data_text = []
    with open(csv_link, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Lấy thông tin từ mỗi hàng của file CSV
            product_name = row['product_name']
            question_user = row['question'] 
            answer_bot = row['answer'] #thông số kỹ thuật
            # join văn bản theo định dạng mong muốn
            s = f"Sản phẩm: {product_name}\nQuestion user: {question_user}\nInstruction answer: {answer_bot}\n"
            data_text.append(Document(s))
    return data_text

# def convert_csv_to_txt():
#     directory_txt = APP_CFG.text_product_directory
#     directory_csv = APP_CFG.csv_product_directory

#     files = [f for f in os.listdir(directory_csv) if os.path.isfile(os.path.join(directory_csv, f))]
#     csv_files = [f for f in files if f.endswith('.csv')]

#     for csv_file in csv_files:
#         # Đọc file CSV
#         csv_path = os.path.join(directory_csv, csv_file)
#         txt_file = csv_file.replace('.csv', '.txt')
#         txt_path = os.path.join(directory_txt, txt_file)
#         data_text = csv2txt(csv_path)
#         with open(txt_path, "w", encoding='utf-8') as file:
#             file.write(data_text)

