import unittest
from unittest.mock import Mock, patch

import requests
from fastapi import Response

from routes.frankfurter_routes import rate
from utils import currency


class FrankfurterRouteTests(unittest.TestCase):
    def setUp(self):
        currency.frankfurterRateCache.clear()

    @patch.object(currency.requests, "get")
    def test_general_pair_normalization_and_cache(self, get):
        get.return_value = Mock(json=Mock(return_value={
            "base": "EUR", "quote": "JPY", "rate": 170.12, "date": "2026-09-16"
        }))
        result = rate(Response(), "eur", "jpy")
        self.assertEqual(result, {"code": 0, "message": "success", "data": {
            "base": "EUR", "quote": "JPY", "rate": 170.12,
            "date": "2026-09-16", "source": "Frankfurter"
        }})
        self.assertEqual(rate(Response(), "EUR", "JPY"), result)
        get.assert_called_once_with("https://api.frankfurter.dev/v2/rate/EUR/JPY", timeout=10)

    @patch.object(currency.requests, "get")
    def test_shared_with_conversion(self, get):
        get.return_value = Mock(json=Mock(return_value={
            "base": "USD", "quote": "HKD", "rate": 7.85, "date": "2026-09-16"
        }))
        rate(Response(), "USD", "HKD")
        currency.get_fx_rate("USD", "HKD")
        self.assertEqual(get.call_count, 1)

    @patch.object(currency.requests, "get")
    def test_upstream_error_statuses_and_recovery(self, get):
        for upstream, expected in [(422, 404), (429, 502), (500, 502)]:
            get.side_effect = requests.HTTPError(response=Mock(status_code=upstream))
            response = Response()
            result = rate(response, "XXX", "HKD")
            self.assertEqual(response.status_code, expected)
            self.assertEqual(result["code"], -1)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(len(currency.frankfurterRateCache), 0)

    @patch.object(currency.requests, "get")
    def test_invalid_date_or_pair_rejected(self, get):
        for data in [
            {"base": "USD", "quote": "HKD", "rate": 7.8},
            {"base": "USD", "quote": "HKD", "rate": 7.8, "date": "bad"},
            {"base": "EUR", "quote": "HKD", "rate": 7.8, "date": "2026-09-16"},
        ]:
            get.return_value = Mock(json=Mock(return_value=data))
            response = Response()
            rate(response, "USD", "HKD")
            self.assertEqual(response.status_code, 502)
