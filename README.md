No documento [Próximos Pássos](https://github.com/CaioTome/DESAFIO-TADS/blob/main/NextSteps.md), há o que será feito depois com os padrões de Projeto

# Como rodar (ainda n testei pq a net da facom n ajuda)
# DESAFIO-TADS
# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install "fastapi[all]" httpx prometheus-fastapi-instrumentator

uvicorn proxy_service:app --reload

python3 test_client.py
