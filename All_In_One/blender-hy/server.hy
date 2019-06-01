(import [socket :as s]
        [sys]
        [traceback]
        [time]
        [bpy]
        [hy]
        [hy.compiler [HyTypeError]])

(def HOST "localhost")
(def PORT 9992)
(def ENCODING "utf-8")
(def BUFFER_SIZE 4096)
(def ADDON_NAME "blispy") ;;TODO move to version file
(def socket nil)
(def stdout nil)

(defn log [&rest args]
  (print ADDON_NAME ":" args))

(defclass StdOut[object]
  (defn __init__[self]
    (setv self.buffer ""))
  
  (defn write[self string]
    (let [out sys.__stdout__]
      (setv self.buffer (+ self.buffer string))
      (out.write string)))
  
  (defn flush[self]
    (setv self.buffer "")))

(defn send [conn data]
  (conn.send (data.encode ENCODING)))

(defn process-input []
  (let [[conn addr] (socket.accept)
        data (conn.recv BUFFER_SIZE)
        data-str (data.decode "utf-8")]
    (try
     (let [result (eval (read-str data-str) (globals))
           buffer (+ stdout.buffer (str result))]
       (send conn buffer)
       (stdout.flush))
     (except [e socket.error]
       (print "socket error"))
     (except [e Exception]
       (let [tb (traceback.format_exc)
             out (+ tb (str e))]
         (send conn out))))))

(defn create-socket[]
  (let [socket (s.socket s.AF_INET s.SOCK_STREAM)]
    (try
     (do
      (socket.setblocking 0)
      (socket.bind (, HOST PORT))
      (socket.listen 1))
     (except [e s.error] ;;TODO expand error
       (log "Socket bind faild. Error:" e)))
    (log "socket binded to host" HOST "at port" PORT)
    socket))


(defclass HyREPL[]
  (defn start[]
    (setv stdout (StdOut))
    (setv sys.stdout stdout)
    (setv socket (create-socket))
    )
  
  (defn update[]
    (process-input))
  
  (defn end[]))
