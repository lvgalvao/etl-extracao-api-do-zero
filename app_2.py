import requests
import duckdb
import asyncio
import aiohttp
from datetime import datetime
import time

# Função para criar o banco de dados e a tabela no DuckDB
def create_database():
    # Conectar ao banco de dados DuckDB (se não existir, ele será criado em memória ou em arquivo)
    conn = duckdb.connect('bitcoin_prices.duckdb')

    # Criar a tabela (se não existir)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS bitcoin_prices (
        id INTEGER PRIMARY KEY,
        price DOUBLE NOT NULL,  -- Garantir que price não será NULL
        timestamp TIMESTAMP NOT NULL  -- Garantir que timestamp não será NULL
    )
    ''')

    conn.close()

# Função assíncrona para obter o preço do Bitcoin via API com aiohttp
async def get_bitcoin_price():
    """Obtém o preço atual do Bitcoin na Coinbase."""
    url = 'https://api.coinbase.com/v2/prices/spot?currency=USD'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Levanta erro para falhas de status da requisição
                data = await response.json()  # Espera pela resposta JSON assíncrona
                price = data['data']['amount']
                return float(price)  # Certifica-se de retornar o preço como float
    except aiohttp.ClientError as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

# Função para inserir dados no banco de dados DuckDB
def insert_bitcoin_price(price):
    if price is None:
        print("Preço inválido, não inserindo no banco.")
        return
    
    conn = duckdb.connect('bitcoin_prices.duckdb')

    # Inserir o preço do Bitcoin com timestamp atual
    timestamp = datetime.now()
    
    # Verifica se o valor de 'price' e 'timestamp' são válidos
    if price is not None and timestamp is not None:
        conn.execute('''
        INSERT INTO bitcoin_prices (price, timestamp)
        VALUES (?, ?)
        ''', (price, timestamp))
        print(f"Preço do Bitcoin: ${price} salvo com sucesso.")
    else:
        print("Erro: Preço ou Timestamp inválido.")

    conn.close()

# Função para gerar os registros a cada 10 segundos de forma assíncrona
async def generate_bitcoin_prices():
    while True:
        price = await get_bitcoin_price()
        if price:
            insert_bitcoin_price(price)
        else:
            print("Não foi possível obter o preço do Bitcoin.")
        
        await asyncio.sleep(10)  # Espera 10 segundos assíncronamente antes de fazer a próxima requisição

# Função principal para criar o banco de dados e iniciar o loop assíncrono
async def main():
    create_database()  # Criar o banco de dados no início
    await generate_bitcoin_prices()  # Começar a gerar os registros de forma assíncrona

# Rodando o script principal
if __name__ == "__main__":
    asyncio.run(main())  # Usa asyncio.run para executar o main assíncrono
