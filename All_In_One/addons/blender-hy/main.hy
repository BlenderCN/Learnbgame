(import bpy)
;;(import server)

(defclass ModalTimerOperator [bpy.types.Operator]
  (setv bl_idname "wm.modal_timer_operator") ;;TODO rename
  (setv bl_label "Blender Hy REPL") ;;TODO rename
  (setv _timer nil)

  (defn modal[self context event]
    (print "woo!")
    (set ["PASS_THROUGH"]))

  (defn execute[self context]
    (let [wm context.window_manager]
      (setv self._timer (wm.event_timer_add 0.1 context.window))
      (wm.modal_handler_add self)
      (set ["RUNNING_MODAL"])))

  (defn cancel[self context]
    (let [wm context.window_manager]
      (wm.event_timer_remove self._timer)
      (set ["CANCELLED"]))))

(defn register[]
  ;;(bpy.utils.register_class ModalTimerOperator)
  ;;TODO serve start
  )

(defn unregister[]
  ;;(bpy.utils.unregister_class ModalTimerOperator)
  )
