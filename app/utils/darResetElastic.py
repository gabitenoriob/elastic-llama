from elasticsearch import Elasticsearch

# Conectar ao Elasticsearch
es = Elasticsearch("http://localhost:9200")

es.options(ignore_status=[400, 404]).indices.delete(index="_all")

print("Todos os índices foram excluídos!")
