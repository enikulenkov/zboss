from enum import IntEnum

class ExecutionRetCode(IntEnum):
    success         = 0
    startup_error   = 1
    stopped_by_user = 2
    timeout         = 3
    internal_error  = 4


