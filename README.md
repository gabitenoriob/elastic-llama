# Elastic Llama

**Elastic Llama** é um sistema de Recuperação Aumentada por Geração (RAG) que integra [LlamaIndex](https://github.com/jerryjliu/llama_index), [Elasticsearch](https://www.elastic.co/) e Llama 3 para consultas em linguagem natural sobre seus documentos.

## 🚀 Funcionalidades

- 📄 Upload de documentos (JSON, TXT,PDF etc.)
- 🔍 Busca eficiente com Elasticsearch
- 🧠 Respostas geradas por Llama 3 com base nos documentos
- 🖥️ Interface interativa com Streamlit
- ⚙️ Arquitetura escalável

## 🧰 Pré-requisitos

- Python 3.8+
- [Elasticsearch](https://www.elastic.co/downloads/elasticsearch)
- [Ollama](https://ollama.com/) com Llama 3

## 🛠️ Instalação

```bash
git clone https://github.com/gabitenoriob/elastic-llama.git
cd elastic-llama
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.0
run streamlit run app.py
```


├── app.py                  # App Streamlit

├── index.py                # Indexação no Elasticsearch

├── query.py                # Consulta e geração com Llama

├── assets/                 # Arquivos estáticos

├── data/                   # Documentos carregados



