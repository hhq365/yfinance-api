import unittest
from unittest.mock import patch

from fastapi import Response

from routes.etf_routes import list_etfs
from services.etf import get_etfs


class ETFTests(unittest.TestCase):
    @patch("services.etf.yf.screen")
    def test_optional_exact_ticker(self, screen):
        screen.return_value = {"total": 1, "quotes": [{"symbol": "2840.HK"}]}
        list_etfs(Response(), "hk", 1, 100, " 2840.hk ")
        self.assertEqual(screen.call_args.args[0].to_dict(), {
            "operator": "AND", "operands": [
                {"operator": "EQ", "operands": ["region", "hk"]},
                {"operator": "EQ", "operands": ["ticker", "2840.HK"]},
            ],
        })
        for ticker in ("", "   "):
            get_etfs("hk", ticker=ticker)
            self.assertEqual(screen.call_args.args[0].to_dict(), {
                "operator": "EQ", "operands": ["region", "hk"],
            })

    @patch("services.etf.yf.screen")
    def test_region_pagination_and_missing_fields(self, screen):
        screen.return_value = {"total": 3, "quotes": [{"symbol": "2840.HK"}]}
        result = get_etfs("HK", page=2, pagesize=1)
        self.assertEqual(result["region"], "hk")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["pagesize"], 1)
        self.assertTrue(result["hasMore"])
        self.assertIsNone(result["items"][0]["regularMarketPrice"])
        self.assertEqual(screen.call_args.args[0].to_dict()["operands"], ["region", "hk"])
        self.assertEqual(screen.call_args.kwargs["offset"], 1)
        self.assertEqual(screen.call_args.kwargs["size"], 1)

    @patch("services.etf.yf.screen")
    def test_empty_and_last_page(self, screen):
        screen.return_value = {"total": 0, "quotes": []}
        self.assertFalse(get_etfs("hk")["hasMore"])
        screen.return_value = {"total": 2, "quotes": [{"symbol": "2840.HK"}]}
        self.assertFalse(get_etfs("hk", 2, 1)["hasMore"])

    @patch("services.etf.yf.screen")
    def test_invalid_region(self, screen):
        response = Response()
        self.assertEqual(list_etfs(response, "zz", 1, 100, "")["code"], -1)
        self.assertEqual(response.status_code, 422)
        screen.assert_not_called()

    @patch("services.etf.yf.screen")
    def test_upstream_failure(self, screen):
        for payload in [None, {}, {"quotes": [], "total": None}]:
            screen.return_value = payload
            response = Response()
            list_etfs(response, "hk", 1, 100, "")
            self.assertEqual(response.status_code, 502)
        screen.side_effect = RuntimeError("upstream error")
        response = Response()
        list_etfs(response, "hk", 1, 100, "")
        self.assertEqual(response.status_code, 502)
