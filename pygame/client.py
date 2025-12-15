import asyncio
import struct
from bleak import BleakClient, BleakScanner
from main_window import KaraokeGame 

DEVICE_ADDRESS = "F3:9A:AA:F0:53:1B"
#"DF49F975-EDAD-04D0-63CD-75DCDE538AB4" 

CHARACTERISTIC_UUID = "00003c00-0000-1000-8000-00805f9b34fb"
#"00000001-0000-00b0-0000-000000000000" 

game = KaraokeGame()

def notification_handler(sender, data):
    try:
        if len(data) >= 2:
            
            pitch_value = int(data[:2].hex(), 16)
            time = int(data[:1:-1].hex(), 16)

            print(f"[BLE AUDIO] raw={data}  pitch={pitch_value}, time={time}")

            game.update_user_input(float(pitch_value), time=time)

            #simulated_pitch = int.from_bytes(data[0:2], byteorder='little', signed=True)
            #print(f"Received Frequency: {simulated_pitch} Hz")
            #game.update_user_input(float(simulated_pitch))
            
    except Exception as e:
        print(f"error: {e}")

async def run_ble_game():

    # print(f"Currently Connected {DEVICE_ADDRESS}...")
    # devices = await BleakScanner.discover(1)
    # for d in devices:
    #     print(d.name, d.address)

    print(f"Currently Connected {DEVICE_ADDRESS}...")
    
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Have Connected: {client.is_connected}")
        # subscribe
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        
        print("Start Receiving Data...")
        
        try:
            while game.running:
                game.process()
                
                await asyncio.sleep(0.001) 
        except Exception as e:
        # stop notify
            await client.stop_notify(CHARACTERISTIC_UUID)
            raise e

if __name__ == "__main__":
    try:
        asyncio.run(run_ble_game())
    except Exception as e:
        print(f"error: {e}")
    finally:
        game.quit()