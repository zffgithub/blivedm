import logging

import grpc

import cyber_pb2
import cyber_pb2_grpc
import blivedm
import asyncio

class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    def __init__(self, stub: cyber_pb2_grpc.CyberManagerStub) -> None:
        super().__init__()
        self._stub = stub

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname} say: {message.msg}')
        response = self._stub.RemoteControl(cyber_pb2.Request(cyber_id=2,danmu=f"{message.uname} say: {message.msg}"))
        # print("调用成功: {}!".format(response))

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')

async def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cyber_pb2_grpc.CyberManagerStub(channel)
        
        room_id = 103# 1455691
        # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
        client = blivedm.BLiveClient(room_id, ssl=True)
        handler = MyHandler(stub=stub)
        client.add_handler(handler)
        client.start()
        try:
            # 演示5秒后停止
            await asyncio.sleep(60)
            client.stop()

            await client.join()
        finally:
            await client.stop_and_close()

if __name__ == '__main__':
    logging.basicConfig()
    # run()
    asyncio.get_event_loop().run_until_complete(run())