import os
import json
from dotenv import load_dotenv
from datetime import date, datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
# import socks

try:
    os.mkdir("data") 
except OSError as error: 
    print(error)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input("Enter the code: "))
        except SessionPasswordNeededError:
            await client.sign_in(password=input("Password: "))

    await client.get_me()

    user_input_channel = input("Enter Telegram URL: ")
    file_name = user_input_channel.split("/")[-1]
    print(f"Channel: {file_name}")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 500
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    while len(all_messages) < limit: #my_channel:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(
            GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open(
        os.path.dirname(os.path.abspath(__file__)) + f"/data/channel_{file_name}.json", "w"
    ) as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)

# Read .env
load_dotenv()
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
username = os.getenv("username")
phone = os.getenv("phone")
proxy_address = os.getenv("proxy_address")
proxy_port = os.getenv("proxy_port")

# proxy = (socks.SOCKS5, proxy_address, proxy_port)

# Create the client and connect
client = TelegramClient(username, api_id, api_hash) # proxy=proxy

with client:
    print(client)
    client.loop.run_until_complete(main(phone))