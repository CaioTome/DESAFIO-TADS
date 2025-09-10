import asyncio
from typing import Dict, Any
import httpx
from fastapi import FastAPI, HTTPException, Request
from prometheus_fastapi_instrumentator import Instrumentator

# A URL da API externa a ser consumida
API_URL = "https://score.hsborges.dev/api/score"

# A fila (FIFO) para armazenar as requisições
request_queue = asyncio.Queue()

# Variáveis para controle do rate limiting e do agendamento
last_request_time = 0
RATE_LIMIT_DELAY = 1  # 1 requisição por segundo

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="Serviço de Proxy Interno",
    description="Proxy resiliente para consumir a API externa `score.hsborges.dev`."
)

# Adiciona instrumentação para métricas Prometheus
@app.on_event("startup")
async def startup_event():
    Instrumentator().instrument(app).expose(app)

async def process_requests_from_queue():
    """
    Processa as requisições da fila, garantindo o rate limiting.
    """
    global last_request_time
    while True:
        # Pega a próxima requisição da fila de forma assíncrona
        # Espera se a fila estiver vazia
        request_data = await request_queue.get()
        
        current_time = asyncio.get_event_loop().time()
        time_to_wait = RATE_LIMIT_DELAY - (current_time - last_request_time)
        
        # Se o tempo de espera for maior que zero, pausa a execução
        if time_to_wait > 0:
            await asyncio.sleep(time_to_wait)

        # Realiza a chamada à API externa
        client = httpx.AsyncClient()
        try:
            # A API espera client-id no header e cpf na query
            response = await client.get(
                API_URL, 
                headers=request_data['headers'], 
                params=request_data['query_params'], 
                timeout=5
            )
            response.raise_for_status() # Lança um erro para status 4xx/5xx

            # Retorna a resposta ao cliente original (utilizando o Future)
            request_data['future'].set_result(response.json())

        except httpx.HTTPStatusError as exc:
            # Lida com erros da API externa
            error_message = f"Erro da API externa: {exc.response.status_code} - {exc.response.text}"
            request_data['future'].set_exception(HTTPException(status_code=exc.response.status_code, detail=error_message))
        except httpx.RequestError as exc:
            # Lida com erros de rede ou timeout
            error_message = f"Erro ao conectar com a API externa: {str(exc)}"
            request_data['future'].set_exception(HTTPException(status_code=503, detail=error_message))
        finally:
            await client.aclose()
            
        last_request_time = asyncio.get_event_loop().time()
        request_queue.task_done()

@app.on_event("startup")
async def start_queue_processor():
    """
    Inicia a tarefa assíncrona que processa a fila no startup da aplicação.
    """
    asyncio.create_task(process_requests_from_queue())

@app.get("/proxy/score")
async def proxy_score(request: Request):
    """
    Endpoint principal que recebe as requisições dos clientes internos.
    
    Ele enfileira a requisição e espera pela resposta do processador da fila.
    """
    # Cria um objeto Future para esperar o resultado da requisição
    future = asyncio.Future()

    # Encapsula os dados da requisição em um "objeto de comando"
    command_data = {
        "headers": request.headers,
        "query_params": request.query_params,
        "future": future
    }
    
    # Adiciona a requisição à fila
    await request_queue.put(command_data)

    # Espera a resposta do processador da fila
    return await future

@app.get("/health")
def health_check():
    """
    Endpoint de health check (liveness/readiness).
    """
    return {"status": "ok", "queue_size": request_queue.qsize()}

