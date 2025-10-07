import asyncio
import signal
import random

from global_def import *
from tcp_server import TCPServer

async def test_get_set(writer, reader, count: int):
    ''' 第一筆還是送MSG_SPEC_HELLO '''
    if count == 0:
        msg = f"idx:{count};src:mobile;cmd:{MSG_SPEC_HELLO};data:mobile_server_port=8888"
        log.debug(f"[TCP Client] Send: {msg}")
        writer.write(msg.encode())
        await writer.drain()
        data = await reader.read(100)
        log.debug(f"[TCP Client] Received: {data.decode()}")
        await asyncio.sleep(random.uniform(0.01, 5))
    else:
        ''' 然後就一直輪流送 GET_CMD_SYS_Wifi dict內的vale '''
        for k, v in SET_CMD_SYS_Wifi.items():
            log.debug(f"{k}:{v}")
            if v == SYS_SET_WIFI_UAP0_SSID:
                msg = f"idx:{count};src:mobile;cmd:{v};data:GIS-IMX93-MS062"
            elif v == SYS_SET_WIFI_UAP0_PWD:
                msg = f"idx:{count};src:mobile;cmd:{v};data:54098493"
            elif v == SYS_SET_WIFI_UAP0_HW_MODE:
                msg = f"idx:{count};src:mobile;cmd:{v};data:g"
            elif v == SYS_SET_WIFI_UAP0_SSID_PWD:
                msg = f"idx:{count};src:mobile;cmd:{v};data:GIS-IMX93-MS062_54098493"
            # msg = f"idx:{count};src:mobile;cmd:{DEMO_SET_TEST};data:GIS-IMX93-MS062"

            log.debug(f"[TCP Client] Send: {msg}")
            writer.write(msg.encode())
            await writer.drain()
            data = await reader.read(100)
            log.debug(f"[TCP Client] Received: {data.decode()}")
            await asyncio.sleep(random.uniform(0.01, 5))

        '''for k, v in GET_CMD_SYS_Wifi.items():
            log.debug(f"{k}:{v}")
            msg = f"idx:{count};src:mobile;cmd:{v}"

            # msg = f"idx:{count};src:mobile;cmd:{DEMO_SET_TEST};data:GIS-IMX93-MS062"

            log.debug(f"[TCP Client] Send: {msg}")
            writer.write(msg.encode())
            await writer.drain()
            data = await reader.read(100)
            log.debug(f"[TCP Client] Received: {data.decode()}")
            await asyncio.sleep(random.uniform(0.01, 5))'''


# ---------------- TCP ----------------
async def tcp_client():
    reader, writer = await asyncio.open_connection(TARGET_IP, TARGET_TCP_PORT)
    print("[TCP Client] Connected to server")
    count = 0

    while True:
        await test_get_set(writer, reader, count)
        ''' 第一筆還是送MSG_SPEC_HELLO '''
        '''if count == 0:
            msg = f"idx:{count};src:mobile;cmd:{MSG_SPEC_HELLO};data:mobile_server_port=8888"
            log.debug(f"[TCP Client] Send: {msg}")
            writer.write(msg.encode())
            await writer.drain()
            data = await reader.read(100)
            log.debug(f"[TCP Client] Received: {data.decode()}")
            await asyncio.sleep(random.uniform(0.01, 5))
        else:
            
            for k, v in SET_CMD_TEST.items():
                log.debug(f"{k}:{v}")
                msg = f"idx:{count};src:mobile;cmd:{v};data:GIS-IMX93-MS062"

                # msg = f"idx:{count};src:mobile;cmd:{DEMO_SET_TEST};data:GIS-IMX93-MS062"

                log.debug(f"[TCP Client] Send: {msg}")
                writer.write(msg.encode())
                await writer.drain()
                data = await reader.read(100)
                log.debug(f"[TCP Client] Received: {data.decode()}")
                await asyncio.sleep(random.uniform(0.01, 5))'''
        count += 1

    print("[TCP Client] Closing connection")
    writer.close()
    await writer.wait_closed()

# ---------------- UDP ----------------
class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, messages, on_con_lost):
        self.messages = messages
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport
        for msg in self.messages:
            print(f"[UDP Client] Send: {msg}")
            self.transport.sendto(msg.encode())
        # 可以選擇在最後關閉
        # self.transport.close()

    def datagram_received(self, data, addr):
        print(f"[UDP Client] Received: {data.decode()}")

    def connection_lost(self, exc):
        print("[UDP Client] Connection closed")
        self.on_con_lost.set_result(True)

async def udp_client():
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol([f"Ping {i}" for i in range(3)], on_con_lost),
        remote_addr=(TARGET_IP, 9999)
    )
    try:
        await asyncio.sleep(2)
    finally:
        transport.close()

async def main():
    tcp = TCPServer('0.0.0.0', SELF_TCP_PORT)
    await tcp.start()
    await asyncio.gather(
        tcp_client(),
        # udp_client(),
    )

    # graceful shutdown on SIGINT/SIGTERM
    stop_event = asyncio.Event()

    def _on_signal():
        log.debug("\nMsg Server Signal received, stopping...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _on_signal)
        except NotImplementedError:
            # Windows may not support add_signal_handler for SIGTERM
            pass

    try:
        await stop_event.wait()
    finally:
        await asyncio.gather(*(srv.stop() for srv in (tcp,) if srv), return_exceptions=True)
        log.debug("Msg Server Bye.")

if __name__ == "__main__":
    asyncio.run(main())