from channels import Group
from channels.sessions import channel_session


@channel_session
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    job_id = message.content['path'][9:]
    message.channel_session['job_ID'] = job_id
    Group("user-%s" % job_id).add(message.reply_channel)


@channel_session
def ws_keepalive(message):
    Group("user-%s" % message.channel_session['job_ID']).add(message.reply_channel)


@channel_session
def ws_message(message):
    print('Channel-' + message.content['text'] + ' connected!')


@channel_session
def ws_disconnect(message):
    Group("user-%s" % message.channel_session['job_ID']).discard(message.reply_channel)