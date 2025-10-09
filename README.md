# Elastic Llama 🦙
Elastic Llama é um sistema de Recuperação Aumentada por Geração (RAG) que integra o poder do LlamaIndex, a eficiência de busca do Elasticsearch e a inteligência do Llama 3. Ele permite que você faça perguntas em linguagem natural sobre seus próprios documentos e obtenha respostas precisas e contextualizadas.


## 📖 Como Funciona?
O sistema segue um fluxo RAG clássico:

Indexação (Ingestão): Você faz o upload de seus documentos (PDF, TXT, JSON, etc.). O LlamaIndex processa e divide esses documentos em pedaços menores (chunks), que são então convertidos em vetores numéricos e armazenados no Elasticsearch para busca rápida.

Recuperação (Retrieval): Quando você faz uma pergunta, sua consulta é usada para buscar os "chunks" de documentos mais relevantes no Elasticsearch.

Geração (Generation): Os "chunks" recuperados são enviados como contexto para o Llama 3, junto com sua pergunta original. O Llama 3 então gera uma resposta coesa e contextualizada com base nas informações encontradas nos seus documentos.

## 🚀 Funcionalidades
📄 Upload de Múltiplos Formatos: Carregue seus documentos nos formatos .pdf, .txt, .json e outros.

🔍 Busca Vetorial Eficiente: Utiliza o Elasticsearch como um motor de busca vetorial para encontrar informações relevantes rapidamente.

🧠 Geração de Respostas com Llama 3: Obtenha respostas inteligentes e contextualizadas geradas por um dos mais modernos modelos de linguagem.

🖥️ Interface Interativa: Uma interface simples e amigável construída com Streamlit para facilitar o upload e as consultas.

⚙️ Arquitetura Escalável: Componentes desacoplados que facilitam a manutenção e a escalabilidade.

## 🛠️ Configuração do Ambiente
Vamos configurar tudo passo a passo! Siga estas instruções com atenção.

1. Pré-requisitos (O que você precisa ter instalado)
Python 3.8+ e pip

Docker (Método recomendado para rodar o Elasticsearch)

LM Studio (Para rodar o Llama 3 localmente)

2. Configurando o Elasticsearch
O Elasticsearch será nosso banco de dados vetorial. A maneira mais fácil de executá-lo é com o Docker.

Abra seu terminal.

Execute o comando abaixo para baixar e iniciar um contêiner do Elasticsearch:

docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.11.1

Nota: A flag xpack.security.enabled=false desativa a autenticação, facilitando a configuração para desenvolvimento local. Não use isso em produção!

Para verificar se o Elasticsearch está funcionando, acesse http://localhost:9200 no seu navegador ou execute curl http://localhost:9200. Você deve ver uma resposta em JSON.

3. Configurando o Llama 3 com LM Studio
O LM Studio facilita a execução de modelos de linguagem como o Llama 3 em sua máquina.

Baixe e instale o LM Studio: Acesse o site oficial do LM Studio.

Baixe o Modelo Llama 3:

Abra o LM Studio e clique no ícone de busca (lupa) na barra lateral esquerda.

Procure por Llama 3.

Recomendamos baixar um modelo GGUF quantizado, como o "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf", que oferece um bom equilíbrio entre desempenho e uso de recursos.

Inicie o Servidor Local:

Clique no ícone <-> na barra lateral para ir para a aba "Local Server".

No topo, selecione o modelo Llama 3 que você acabou de baixar.

Clique em "Start Server".

O LM Studio agora está expondo uma API compatível com a OpenAI em http://localhost:1234/v1. O Elastic Llama se conectará a este endereço.

## 🚀 Instalação e Execução do Projeto
Com o Elasticsearch e o Llama 3 rodando, agora podemos configurar e executar o projeto.

Clone o repositório:

git clone [https://github.com/gabitenoriob/elastic-llama.git](https://github.com/gabitenoriob/elastic-llama.git)
cd elastic-llama

Crie e ative um ambiente virtual:

### Crie o ambiente
python -m venv venv

### Instale as dependências:

pip install -r requirements.txt

Indexe seus documentos:

Coloque os documentos que você deseja consultar dentro da pasta data/.

## Execute o script de indexação para processar os arquivos e enviá-los para o Elasticsearch.

python index.py

## Execute a aplicação Streamlit:

streamlit run app.py

Acesse o endereço local fornecido pelo Streamlit (geralmente http://localhost:8501) no seu navegador e comece a fazer perguntas!
