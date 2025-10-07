import logging
import threading

from global_def import *
import asyncio
import signal
from typing import Optional, Tuple


# ---------------- TCP Server ----------------
class TCPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 55688, parser = None):
        self.host = host
        self.port = port
        self._server: Optional[asyncio.base_events.Server] = None
        self._serve_task: Optional[asyncio.Task] = None
        self.parser = parser

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        log.debug("[TCP] + Connection from %s", addr)
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                msg = data.decode(errors="ignore")
                log.debug("[TCP]   Received: %s from %s", msg, addr)
                writer.write(f"{msg};OK".encode())
                await writer.drain()
                if self.parser is not None:
                    asyncio.create_task(self.parser(data, addr))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.debug("[TCP] ! Error with %s", addr)
        finally:
            log.debug("[TCP] ! Close %s", addr)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def start(self):
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port, reuse_address=True)
        sock = self._server.sockets[0].getsockname() if self._server.sockets else (self.host, self.port)
        log.debug("[TCP]   Serving on %s",sock)
        self._serve_task = asyncio.create_task(self._server.serve_forever())

    async def stop(self):
        if self._server is not None:
            log.debug("[TCP]   Shutting down...")
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        if self._serve_task:
            self._serve_task.cancel()
            try:
                await self._serve_task
            except asyncio.CancelledError:
                pass
            self._serve_task = None


