import webapp2
import json

import logging
from google.appengine.api import channel

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info('get')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, webapp2 World!')

# put these in DB
last_channel_group_id = 0
channel_groups = dict()  # id: [token, token, token, ...]

class CreateChannelGroup(webapp2.RequestHandler):
    def get(self):
        global last_channel_group_id, channel_groups
        # TODO(smike): make this threadsafe
        last_channel_group_id += 1
        channel_groups['%s' % last_channel_group_id] = []

        channel_groups.get
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'id': last_channel_group_id}))

class JoinChannelGroup(webapp2.RequestHandler):
    def get(self):
        global channel_groups

        channel_group_id = self.request.get('id')
        channel_group = channel_groups['%s' % channel_group_id]
        client_id = '%s/%s' % (channel_group_id, len(channel_group))
        token = channel.create_channel(client_id)
        channel_group.append(token)

        logging.info('Clients for group %s: %s' % (channel_group_id, channel_group))

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'token': token}))

class ForwardMessage(webapp2.RequestHandler):
    def post(self):
        global channel_groups

        channel_group_id = self.request.get('group')
        sender_token = self.request.get('sender')
        message = self.request.get('message')

        channel_group = channel_groups['%s' % channel_group_id]
        # forward the message to everyone other than the sender
        logging.info('sending message from %s to %s' % (sender_token, channel_group))
        for token in channel_group:
            if token != sender_token:
                logging.info('sending message to %s: %s' % (token, message))
                channel.send_message(token, message)

        self.response.set_status(200)


app = webapp2.WSGIApplication([('/createChannelGroup', CreateChannelGroup),
                               ('/joinChannelGroup', JoinChannelGroup),
                               ('/forwardMessage', ForwardMessage),
                               ('/', MainPage)],
                              debug=True)
