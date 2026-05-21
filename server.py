import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# Armazena as conexões ativas
active_clients = {}  # {machine_name: websocket}
admin_connection = None

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    global admin_connection
    await websocket.accept()
    
    # Se for a sua máquina se conectando
    if client_id == "ADMIN":
        admin_connection = websocket
        print("Painel ADM conectado com sucesso!")
    else:
        # Se for um cliente, o client_id será "nome_maquina-setor"
        active_clients[client_id] = websocket
        print(f"Cliente conectado: {client_id}")
        # Avisa o admin que um novo cliente está online
        if admin_connection:
            await admin_connection.send_text(json.dumps({
                "type": "sys_status", 
                "message": f"Dispositivo online: {client_id}"
            }))

    try:
        while True:
            # Aguarda mensagens de texto estruturadas em JSON
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Se o cliente enviou um chamado ou mensagem de chat
            if client_id != "ADMIN":
                if admin_connection:
                    await admin_connection.send_text(json.dumps(message_data))
            # Se você (ADMIN) respondeu no chat para um cliente específico
            else:
                target = message_data.get("target")
                if target in active_clients:
                    await active_clients[target].send_text(json.dumps(message_data))

    except WebSocketDisconnect:
        if client_id == "ADMIN":
            admin_connection = None
            print("Painel ADM desconectado.")
        else:
            if client_id in active_clients:
                del active_clients[client_id]
            print(f"Cliente desconectado: {client_id}")
            if admin_connection:
                await admin_connection.send_text(json.dumps({
                    "type": "sys_status", 
                    "message": f"Dispositivo offline: {client_id}"
                }))

if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor na porta 8000 de todas as interfaces de rede
    uvicorn.run(app, host="0.0.0.0", port=8000)