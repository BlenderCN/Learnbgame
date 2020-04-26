import bpy
import mmvt_utils as mu

try:
    from pizco import Server
except:
    class Server(object):
        pass

from concurrent import futures
import traceback
import os
import os.path as op
import sys
from queue import Queue
import time



def PSMessage(action, options):
    """Builds a message
    """
    return 'PSMessage', action, options


class MMVT_Server(Server):

    _running = False

    def on_request(self, sender, topic, content, msgid):
        """Handles Proxy Server communication, handling attribute access in served_object.

        Messages between proxy and server are handled using a tuple
        containing three elements: a string 'PSMessage', `action` and `options`.

        From Proxy to Server, valid actions are:

        - `exec`: execute a method from an attribute served object.
        - `getattr`: get an attribute from the served object.
        - `setattr`: set an attribute to the served object.
        - `get`: get an attribute from the served object, returning a remote object
                 when necessary.

        From Server to Proxy, valid action are:

        - `return`: return a value.
        - `remote`: return a RemoteAttribute object.
        - `raise`: raise an exception.


        """
        try:
            content_type, action, options = content
            if content_type != 'PSMessage':
                raise ValueError()
        except:
            return super(Server, self).on_request(
                sender, topic, content, msgid)

        try:
            if action == 'exec':
                if options['name'].startswith('mmvt_utils.'):
                    func_name = options['name'].split('.')[-1]
                    attr = getattr(mu, func_name)
                else:
                    attr = getattr(self.served_object, options['name'])
                meth = getattr(attr, options['method'])
                PizcoPanel.q_in.put((options, attr, meth))
                ret = mu.queue_get(PizcoPanel.q_out)
                while ret is None:
                    time.sleep(0.1)
                    ret = mu.queue_get(PizcoPanel.q_out)

            elif action == 'getattr':
                ret = getattr(self.served_object, options['name'])

            elif action == 'setattr':
                setattr(self.served_object, options['name'], options['value'])
                return PSMessage('return', None)

            elif action == 'get':
                if options['name'].startswith('mmvt_utils.'):
                    func_name = options['name'].split('.')[-1]
                    attr = getattr(mu, func_name)
                else:
                    attr = getattr(self.served_object, options['name'])
                if options.get('force_as_object', False) or self.force_as_object(attr):
                    ret = attr
                elif self.return_as_remote(attr):
                    return PSMessage('remote', None)
                else:
                    ret = attr

            elif action == 'inspect':
                return PSMessage('return', self.inspect())

            elif action == 'instantiate':
                if self.served_object is not None:
                    return PSMessage('raise', (Exception('Cannot instantiate another object.'),
                                               ''))

                mod_name, class_name = options['class'].rsplit('.', 1)
                mod = __import__(mod_name, fromlist=[class_name])
                klass = getattr(mod, class_name)
                self.served_object = klass(*options['args'], **options['kwargs'])
                return PSMessage('return', None)
            else:
                ret = Exception('invalid message action {}'.format(action))
                return PSMessage('raise', (ret, ''))

            if isinstance(ret, futures.Future):
                ret.add_done_callback(lambda fut: self.publish('__future__',
                                                               {'msgid': msgid,
                                                                'result': fut.result() if not fut.exception() else None,
                                                                'exception': fut.exception()}))
                return PSMessage('future_register', msgid)

            return PSMessage('return', ret)

        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.format_exception(exc_type, exc_value, exc_tb)[1:]
            return PSMessage('raise', (ex, tb))


class ServerListener(bpy.types.Operator):
    bl_idname = 'mmvt.server_listener'
    bl_label = 'server_listener'
    bl_options = {'UNDO'}
    press_time = time.time()
    running = False

    def modal(self, context, event):
        func_data = mu.queue_get(PizcoPanel.q_in)
        if not func_data is None:
            print('Message in the server queue!')
            options, attr, meth = func_data
            ret = meth(*options.get('args', ()), **options.get('kwargs', {}))
            print('Putting the ret in pizco out queue')
            if ret is None:
                ret = True
            PizcoPanel.q_out.put(ret)

        return {'PASS_THROUGH'}

    def invoke(self, context, event=None):
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.running:
            context.window_manager.modal_handler_add(self)
            self._timer = context.window_manager.event_timer_add(0.1, context.window)
            self.running = True
        return {'RUNNING_MODAL'}


def pizco_draw(self, context):
    layout = self.layout
    layout.label(text='Server: {}'.format(bpy.context.scene.pizco_server_address))


class PizcoPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Pizco"
    addon = None
    init = False
    q_in, q_out = Queue(), Queue()

    @classmethod
    def poll(cls, context):
        return True # Hide when False

    def draw(self, context):
        if PizcoPanel.init:
            pizco_draw(self, context)


bpy.types.Scene.pizco_server_address = bpy.props.StringProperty()


def init(addon):
    PizcoPanel.addon = addon
    if init_pizco(addon):
        register()
        PizcoPanel.init = True
        bpy.ops.mmvt.server_listener()


def init_pizco(mmvt):
    log_fname = op.join(mu.make_dir(op.join(mu.get_user_fol(), 'logs')), 'pizco.log')
    if op.isfile(log_fname):
        os.remove(log_fname)
    for k in range(10):
        try:
            bpy.context.scene.pizco_server_address = 'tcp://127.0.0.1:800{}'.format(str(k))
            MMVT_Server(mmvt, bpy.context.scene.pizco_server_address)
            pizco_exist = True
            with open(log_fname, 'w') as log:
                log.write(bpy.context.scene.pizco_server_address)
            break
        except:
            # print('No pizco')
            # print(traceback.format_exc())
            pizco_exist = False
    if not pizco_exist:
        print('No pizco')
    return pizco_exist


def register():
    try:
        unregister()
        bpy.utils.register_class(PizcoPanel)
        bpy.utils.register_class(ServerListener)
    except:
        print("Can't register Template Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(PizcoPanel)
        bpy.utils.unregister_class(ServerListener)
    except:
        pass
