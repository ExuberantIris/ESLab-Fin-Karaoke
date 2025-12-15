import asyncio
from bleak import BleakClient, BleakScanner
import pygame
from main_window import UpdatePlot, main_loop, add_points

# 16-bit UUIDs expanded to standard BLE format
SERVICE_UUID = "00005012-0000-1000-8000-00805f9b34fb"
CHAR_UUID    = "00003c00-0000-1000-8000-00805f9b34fb"

TARGET_NAME = "BlueNRG"   # Peripheral name

def notification_handler(sender, data):
    """Callback when notification is received."""
    print(f"[NOTIFY] {sender}: {int(data[:2].hex(), 16)}   raw={data[:2]}")
    UpdatePlot(int(data[:2].hex(), 16))


async def find_device():
    """Scan until blueNRG device is found."""
    print("Scanning for blueNRG...")
    devices = await BleakScanner.discover()

    for d in devices:
        if d.name and TARGET_NAME.lower() in d.name.lower():
            print(f"Found device: {d.name}  [{d.address}]")
            return d.address

    raise RuntimeError("blueNRG not found. Make sure it is advertising.")

async def main():
    # 1. scan for device
    asyncio.gather(main_loop(), add_points())

    try:
        address = await find_device()

        # 2. connect
        print(f"Connecting to {address} ...")
        async with BleakClient(address) as client:
            print("Connected:", client.is_connected)

            # 3. start notification on characteristic 0x3C00
            print("Enabling notifications...")
            await client.start_notify(CHAR_UUID, notification_handler)

            print("Listening for notifications. Press Ctrl+C to exit.")
            while True:
                await asyncio.sleep(1)  # keep alive loop
    except Exception as e:
        print(e)
        pygame.quit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"error: {e}")
    finally:
        pygame.quit()