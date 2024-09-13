# Đội quân bán hàng

## 1. Pipeline

## 2. Cây thư mục 
    ├── app.py                              # demo on gradio app
    ├── configs
    │   ├── config_fewshot                  # chứa con ví dụ few shot cho sản phẩm
    │   ├── config.yml
    │   ├── load_config.py                  # chứa config cho toàn bộ project
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
    ├── Examples                            # chứa các ví dụ cho few shot
    │   ├── enum.py
    │   ├── example.py
    │   ├── example.yml
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
    ├── requirements.txt                    # các thư viện yêu cầu cảu project
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
