import os
import dotenv
import pandas as pd
from elasticsearch import Elasticsearch

dotenv.load_dotenv()

def init_elastic(df: pd.DataFrame, index_name: str) -> Elasticsearch:
    # Create the client instance
    # client = Elasticsearch(
    # # For local development
    # # hosts=["http://localhost:9200"]
    # hosts=[ELASTIC_HOST]
    # )
    client = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY"),
    )
    # Define the mappings
    mappings = {
        "properties": {
            "product_info_id": {"type": "text"},
            "group_product_name":{"type": "keyword"},
            "product_code":{ "type":"text"},
            "group_name": {"type": "text"},
            "product_name": {"type": "text"},
            "file_path": {"type" : "text"},
            "short_description": {"type": "text"},
            "specification": {"type": "text"},
            "power": {"type": "float"},
            "weight": {"type": "float"},
            "volume": {"type": "float"},
            "lifecare_price": {"type": "float"}
        }
    }

    # Create the index with mappings
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body={"mappings": mappings})
        # Index documents
        for i, row in df.iterrows():
            doc = {
                "product_info_id": row["product_info_id"],
                "group_product_name": row["group_product_name"],
                "product_code": row["product_code"],
                "group_name": row["group_name"],
                "product_name": row["product_name"],
                "file_path": row["file_path"],
                "short_description": row["short_description"],
                "specification": row["specification"],
                "power": row["power"],
                "weight": row["weight"],
                "volume": row["volume"],
                "lifecare_price": row["lifecare_price"]
            }
            client.index(index=index_name, id=i, document=doc)

        client.indices.refresh(index=index_name)
        print(f"Index {index_name} created.")
    else:
        print(f"Index {index_name} already exists.")

    return client