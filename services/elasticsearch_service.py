from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

def test_connection():
    if es.ping():
        print("Conectado ao Elasticsearch.")
    else:
        print("Falha ao conectar ao Elasticsearch.")

def create_elasticsearch_index(index_name='teste'):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Índice '{index_name}' excluído.")
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
    print(f"Índice '{index_name}' criado.")

def add_file_to_elasticsearch(file_path, file_name, file_content, index_name='teste'):
    chunk_size = 1000
    for i in range(0, len(file_content), chunk_size):
        chunk_text = file_content[i:i+chunk_size]
        es.index(index=index_name, body={
            "content": chunk_text,
            "filename": file_name
        })

def search_documents(keywords: list, index_name='teste'):
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"content": " ".join(keywords)}},
                    {"match": {"content": {"query": " ".join(keywords), "fuzziness": "AUTO"}}}
                ],
                "minimum_should_match": 1
            }
        },
        "size": 5
    }
    try:
        response = es.search(index=index_name, body=query)
        return [hit['_source']['content'][:50000] for hit in response['hits']['hits']]
    except Exception as e:
        print(f"Erro na busca ES: {e}")
        return []
