import httpx
import asyncio
import time
import random

async def send_request(client: httpx.AsyncClient, client_id: str, cpf: str):
    """Envia uma requisição ao proxy e imprime a resposta."""
    try:
        response = await client.get(
            f"http://127.0.0.1:8000/proxy/score?cpf={cpf}",
            headers={"client-id": client_id},
            timeout=10
        )
        response.raise_for_status()
        print(f"Requisição para CPF {cpf} - Resposta do proxy: {response.json()}")
    except httpx.HTTPStatusError as exc:
        print(f"Erro ao processar a requisição para CPF {cpf}: {exc.response.status_code} - {exc.response.text}")
    except httpx.RequestError as exc:
        print(f"Erro de conexão para CPF {cpf}: {exc}")

async def main(num_requests: int):
    """Dispara uma rajada de requisições."""
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(num_requests):
            test_cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            tasks.append(send_request(client, "seu-client-id", test_cpf))

        print(f"Iniciando uma rajada de {num_requests} requisições...")
        start_time = time.time()
        
        await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"\nRajada de {num_requests} requisições concluída em {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    NUM_REQUESTS = 20
    asyncio.run(main(NUM_REQUESTS))

