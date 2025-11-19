import asyncio
import websockets
import json
import base64

# Configuration
WS_URL = "ws://localhost:55534/debugger"  # Default PPSSPP WebSocket port
BREAKPOINT_ADDR = 0x08A233C0   # Example: a common default load address for user memory
MEMORY_ADDR = 0x09B20C40       # Memory address to read
READ_LENGTH = 0x20000               # Number of bytes to read

fileout = open('data.cpk','wb')

async def ppsspp_debugger_client():
    async with websockets.connect(WS_URL) as websocket:
        print(f"Connected to PPSSPP debugger at {WS_URL}")

        # 1. Send the initial "version" message as requested by PPSSPP
        #    (See WebSocket/GameSubscriber.cpp in PPSSPP source)
        version_message = {
            "event": "version",
            "version": 1,
            "ticket": "1"
        }
        await websocket.send(json.dumps(version_message))
        print("Sent version message")

        # Wait for and print the response to confirm connection
        response = await websocket.recv()
        print(f"Received: {response}")

        # 2. Set a breakpoint
        #    "HLE" breakpoints are often easier to manage
        breakpoint_message = {
            "event": "cpu.breakpoint.add",
            "address": BREAKPOINT_ADDR,
            "clear": False,
            "ticket": "2"
        }
        await websocket.send(json.dumps(breakpoint_message))
        print(f"Sent breakpoint message for address {hex(BREAKPOINT_ADDR)}")

        # 3. Resume the game (assuming it's paused or stopped)
        resume_message = {
            "event": "cpu.resume",
            "ticket": "3"
        }
        await websocket.send(json.dumps(resume_message))
        print("Sent resume message")

        # 4. Wait for a breakpoint hit event
        print("Waiting for breakpoint hit...")
        startRead = False
        async for message in websocket:
            global MEMORY_ADDR
            data = json.loads(message)
            if data.get("event") == "cpu.stepping" and not startRead:
                print(f"Breakpoint hit at address: {hex(data.get('pc'))}")
                

                read_reg_message = {
                    "event": "cpu.getReg",
                    "name": 'v0',
                    "ticket": "4"
                }
                await websocket.send(json.dumps(read_reg_message))
                read_reg_message = {
                    "event": "cpu.getReg",
                    "name": 'a1',
                    "ticket": "6"
                }
                await websocket.send(json.dumps(read_reg_message))
            elif data.get("event") == "cpu.getReg":
                if(data.get("ticket") == '6'):
                    MEMORY_ADDR = int(data.get("uintValue"))
                if(data.get("uintValue") == 0x20000 or data.get("uintValue") == 0x2000):
                    print(data)
                    read_memory_message = {
                        "event": "memory.read",
                        "address": MEMORY_ADDR,
                        "size": READ_LENGTH,
                        "ticket": "5"
                    }
                    await websocket.send(json.dumps(read_memory_message))
                    startRead = True
                else:
                    await websocket.send(json.dumps(resume_message))
            else:
                if data.get("event") == "memory.read":
                    
                    # The data is base64 encoded; decode it
                    encoded_data = data.get("base64")
                    decoded_data = base64.b64decode(encoded_data)
                    fileout.write(decoded_data)
                    #print(f"Read data (bytes): {decoded_data.hex()}")
                    startRead = False
                    await websocket.send(json.dumps(resume_message))


# Run the client
if __name__ == "__main__":
    try:
        asyncio.run(ppsspp_debugger_client())
    except ConnectionRefusedError:
        print("Connection failed. Is PPSSPP running with the remote debugger enabled?")
    except Exception as e:
        print(f"An error occurred: {e}")
