from typing import List
from .client import Client
from .consts import *
from .exceptions import *
from codedict import codes
import asyncio


class PublicAPI(Client):

    def __init__(self, use_server_time=False, test=False):
        Client.__init__(self, '', '', '', use_server_time, test)

    async def get_instruments(self, instType: str) -> List[dict]:
        """获取所有可交易产品的信息列表\n
        GET /api/v5/public/instruments?instType=SWAP

        :param instType: SPOT：币币 SWAP：永续合约 FUTURES：交割合约 OPTION：期权
        """
        params = dict(instType=instType)
        res = await self._request_with_params(GET, GET_INSTRUMENTS, params)
        assert res['code'] == '0', f"{GET_INSTRUMENTS}, msg={codes[res['code']]}"
        return res['data']

    async def get_specific_instrument(self, instType, instId, uly='') -> dict:
        """获取单个可交易产品的信息\n
        GET /api/v5/public/instruments?instType=SWAP&instId=BTC-USDT-SWAP

        :param instType: SPOT：币币 SWAP：永续合约 FUTURES：交割合约 OPTION：期权
        :param instId: 产品ID
        :param uly: 合约标的指数，仅适用于交割/永续/期权，期权必填
        """
        if uly:
            assert uly in ('SWAP', 'FUTURES', 'OPTION')
            params = dict(instType=instType, instId=instId, uly=uly)
        else:
            params = dict(instType=instType, instId=instId)
        res = await self._request_with_params(GET, GET_INSTRUMENTS, params)
        if res['code'] == '51001':
            raise OkexRequestException(codes[res['code']])
        return res['data'][0]

    async def get_funding_time(self, instId: str) -> dict:
        """获取当前资金费率\n
        GET /api/v5/public/funding-rate?instId=BTC-USD-SWAP

        :param instId: 产品ID，如 BTC-USD-SWAP
        """
        params = dict(instId=instId)
        res = await self._request_with_params(GET, FUNDING_RATE, params)
        assert res['code'] == '0', f"{FUNDING_RATE}, msg={codes[res['code']]}"
        return res['data'][0]

    async def get_historical_funding_rate(self, instId: str, after='', before='', limit='') -> List[dict]:
        """获取最近3个月的历史资金费率\n
        GET /api/v5/public/funding-rate-history?instId=BTC-USD-SWAP

        :param instId: 产品ID
        :param after: 请求此时间戳之前
        :param before: 请求此时间戳之后
        :param limit: 分页返回的结果集数量，最大为100，不填默认返回100条
        """
        params = dict(instId=instId, after=after, before=before, limit=limit)
        res = await self._request_with_params(GET, FUNDING_RATE_HISTORY, params)
        assert res['code'] == '0', f"{FUNDING_RATE_HISTORY}, msg={codes[res['code']]}"
        return res['data']

    async def get_tickers(self, instType: str, uly='') -> List[dict]:
        """获取所有产品行情信息\n
        GET /api/v5/market/tickers?instType=SWAP

        :param instType: 产品类型，SPOT：币币 SWAP：永续合约 FUTURES：交割合约 OPTION：期权
        :param uly: 标的指数，仅适用于交割/永续/期权
        """
        if uly:
            assert uly in ('SWAP', 'FUTURES', 'OPTION')
            params = dict(instType=instType, uly=uly)
        else:
            params = dict(instType=instType)
        while True:
            try:
                return (await self._request_with_params(GET, GET_TICKERS, params))['data']
            except OkexAPIException:
                await asyncio.sleep(10)

    async def get_specific_ticker(self, instId: str) -> dict:
        """获取单个产品行情信息\n
        GET /api/v5/market/ticker?instId=BTC-USD-SWAP

        :param instId: 产品ID
        """
        params = dict(instId=instId)
        while True:
            try:
                return (await self._request_with_params(GET, GET_TICKER, params))['data'][0]
            except OkexAPIException:
                await asyncio.sleep(10)

    async def get_kline(self, instId: str, bar='4H', after='', before='', limit='') -> List[List]:
        """获取K线数据。K线数据按请求的粒度分组返回，K线数据每个粒度最多可获取最近1440条。\n
        GET /api/v5/market/candles

        :param instId: 产品ID
        :param bar: 时间粒度, [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
        :param after: 请求此时间戳之前
        :param before: 请求此时间戳之后
        :param limit: 分页返回的结果集数量，最大为300，不填默认返回100条
        """
        params = dict(instId=instId, bar=bar, after=after, before=before, limit=limit)
        res = await self._request_with_params(GET, GET_CANDLES, params)
        assert res['code'] == '0', f"{GET_CANDLES}, msg={codes[res['code']]}"
        return res['data']

    async def history_kline(self, instId: str, bar='4H', after='', before='', limit='') -> List[List]:
        """获取最近几年的历史k线数据\n
        GET /api/v5/market/history-candles

        :param instId: 产品ID
        :param bar: 时间粒度, [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
        :param after: 请求此时间戳之前
        :param before: 请求此时间戳之后
        :param limit: 分页返回的结果集数量，最大为100，不填默认返回100条
        """
        params = dict(instId=instId, bar=bar, after=after, before=before, limit=limit)
        res = await self._request_with_params(GET, HISTORY_CANDLES, params)
        assert res['code'] == '0', f"{HISTORY_CANDLES}, msg={codes[res['code']]}"
        return res['data']
