# DESAFIO-TADS
# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install "fastapi[all]" httpx prometheus-fastapi-instrumentator

uvicorn proxy_service:app --reload

python3 test_client.py
