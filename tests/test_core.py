#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：NameProcessor / URLCleaner / DirectChecker.is_known_direct
覆盖核心纯函数，防止回归
"""

import unittest
import sys
import os

# 确保能导入 iptv_apex 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iptv_apex.utils.name import NameProcessor
from iptv_apex.utils.url import URLCleaner
from iptv_apex.config import Config


class TestNameProcessor(unittest.TestCase):
    """NameProcessor 测试"""

    @classmethod
    def setUpClass(cls):
        """加载配置，初始化分类规则"""
        Config.load_from_file()
        Config.init_compiled_rules()

    def test_simplify_traditional(self):
        """繁体转简体"""
        self.assertEqual(NameProcessor.simplify("翡翠台"), "翡翠台")
        self.assertEqual(NameProcessor.simplify("鳳凰衛視"), "凤凰卫视")
        self.assertEqual(NameProcessor.simplify("臺灣"), "台湾")

    def test_normalize_cctv(self):
        """CCTV 名称规范化"""
        self.assertEqual(NameProcessor.normalize("CCTV1"), "CCTV-1")
        self.assertEqual(NameProcessor.normalize("CCTV-1"), "CCTV-1")
        self.assertEqual(NameProcessor.normalize("CCTV5+"), "CCTV-5+")
        self.assertEqual(NameProcessor.normalize("CCTV13新闻"), "CCTV-13")

    def test_normalize_cctv_aliases(self):
        """CCTV 别名规范化"""
        self.assertEqual(NameProcessor.normalize("中央一台"), "CCTV-1")
        self.assertEqual(NameProcessor.normalize("央视五套"), "CCTV-5")
        self.assertEqual(NameProcessor.normalize("综合频道"), "CCTV-1")

    def test_normalize_satellite(self):
        """卫视名称规范化"""
        self.assertEqual(NameProcessor.normalize("湖南卫视高清"), "湖南卫视")
        self.assertEqual(NameProcessor.normalize("浙江卫视超清"), "浙江卫视")

    def test_normalize_hk(self):
        """港澳台频道规范化"""
        self.assertEqual(NameProcessor.normalize("翡翠台"), "翡翠")
        self.assertEqual(NameProcessor.normalize("凤凰卫视中文"), "凤凰中文")

    def test_classify_cctv(self):
        """CCTV 分类优先"""
        self.assertEqual(NameProcessor.classify("CCTV-1"), "央视频道")
        self.assertEqual(NameProcessor.classify("CCTV-5体育"), "央视频道")
        self.assertEqual(NameProcessor.classify("CCTV-13新闻"), "央视频道")

    def test_classify_satellite(self):
        """卫视频道分类"""
        self.assertEqual(NameProcessor.classify("湖南卫视"), "卫视频道")
        self.assertEqual(NameProcessor.classify("浙江卫视"), "卫视频道")

    def test_classify_news(self):
        """新闻资讯分类"""
        self.assertEqual(NameProcessor.classify("CCTV-13"), "央视频道")  # CCTV 优先
        self.assertEqual(NameProcessor.classify("新闻资讯"), "新闻资讯")

    def test_classify_sports(self):
        """体育赛事分类"""
        self.assertEqual(NameProcessor.classify("CCTV-5"), "央视频道")  # CCTV 优先
        self.assertEqual(NameProcessor.classify("体育赛事"), "体育赛事")

    def test_classify_kids(self):
        """少儿动漫分类"""
        self.assertEqual(NameProcessor.classify("动画"), "少儿动漫")
        self.assertEqual(NameProcessor.classify("动画频道"), "少儿动漫")

    def test_classify_other(self):
        """未分类"""
        self.assertEqual(NameProcessor.classify("未知频道"), "其他频道")
        self.assertEqual(NameProcessor.classify(""), "其他频道")

    def test_is_blacklisted(self):
        """黑名单检测"""
        self.assertTrue(NameProcessor.is_blacklisted("购物频道"))
        self.assertTrue(NameProcessor.is_blacklisted("测试源"))
        self.assertTrue(NameProcessor.is_blacklisted("备用源"))
        self.assertFalse(NameProcessor.is_blacklisted("CCTV-1"))

    def test_is_overseas(self):
        """境外频道检测"""
        self.assertTrue(NameProcessor.is_overseas("TVB翡翠台"))
        self.assertTrue(NameProcessor.is_overseas("凤凰卫视"))
        self.assertTrue(NameProcessor.is_overseas("CNN"))
        self.assertFalse(NameProcessor.is_overseas("CCTV-1"))
        self.assertFalse(NameProcessor.is_overseas("湖南卫视"))

    def test_clean_name(self):
        """噪音清洗"""
        self.assertEqual(NameProcessor.clean_name("CCTV-1(高清)"), "CCTV-1")
        self.assertEqual(NameProcessor.clean_name("湖南卫视 HD"), "湖南卫视")
        self.assertEqual(NameProcessor.clean_name("【测试】频道"), "频道")

    def test_get_display_name_cctv(self):
        """CCTV 显示名称格式化"""
        self.assertEqual(NameProcessor.get_display_name("CCTV1"), "CCTV-1综合")
        self.assertEqual(NameProcessor.get_display_name("CCTV-5"), "CCTV-5")  # 无后缀时不加
        self.assertEqual(NameProcessor.get_display_name("CCTV5+体育"), "CCTV-5+体育")
        self.assertEqual(NameProcessor.get_display_name("CCTV13新闻"), "CCTV-13新闻")


class TestURLCleaner(unittest.TestCase):
    """URLCleaner 测试"""

    def test_fingerprint_strips_params(self):
        """URL 指纹去除参数"""
        fp1 = URLCleaner.get_fingerprint("http://example.com/live/1?token=abc")
        fp2 = URLCleaner.get_fingerprint("http://example.com/live/1?token=xyz")
        self.assertEqual(fp1, fp2)

    def test_fingerprint_different_path(self):
        """不同路径指纹不同"""
        fp1 = URLCleaner.get_fingerprint("http://example.com/live/1")
        fp2 = URLCleaner.get_fingerprint("http://example.com/live/2")
        self.assertNotEqual(fp1, fp2)

    def test_fingerprint_case_insensitive(self):
        """域名大小写不敏感"""
        fp1 = URLCleaner.get_fingerprint("http://EXAMPLE.com/live/1")
        fp2 = URLCleaner.get_fingerprint("http://example.com/live/1")
        self.assertEqual(fp1, fp2)

    def test_filter_private_ip(self):
        """内网 IP 过滤"""
        self.assertTrue(URLCleaner.filter_private_ip("http://192.168.1.1/live"))
        self.assertTrue(URLCleaner.filter_private_ip("http://10.0.0.1/live"))
        self.assertTrue(URLCleaner.filter_private_ip("http://127.0.0.1/live"))
        self.assertFalse(URLCleaner.filter_private_ip("http://8.8.8.8/live"))

    def test_vod_domain(self):
        """点播域名过滤"""
        Config.VOD_DOMAINS = {"douyin.com", "kuaishou.com", "goodiptv.club/douyu"}
        self.assertTrue(URLCleaner.is_vod_domain("http://live.douyin.com/123"))
        self.assertTrue(URLCleaner.is_vod_domain("http://goodiptv.club/douyu/123"))
        self.assertFalse(URLCleaner.is_vod_domain("http://live.example.com/123"))

    def test_get_hostname(self):
        """主机名提取"""
        self.assertEqual(URLCleaner._get_hostname("http://example.com/path"), "example.com")
        self.assertEqual(URLCleaner._get_hostname("http://example.com:8080/path"), "example.com")


class TestDirectChecker(unittest.TestCase):
    """DirectChecker.is_known_direct 测试"""

    def setUp(self):
        from iptv_apex.checker.direct import DirectChecker
        self.checker = DirectChecker()

    def test_known_cdn(self):
        """已知 CDN 直通"""
        self.assertTrue(self.checker.is_known_direct("http://live.264788.com/stream"))
        self.assertTrue(self.checker.is_known_direct("http://goodiptv.club/stream"))
        self.assertTrue(self.checker.is_known_direct("http://cdn.example.com/stream"))  # cdn. 后缀匹配
        self.assertTrue(self.checker.is_known_direct("http://cdn8.example.com/stream"))

    def test_ipv6_cn_operators(self):
        """国内运营商 IPv6 直通"""
        self.assertTrue(self.checker.is_known_direct("http://[2409:8087:1234::1]/stream"))
        self.assertTrue(self.checker.is_known_direct("http://[2408:8000:1234::1]/stream"))
        self.assertTrue(self.checker.is_known_direct("http://[240e:600:1234::1]/stream"))

    def test_unknown_domain(self):
        """未知域名不直通"""
        self.assertFalse(self.checker.is_known_direct("http://unknown.example.com/stream"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
