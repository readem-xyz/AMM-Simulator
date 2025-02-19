import asyncio
from typing import List
from .client import Client
from .consts import *
from codedict import codes


class TradeAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, test=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, test)

    async def take_spot_order(self, instId, side, order_type, size, price='', tgtCcy='', client_oid='') -> dict:
        """币币下单：POST /api/v5/trade/order\n
        body{"instId":"BTC-USDT","tdMode":"cash","ccy":"USDT","clOrdId":"b15","side":"buy","ordType":"limit",
        "px":"2.15","sz":"2"}

        :param instId: 产品ID
        :param side: buy：买 sell：卖
        :param order_type: market：市价单 limit：限价单 post_only：只做maker单 fok：全部成交或立即取消 ioc：立即成交并取消剩余
        :param size: 委托数量
        :param price: 委托价格
        :param tgtCcy: 市价单委托数量的类型 base_ccy: 交易货币 ；quote_ccy：计价货币
        :param client_oid: 客户自定义订单ID
        """
        params = dict(instId=instId, tdMode='cash', side=side, ordType=order_type, sz=size, px=price, tgtCcy=tgtCcy,
                      clOrdId=client_oid)
        order = await self._request_with_params(POST, TRADE_ORDER, params)
        if order['code'] == '0':
            return order['data'][0]
        else:
            return dict(ordId='-1', code=order['data'][0]['sCode'], msg=codes[order['data'][0]['sCode']])

    async def take_margin_order(self, instId, side, order_type, size, price='', client_oid='', reduceOnly=False) -> dict:
        """币币杠杆下单：POST /api/v5/trade/order\n
        body{"instId":"BTC-USDT","tdMode":"cross","ccy":"USDT","clOrdId":"b15","side":"buy","ordType":"limit",
        "px":"2.15","sz":"2"}

        :param instId: 产品ID
        :param side: buy：买 sell：卖
        :param order_type: market：市价单 limit：限价单 post_only：只做maker单 fok：全部成交或立即取消 ioc：立即成交并取消剩余
        :param size: 委托数量
        :param price: 委托价格
        :param client_oid: 客户自定义订单ID
        :param reduceOnly: 只减仓
        """
        params = dict(instId=instId, tdMode='cross', ccy='USDT', side=side, ordType=order_type, sz=size, px=price,
                      clOrdId=client_oid, reduceOnly=reduceOnly)
        order = await self._request_with_params(POST, TRADE_ORDER, params)
        if order['code'] == '0':
            return order['data'][0]
        else:
            return dict(ordId='-1', code=order['data'][0]['sCode'], msg=codes[order['data'][0]['sCode']])

    async def take_swap_order(self, instId, side, order_type, size, price='', client_oid='', reduceOnly=False) -> dict:
        """合约下单: POST /api/v5/trade/order\n
        body{"instId":"BTC-USDT-SWAP","tdMode":"isolated","ccy":"USDT","clOrdId":"b15","side":"buy","ordType":"limit",
        "px":"2.15","sz":"2"}

        :param instId: 产品ID
        :param side: buy：买 sell：卖
        :param order_type: market：市价单 limit：限价单 post_only：只做maker单 fok：全部成交或立即取消 ioc：立即成交并取消剩余
        :param size: 委托数量
        :param price: 委托价格
        :param client_oid: 客户自定义订单ID
        :param reduceOnly: 只减仓
        """
        params = dict(instId=instId, tdMode='isolated', ccy='USDT', side=side, ordType=order_type, sz=size, px=price,
                      clOrdId=client_oid, reduceOnly=reduceOnly)
        order = await self._request_with_params(POST, TRADE_ORDER, params)
        if order['code'] == '0':
            return order['data'][0]
        else:
            return dict(ordId='-1', code=order['data'][0]['sCode'], msg=codes[order['data'][0]['sCode']])

    async def batch_order(self, orders: List[dict]) -> List[dict]:
        """每次最多可以批量提交20个新订单。请求参数应该按数组格式传递。\n
        POST /api/v5/trade/batch-orders
        """
        # :param instId: 产品ID
        # :param tdMode: 交易模式 保证金模式：isolated：逐仓 ；cross：全仓 非保证金模式：cash：非保证金
        # :param side: buy：买 sell：卖
        # :param ordType: market：市价单 limit：限价单 post_only：只做maker单 fok：全部成交或立即取消 ioc：立即成交并取消剩余
        # :param sz: 委托数量
        # :param px: 委托价格
        # :param tgtCcy: 市价单委托数量的类型 base_ccy: 交易货币 ；quote_ccy：计价货币
        # :param clOrdId: 客户自定义订单ID
        # :param reduceOnly: 只减仓
        assert len(orders) <= 300
        for order in orders:
            assert 'instId' in order
            assert 'tdMode' in order
            assert 'side' in order
            assert 'ordType' in order
            assert 'sz' in order
        n = len(orders) // 20 + 1
        batches = []
        for i in range(n):
            if i < n - 1:
                batch = self._request_with_params(POST, BATCH_ORDER, orders[i * 20:(i + 1) * 20])
            else:
                if i * 20 < len(orders):
                    batch = self._request_with_params(POST, BATCH_ORDER, orders[i * 20:])
                else:
                    break
            batches.append(batch)
        # batches = await asyncio.gather(*batches)
        res = []
        for batch in batches:
            batch = await batch
            await asyncio.sleep(2)
            res.append(batch)
        orders = []
        for batch in res:
            assert batch['code'] == '0', f"{BATCH_ORDER}, msg={codes[batch['code']]}"
            # if batch['code'] != '0':
            #     for order in batch['data']:
            #         print(order)
            orders.extend(batch['data'])
        return orders

    async def get_order_info(self, instId, order_id='', client_oid='') -> dict:
        """获取订单信息\n
        GET /api/v5/trade/order?ordId=2510789768709120&instId=BTC-USDT

        :param instId: 产品ID
        :param order_id: 订单ID
        :param client_oid: 用户自定义ID
        """
        assert order_id or client_oid
        params = dict(ordId=order_id, instId=instId) if order_id else dict(clOrdId=client_oid, instId=instId)
        res = await self._request_with_params(GET, TRADE_ORDER, params)
        assert res['code'] == '0', f"{TRADE_ORDER}, msg={codes[res['code']]}"
        return res['data'][0]

    async def cancel_order(self, instId, order_id='', client_oid='') -> dict:
        """撤销之前下的未完成订单\n
        POST /api/v5/trade/cancel-order

        :param instId: 产品ID
        :param order_id: 订单ID
        :param client_oid: 用户自定义ID
        """
        assert order_id or client_oid
        params = dict(ordId=order_id, instId=instId) if order_id else dict(clOrdId=client_oid, instId=instId)
        order = await self._request_with_params(POST, CANCEL_ORDER, params)
        if order['code'] == '0':
            return order['data'][0]
        else:
            return dict(ordId='-1', code=order['data'][0]['sCode'], msg=codes[order['data'][0]['sCode']])

    async def batch_cancel(self, orders: List[dict]) -> List[dict]:
        """撤销未完成的订单，每次最多可以撤销20个订单。请求参数应该按数组格式传递。\n
        POST /api/v5/trade/cancel-batch-orders
        """
        assert len(orders) <= 300
        for order in orders:
            assert 'instId' in order
            assert 'ordId' in order or 'clOrdId' in order
        n = len(orders) // 20 + 1
        batches = []
        for i in range(n):
            if i < n - 1:
                batch = self._request_with_params(POST, BATCH_CANCEL, orders[i * 20:(i + 1) * 20])
            else:
                if i * 20 < len(orders):
                    batch = self._request_with_params(POST, BATCH_CANCEL, orders[i * 20:])
                else:
                    break
            batches.append(batch)
        # batches = await asyncio.gather(*batches)
        res = []
        for batch in batches:
            batch = await batch
            await asyncio.sleep(2)
            res.append(batch)
        orders = []
        for batch in res:
            assert batch['code'] == '0', f"{BATCH_CANCEL}, msg={codes[batch['code']]}"
            orders.extend(batch['data'])
        return orders

    async def pending_order(self, instType='', uly='', instId='', ordType='', state='') -> List[dict]:
        """获取当前账户下所有未成交订单信息\n
        GET /api/v5/trade/orders-pending

        :param instType: 产品类型 SPOT：币币 MARGIN：币币杠杆 SWAP：永续合约 FUTURES：交割合约 OPTION：期权
        :param uly: 标的指数
        :param instId: 产品ID
        :param ordType: 订单类型 market：市价单 limit：限价单 post_only：只做maker单 fok：全部成交或立即取消 ioc：立即成交并取消剩余
                        optimal_limit_ioc：市价委托立即成交并取消剩余（仅适用交割、永续）
        :param state: 订单状态 live：等待成交 partially_filled：部分成交
        :param after: 请求此ID之前（更旧的数据）的分页内容，传的值为对应接口的ordId
        :param before: 请求此ID之后（更新的数据）的分页内容，传的值为对应接口的ordId
        :param limit: 返回结果的数量，默认100条
        """
        params = dict(instType=instType, uly=uly, instId=instId, ordType=ordType, state=state)
        temp = await self._request_with_params(GET, PENDING_ORDER, params)
        assert temp['code'] == '0', f"{PENDING_ORDER}, msg={codes[temp['code']]}"
        res = temp['data']
        while len(temp) == 100:
            params = dict(instType=instType, uly=uly, instId=instId, ordType=ordType, state=state,
                          after=temp[100 - 1]['ordId'])
            temp = await self._request_with_params(GET, PENDING_ORDER, params)
            assert temp['code'] == '0', f"{PENDING_ORDER}, msg={codes[temp['code']]}"
            res.extend(temp['data'])
        return res
