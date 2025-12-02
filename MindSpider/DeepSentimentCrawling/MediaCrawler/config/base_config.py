# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# 基础配置
PLATFORM = "zhihu"  # 平台，xhs | dy | ks | bili | wb | tieba | zhihu
KEYWORDS = "电动自行车新国标,G7,大埔火灾,GitHub趋势,AI换脸,朱征夫,华为新机,iPhone音质,余华,郭炜炜,字节跳动,云南垃圾,贴吧热议,军嫂,经济舱座位,存钱技巧,钓鱼岛,丁少华,卢旺达,荒野求生,打印机,婚检,白百何,AI手机,滨崎步,付辛博,中国男篮,俄军导弹,解限机,西山居,抖音舞蹈,以色列,iPhone,外卖维权,胡歌,肖战,富家女骗钱,蔚来事故,快递业务量,网警,新能源车销量,大白鲨,中国航天,排骨羽绒服,毕导,朴赞郁,爱马仕,海警,山东话,甲型H3N2"  # 关键词搜索配置，以英文逗号分隔
LOGIN_TYPE = "qrcode"  # qrcode or phone or cookie
COOKIES = ""
CRAWLER_TYPE = "search"  # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据)

# ==================== DrissionPage 配置 ====================
# 是否使用 DrissionPage 替代 Playwright（仅支持小红书平台）
# DrissionPage 优势：不基于 webdriver，更难被检测，运行速度更快
# 推荐在遇到反爬虫检测时启用此选项
USE_DRISSION_PAGE = True

# 自定义 DrissionPage 浏览器路径（可选）
# 如果留空则自动检测。若在 WSL/服务器环境运行，请将其设置为浏览器可执行文件的绝对路径
# 若需强制使用 WSL 内已安装的 Chrome，请填写绝对路径
DRISSION_BROWSER_PATH = "/usr/bin/google-chrome-stable"

# 是否连接到已运行的浏览器（CDP 模式，需手动启动带远程调试端口的 Chrome/Edge）
DRISSION_ATTACH_TO_BROWSER = True
DRISSION_REMOTE_DEBUG_HOST = "127.0.0.1"
DRISSION_REMOTE_DEBUG_PORT = 9222

# 是否开启 IP 代理
ENABLE_IP_PROXY = False

# 代理IP池数量
IP_PROXY_POOL_COUNT = 2

# 代理IP提供商名称
IP_PROXY_PROVIDER_NAME = "kuaidaili"  # kuaidaili | wandouhttp

# 设置为True不会打开浏览器（无头浏览器）
# 设置False会打开一个浏览器
# 小红书如果一直扫码登录不通过，打开浏览器手动过一下滑动验证码
# 抖音如果一直提示失败，打开浏览器看下是否扫码登录之后出现了手机号验证，如果出现了手动过一下再试。
HEADLESS = True

# 是否保存登录状态
SAVE_LOGIN_STATE = True

# ==================== CDP (Chrome DevTools Protocol) 配置 ====================
# 是否启用CDP模式 - 使用用户现有的Chrome/Edge浏览器进行爬取，提供更好的反检测能力
# 启用后将自动检测并启动用户的Chrome/Edge浏览器，通过CDP协议进行控制
# 这种方式使用真实的浏览器环境，包括用户的扩展、Cookie和设置，大大降低被检测的风险
ENABLE_CDP_MODE = True

# CDP调试端口，用于与浏览器通信
# 如果端口被占用，系统会自动尝试下一个可用端口
CDP_DEBUG_PORT = 9222

# 自定义浏览器路径（可选）
# 如果为空，系统会自动检测Chrome/Edge的安装路径
# Windows示例: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# macOS示例: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CUSTOM_BROWSER_PATH = ""

# CDP模式下是否启用无头模式
# 注意：即使设置为True，某些反检测功能在无头模式下可能效果不佳
CDP_HEADLESS = False

# 浏览器启动超时时间（秒）
BROWSER_LAUNCH_TIMEOUT = 30

# 是否在程序结束时自动关闭浏览器
# 设置为False可以保持浏览器运行，便于调试
AUTO_CLOSE_BROWSER = True

# 数据保存类型选项配置,支持五种类型：csv、db、json、sqlite、postgresql, 最好保存到DB，有排重的功能。
SAVE_DATA_OPTION = "db"  # csv or db or json or sqlite or postgresql

# 用户浏览器缓存的浏览器文件配置
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

# 爬取开始页数 默认从第一页开始
START_PAGE = 1

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 50

# 并发爬虫数量控制
MAX_CONCURRENCY_NUM = 1

# 是否开启爬媒体模式（包含图片或视频资源），默认不开启爬媒体
ENABLE_GET_MEIDAS = False

# 是否开启爬评论模式, 默认开启爬评论
ENABLE_GET_COMMENTS = True

# 爬取一级评论的数量控制(单视频/帖子)
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 20

# 是否开启爬二级评论模式, 默认不开启爬二级评论
# 老版本项目使用了 db, 则需参考 schema/tables.sql line 287 增加表字段
ENABLE_GET_SUB_COMMENTS = False

# 词云相关
# 是否开启生成评论词云图
ENABLE_GET_WORDCLOUD = False
# 自定义词语及其分组
# 添加规则：xx:yy 其中xx为自定义添加的词组，yy为将xx该词组分到的组名。
CUSTOM_WORDS = {
    "零几": "年份",  # 将“零几”识别为一个整体
    "高频词": "专业术语",  # 示例自定义词
}

# 停用(禁用)词文件路径
STOP_WORDS_FILE = "./docs/hit_stopwords.txt"

# 中文字体文件路径
FONT_PATH = "./docs/STZHONGS.TTF"

# 爬取间隔时间
CRAWLER_MAX_SLEEP_SEC = 2

from .bilibili_config import *
from .xhs_config import *
from .dy_config import *
from .ks_config import *
from .weibo_config import *
from .tieba_config import *
from .zhihu_config import *
