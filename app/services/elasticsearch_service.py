from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

def create_elasticsearch_index(index_name='report_data'):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text"},
                    "filename": {"type": "text"}
                }
            }
        })
        print(f"Índice '{index_name}' criado com sucesso.")

def search_documents(query, index_name='report_data'):
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content"]
            }
        }
    }
    response = es.search(index=index_name, body=search_query)
    return [hit['_source']['content'] for hit in response['hits']['hits']]
