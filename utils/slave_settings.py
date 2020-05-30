'''从控机工作状态'''

AVAILABLE = 1
CLOSED = 2
RUNNING = 3
WAITING = 4
READY = 5

'''从控机属性设置'''
TEMP_LOW_BOUND = 10
TEMP_HIGH_BOUND = 40

COOL_MODE = 1
WARM_MODE = 2
DRY_MODE = 3

MAX_SPEED = 7
MIN_SPEED = 1

FEE_RATE_PER_MIN = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

'''房间号'''
room_ids = ['u101', 'u102', 'b103', 'b104', 't105', 't106', 'u201', 'b202', 't203']