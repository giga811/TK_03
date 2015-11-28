from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from chat import app

class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []
	sensor_data = []

    def initialize(self):
        self.logger = app.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, room):
        self.room = room
        self.join(room)
        return True

    def on_nickname(self, nickname):
        self.log('Nickname: {0}'.format(nickname))
        self.nicknames.append(nickname)
        self.session['nickname'] = nickname
        self.broadcast_event('announcement', nickname)
        self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        nickname = self.session['nickname']
        self.nicknames.remove(nickname)
        self.broadcast_event('announcement', nickname)
        self.broadcast_event('nicknames', self.nicknames)
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
            self.session['nickname'], msg)
        return True

	def recv_data(self, data):
		# Send sensor data.
		self.log('User data: {0}'.format(data))
		self.sensor_data.append(data);
		self.emit_to_room(self.room, 'sensor_data', 
			self.session['nickname', data])
		return True