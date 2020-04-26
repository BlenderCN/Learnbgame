from blendmotion.logger import get_logger

class OperatorError(Exception):
    def report(self, opr):
        opr.report({'ERROR'}, str(self))

    def log(self):
        get_logger().error(self)

def error_and_log(opr, message):
    get_logger().error(message)
    opr.report({'ERROR'}, message)
    return {'CANCELLED'}
