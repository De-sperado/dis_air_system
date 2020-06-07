import copy
import logging

from threading import Timer, Thread, Lock

# 全局日志记录器
logger = logging.getLogger('django')
UPDATE_FREQUENCY = 1
MAX_WAITING_TIME = 10
MAX_QUEUE = 3
TEMPERATURE_CHANGE_RATE_PER_SEC = (1 / 180, 1 / 120, 1 / 60)
current_temp = 30.0

#工作模式
No = '0'
COOL = '制冷'
HOT = '制热'

#日志条目operation值
POWER_ON = 'power on'
POWER_OFF = 'power off'
CHANGE_TEMP = 'change temp'
CHANGE_SPEED = 'change speed'

#主控机状态
STANDBY = '待机'
RUNNING = '运行中'
STOPPED = '已关机'

#从控机工作状态
AVAILABLE = '未入住'
CLOSED = '关机'
SERVING = '服务中'
WAITING = '等待中'
STANDBY = '待机'

#从控机风速设置
LOW = 0
NORMAL = 1
HIGH = 2

#房间号
room_ids = ('309c', '310c', '311c', '312c', 'f3')

TEMP_LIMT={COOL:[25,30],HOT:[18,25]}

DEFAULT_TARGET_TEMP={COOL:22,HOT:28}


class RepeatTimer(Timer):
    """循环定时器"""

    def __init__(self, interval, function, *args, **kwargs):
        Timer.__init__(self, interval, function, *args, **kwargs)
        self.setName('Timer')

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)


class DBFacadeThread(Thread):

    def __init__(self, function, **kwargs):
        Thread.__init__(self)
        self.name = 'DBFacade'
        self.function = function
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = copy.copy(self.function(**self.kwargs))


class DBFacade:
    """数据库操作"""

    _lock = Lock()
    _thread = None

    @staticmethod
    def exec(function, **kwargs):
        if DBFacade._thread is not None:
            with DBFacade._lock:
                DBFacade._thread.join()
        with DBFacade._lock:
            DBFacade._thread = DBFacadeThread(function, **kwargs)
            DBFacade._thread.start()
            DBFacade._thread.join()
            return DBFacade._thread.result
