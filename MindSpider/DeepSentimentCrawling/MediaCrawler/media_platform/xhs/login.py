# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


import asyncio
import functools
import sys
import time
from typing import Optional

from DrissionPage import ChromiumPage, ChromiumOptions

import config
from base.base_crawler import AbstractLogin
from cache.cache_factory import CacheFactory
from tools import utils


class XiaoHongShuLogin(AbstractLogin):
    """基于 DrissionPage 的小红书登录类"""

    def __init__(
        self,
        login_type: str,
        page: ChromiumPage,
        login_phone: Optional[str] = "",
        cookie_str: str = ""
    ):
        config.LOGIN_TYPE = login_type
        self.page = page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    def check_login_state(self, no_logged_in_session: str, max_wait: int = 600) -> bool:
        """
        检查登录状态
        Args:
            no_logged_in_session: 未登录时的 session
            max_wait: 最大等待时间（秒）
        Returns:
            登录成功返回 True，否则返回 False
        """
        wait_time = 0
        while wait_time < max_wait:
            # 检查是否出现验证码
            if "请通过验证" in self.page.html:
                utils.logger.info("[XiaoHongShuLogin.check_login_state] 登录过程中出现验证码，请手动验证")

            # 获取当前 cookies
            current_cookies = self.page.cookies(all_domains=True, all_info=True)
            cookie_dict = {cookie['name']: cookie['value'] for cookie in current_cookies}
            current_web_session = cookie_dict.get("web_session")
            
            if current_web_session and current_web_session != no_logged_in_session:
                utils.logger.info("[XiaoHongShuLogin.check_login_state] 登录成功！")
                return True
            
            time.sleep(1)
            wait_time += 1
        
        return False

    async def begin(self):
        """开始登录小红书"""
        utils.logger.info("[XiaoHongShuLogin.begin] Begin login xiaohongshu ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[XiaoHongShuLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookies ...")

    async def login_by_mobile(self):
        """手机号登录"""
        utils.logger.info("[XiaoHongShuLogin.login_by_mobile] Begin login xiaohongshu by mobile ...")
        await asyncio.sleep(1)
        
        try:
            # 尝试点击登录按钮
            login_button = self.page.ele("xpath://*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button", timeout=5)
            if login_button:
                login_button.click()
                await asyncio.sleep(1)
            
            # 切换到手机登录
            other_method_btn = self.page.ele("xpath://div[@class='login-container']//div[@class='other-method']/div[1]", timeout=5)
            if other_method_btn:
                other_method_btn.click()
        except Exception as e:
            utils.logger.info("[XiaoHongShuLogin.login_by_mobile] have not found mobile button icon and keep going ...")

        await asyncio.sleep(1)
        
        # 输入手机号
        phone_input = self.page.ele("css:label.phone > input")
        phone_input.input(self.login_phone)
        await asyncio.sleep(0.5)

        # 发送验证码
        send_btn = self.page.ele("css:label.auth-code > span")
        send_btn.click()
        
        sms_code_input = self.page.ele("css:label.auth-code > input")
        submit_btn = self.page.ele("css:div.input-container > button")
        
        cache_client = CacheFactory.create_cache(config.CACHE_TYPE_MEMORY)
        max_get_sms_code_time = 60 * 2  # 最长获取验证码的时间为2分钟
        no_logged_in_session = ""
        
        while max_get_sms_code_time > 0:
            utils.logger.info(f"[XiaoHongShuLogin.login_by_mobile] get sms code from redis remaining time {max_get_sms_code_time}s ...")
            await asyncio.sleep(1)
            sms_code_key = f"xhs_{self.login_phone}"
            sms_code_value = cache_client.get(sms_code_key)
            if not sms_code_value:
                max_get_sms_code_time -= 1
                continue

            # 获取当前 session
            current_cookies = self.page.cookies(all_domains=True, all_info=True)
            cookie_dict = {cookie['name']: cookie['value'] for cookie in current_cookies}
            no_logged_in_session = cookie_dict.get("web_session", "")

            # 输入验证码
            sms_code_input.input(sms_code_value.decode())
            await asyncio.sleep(0.5)
            
            # 同意隐私协议
            agree_privacy = self.page.ele("xpath://div[@class='agreements']//*[local-name()='svg']")
            if agree_privacy:
                agree_privacy.click()
            await asyncio.sleep(0.5)

            # 点击登录
            submit_btn.click()
            break

        # 检查登录状态
        if not self.check_login_state(no_logged_in_session):
            utils.logger.info("[XiaoHongShuLogin.login_by_mobile] Login xiaohongshu failed by mobile login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[XiaoHongShuLogin.login_by_mobile] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_qrcode(self):
        """二维码登录"""
        utils.logger.info("[XiaoHongShuLogin.login_by_qrcode] Begin login xiaohongshu by qrcode ...")
        
        # 查找二维码
        qrcode_img = self.page.ele("xpath://img[@class='qrcode-img']", timeout=5)
        
        if not qrcode_img:
            utils.logger.info("[XiaoHongShuLogin.login_by_qrcode] login failed , have not found qrcode please check ....")
            # 尝试点击登录按钮
            await asyncio.sleep(0.5)
            login_button = self.page.ele("xpath://*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button", timeout=5)
            if login_button:
                login_button.click()
                qrcode_img = self.page.ele("xpath://img[@class='qrcode-img']", timeout=5)
            
            if not qrcode_img:
                utils.logger.error("[XiaoHongShuLogin.login_by_qrcode] Still cannot find qrcode, exiting...")
                sys.exit()

        # 获取二维码图片的 base64
        base64_qrcode_img = qrcode_img.attr('src')
        if base64_qrcode_img and base64_qrcode_img.startswith('data:image'):
            base64_qrcode_img = base64_qrcode_img.split(',')[1]

        # 获取当前 session
        current_cookies = self.page.cookies(all_domains=True, all_info=True)
        cookie_dict = {cookie['name']: cookie['value'] for cookie in current_cookies}
        no_logged_in_session = cookie_dict.get("web_session", "")

        # 显示二维码
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[XiaoHongShuLogin.login_by_qrcode] waiting for scan code login, remaining time is 120s")
        
        # 检查登录状态（最多等待120秒）
        if not self.check_login_state(no_logged_in_session, max_wait=120):
            utils.logger.info("[XiaoHongShuLogin.login_by_qrcode] Login xiaohongshu failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[XiaoHongShuLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_cookies(self):
        """Cookie 登录"""
        utils.logger.info("[XiaoHongShuLogin.login_by_cookies] Begin login xiaohongshu by cookie ...")
        
        cookie_dict = utils.convert_str_cookie_to_dict(self.cookie_str)
        for key, value in cookie_dict.items():
            if key != "web_session":  # only set web_session cookie attr
                continue
            
            # DrissionPage 设置 cookie 的方式
            self.page.set.cookies([(key, value, {'domain': '.xiaohongshu.com'})])
        
        # 刷新页面使 cookie 生效
        self.page.refresh()
        await asyncio.sleep(2)
        
        utils.logger.info("[XiaoHongShuLogin.login_by_cookies] Cookie login completed")
