# SALES ARMY CHATBOT

## **1. Pipeline**

## **2. Tree project**
    ├── app.py                              # demo on gradio app
    ├── configs
    │   ├── config_fewshot                  # config cho elastic search và các ví dụ fewshot
    │   │   ├── enum.py
    │   │   ├── example_fewshot.yml
    │   ├── config.yml
    │   ├── __init__.py
    │   ├── load_config.py
    ├── data
    │   ├── Cau_hoi_thuong_gap.csv          # file chứa các câu hỏi thường gặp của khách hàng
    │   ├── dieu_hoa.csv                    # file sản phẩm điều hòa
    │   ├── product_final_300_extract.xlsx  # file tất cả các sản phẩm
    │   └── vector_db                       # folder lưu embedding của sản phẩm và câu hỏi thường gặp
    │       ├── Cau_hoi_thuong_gap
    │       │   └── chroma.sqlite3
    │       └── dieu_hoa
    │           └── chroma.sqlite3
    ├── elastic_search                      # folder chưa code sử dụng elastic search để search thông tin sp
    │   ├── few_shot_sentence.py
    │   ├── indexing_db.py
    │   └── retrieval.py
    ├── images                              # ảnh giao diện app
    │   ├── avt_bot.png
    │   ├── avt_vcc.png
    │   └── image.png
    ├── logs                                # chứa 3 loại log: thông tin, lỗi, thời gian
    │   ├── error
    │   ├── logger.py
    │   ├── terminal
    │   └── times
    ├── README.md                       
    ├── requirements.txt                    # các thư viện yêu cầu của project
    ├── source
    │   ├── generater.py                    # file chat chính 
    │   ├── load_db.py                      # load vector embedding
    │   ├── retriever.py                    # file khởi tạo retrieval và lấy context 
    │   └── router.py                       # router điều hướng: elastic search, chroma db, tương tự, tồn kho
    ├── test_code.py
    └── utils                               # các file code sử dụng cho cho các file khác
        ├── base_model.py                   # base model        
        ├── caculate_time.py                # tính thời gian
        ├── data_process.py                 # convert csv to text
        ├── __init__.py                     # import các thư viện từ module utils
        └── prompt.py                       # chưa toàn bộ prompt cho LLM

## **3. Run project**

    1. Configure .env file (similar to .example_env file)

    2. Install the necessary libraries for the project 
        pip install -r requirements.txt

    3. Chat with chatbot on gradio
        python3 run app.py

## **4. Demo**