import asyncio
import socket
import db


class Server:
    def __init__(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.loop = asyncio.new_event_loop()
        self.users = []

    def complete(self):
        self.socket.bind(('localhost', 8080))
        self.socket.listen(10)
        self.socket.setblocking(False)

        database = db.Database()

        database.createEntities()
        database.closeDatabase()

        print("Server has started!")

    async def sendText(self, data=None, socketSent=None):
        for user in self.users:
            if user != socketSent and data:
                await self.loop.sock_sendall(user, data)

    async def getUser(self, gottenSocket=None):
        if not gottenSocket:
            print("Invalid socket")
            return
        while True:
            try:
                data = await self.loop.sock_recv(gottenSocket, 1024)
                await self.sendText(data, gottenSocket)
            except ConnectionResetError:
                print("User was removed")
                self.users.remove(gottenSocket)
                return

    async def acceptSocket(self):
        while True:
            username, data = await self.loop.sock_accept(self.socket)
            print(f"{data} is connected!")
            self.users.append(username)
            self.loop.create_task(self.getUser(username))

    async def main(self):
        await self.loop.create_task(self.acceptSocket())

    def start(self):
        self.loop.run_until_complete(self.main())


if __name__ == '__main__':
    server = Server()
    server.complete()
    server.start()
