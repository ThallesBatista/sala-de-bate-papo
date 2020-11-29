import asyncio
import json # Biblioteca adicional para lidar com eventos em formato json
import websockets

CONNECTIONS = set()
NAMES = set()
CONNECTION_NAME = dict()

# As mensagens enviadas possuem um campo 'type' um campo 'message',
# a intenção seria que o cliente trocasse as cores da mensagem de acordo
# com o tipo, mas a funcionalidade ainda não foi implementada

def private_message_event(message, sender):
    return json.dumps({"type": "PRIVATE", "message": "%s (private) >> %s"%(sender, message)})

def public_message_event(message, sender):
    return json.dumps({"type": "PUBLIC", "message": "%s >> %s"%(sender, message)})

def user_out_event(name):
    message = "%s saiu da sala."%name
    return json.dumps({"type": "SYSTEM", "message": message})

def user_in_event(name):
    message = "%s entrou na sala."%name
    return json.dumps({"type": "SYSTEM", "message": message})

def greetings_message():
    message = "Bem vindo ao servidor de chat escrito em Python com asyncio e WebSockets. Qual o seu nome?"
    return json.dumps({"type": "SYSTEM", "message": message})

def retry_name_message():
    message = "Este nome já pertence a outro usuário, por favor, tente outro."
    return json.dumps({"type": "SYSTEM", "message": message})

async def notify_private_message(websocket, message, receiver):
    if CONNECTIONS:  # asyncio.wait doesn't accept an empty list
        message = private_message_event(message, CONNECTION_NAME[websocket])
        
        receiver_connection = None
        for conn, name in CONNECTION_NAME.items():
            if name == receiver: 
                receiver_connection = conn
                break
        
        if receiver_connection: await receiver_connection.send(message)

async def notify_public_message(websocket, message):
    if CONNECTIONS:  # asyncio.wait doesn't accept an empty list
        message = public_message_event(message, CONNECTION_NAME[websocket])
        for user in CONNECTIONS:
            if user != websocket: await user.send(message)

async def notify_user_in(websocket, name):
    if CONNECTIONS:  # asyncio.wait doesn't accept an empty list
        message = user_in_event(name)
        for user in CONNECTIONS:
            if user != websocket: await user.send(message)

async def notify_new_user(websocket):
    message = greetings_message()
    await websocket.send(message)

async def notify_new_user_retry(websocket):
    message = retry_name_message()
    await websocket.send(message)

async def notify_user_out(websocket):
    if CONNECTIONS:  # asyncio.wait doesn't accept an empty list
        message = user_out_event(CONNECTION_NAME[websocket])
        for user in CONNECTIONS:
            if user != websocket: await user.send(message)

async def register(websocket):
    await notify_new_user(websocket)
    aux = await websocket.recv()
    name = json.loads(aux)["message"]

    valid_name = True
    if (name in NAMES): valid_name = False

    while (not valid_name):
        await notify_new_user_retry(websocket)
        aux = await websocket.recv()
        name = json.loads(aux)["message"]
        if (name not in NAMES): valid_name = True

    CONNECTIONS.add(websocket)
    NAMES.add(name)
    CONNECTION_NAME[websocket] = name
    await notify_user_in(websocket, name)

async def unregister(websocket):
    CONNECTIONS.remove(websocket)
    NAMES.remove(CONNECTION_NAME[websocket])
    await notify_user_out(websocket)


async def main(websocket, path):
    await register(websocket)
    try:
        async for message in websocket: # Consumer
            data = json.loads(message)
            if data["action"] == "public_message":
                await notify_public_message(websocket,data['message'])
            elif data["action"] == "private_message":
                await notify_private_message(websocket,data['message'],data['receiver'])
    finally:
        await unregister(websocket)


start_server = websockets.serve(main, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
