import platform

import utils.log_utils
from arglassescmd.cmd_def import *
from arglassescmd.cmd_dict import *
LOG_FILE_PREFIX = "msg_server.log"

log = utils.log_utils.logging_init(__file__, LOG_FILE_PREFIX)



# TARGET_IP = "192.168.1.2"
# TARGET_IP = "192.168.0.113"

TARGET_IP = "127.0.0.1"


TARGET_TCP_PORT = 9527
TARGET_UDP_PORT = 9528

SELF_TCP_PORT = 8888

UNIX_MSG_SERVER_URI = '/tmp/ipc_msg_server.sock'
UNIX_ACT_SERVER_URI = '/tmp/ipc_act_server.sock'
UNIX_SYS_SERVER_URI = '/tmp/ipc_sys_server.sock'
UNIX_LE_SERVER_URI = '/tmp/ipc_le_server.sock'