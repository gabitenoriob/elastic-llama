from elasticsearch import Elasticsearch
#curl -X DELETE "http://localhost:9200/nomeinidce"
#pegar todos os indices curl -X GET "http://localhost:9200/_cat/indices?v"
#deletar todos os indices curl -X DELETE "http://localhost:9200/_all"
# Conectar ao Elasticsearch
es = Elasticsearch("http://localhost:9200")

if es.options(ignore_status=[400, 404]).indices.delete(index="_all"):
    print("Todos os índices foram excluídos!")
