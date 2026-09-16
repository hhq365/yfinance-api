import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from fastapi import Response

from routes.dexscreener_routes import price
from services import dexscreener as service


class DexScreenerTests(unittest.TestCase):
    def setUp(self):
        service.price_cache.clear()
        self.address = service.settings.dexscreener_token_addresses["bsc"]["USDT"]
        fx = patch("utils.currency._get_frankfurter_usd_hkd", return_value=Decimal("7.8"))
        fx.start()
        self.addCleanup(fx.stop)

    def pair(self, **changes):
        data = {
            "chainId": "bsc", "baseToken": {"address": self.address, "symbol": "USDT"},
            "priceUsd": "0.9994", "liquidity": {"usd": 10000},
            "volume": {"h24": 100}, "pairAddress": "selected",
        }
        data.update(changes)
        return data

    @patch.object(service.requests, "get")
    def test_selection_conversion_and_normalized_cache(self, get):
        get.return_value = Mock(json=Mock(return_value=[
            self.pair(baseToken={"address": "fake", "symbol": "USDT"}, liquidity={"usd": 999999}),
            self.pair(chainId="ethereum"),
            self.pair(priceUsd="NaN"), self.pair(volume={"h24": 0}),
            self.pair(liquidity=None), self.pair(priceUsd="1.2", liquidity={"usd": 50}),
            self.pair(),
        ]))
        result = service.get_dexscreener_price("BSC", "usdt")
        self.assertEqual(result["priceUSD"], 0.9994)
        self.assertAlmostEqual(result["priceHKD"], 7.79532)
        self.assertEqual(result["fxRateSource"], "Frankfurter")
        self.assertEqual(result["pairAddress"], "selected")
        self.assertEqual(result, service.get_dexscreener_price("bsc", "USDT"))
        get.assert_called_once()

    @patch.object(service.requests, "get")
    def test_unknown_symbol_does_not_search_by_name(self, get):
        with self.assertRaises(service.DexScreenerError) as caught:
            service.get_dexscreener_price("bsc", "FAKE")
        self.assertEqual(caught.exception.status_code, 404)
        get.assert_not_called()

    @patch.object(service.requests, "get")
    def test_quote_side_is_not_mispriced_and_errors_are_not_cached(self, get):
        get.return_value = Mock(json=Mock(return_value=[self.pair(
            baseToken={"address": "other"}, quoteToken={"address": self.address}
        )]))
        response = Response()
        self.assertEqual(price(response, "bsc", "USDT")["code"], -1)
        self.assertEqual(response.status_code, 404)
        get.return_value.json.return_value = [self.pair()]
        self.assertEqual(price(Response(), "bsc", "USDT")["code"], 0)
        self.assertEqual(get.call_count, 2)

    @patch.object(service.requests, "get")
    def test_fx_failure_returns_gateway_error(self, get):
        get.return_value = Mock(json=Mock(return_value=[self.pair()]))
        with patch.object(service, "convert_price", return_value=(None, None)):
            response = Response()
            self.assertEqual(price(response, "bsc", "USDT")["code"], -1)
            self.assertEqual(response.status_code, 502)
            self.assertEqual(len(service.price_cache), 0)

    @patch.object(service.requests, "get")
    def test_upstream_failures(self, get):
        for payload in ({}, None, "invalid"):
            get.return_value = Mock(json=Mock(return_value=payload))
            response = Response()
            self.assertEqual(price(response, "bsc", "USDT")["code"], -1)
            self.assertEqual(response.status_code, 502)
        get.side_effect = requests.Timeout()
        response = Response()
        price(response, "bsc", "USDT")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
