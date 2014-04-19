#!/usr/bin/python
## called from client server to process commands.
import sys, time, re

class worker():
    """
    This does all our work for us.
    """

    def __init__(self, nick):
        self.nick        = nick
        self.auth        = authentication()
        self.cmd         = "!"
        self._queue      = ()
        self.channelPool = channelPool()
        self.roster      = userRoster()

    def privmsg(self, user, channel, msg):
        to = user.split('!',1)[0]
        if msg.startswith("!ping"):
            return 'msg', to, 'pong!'
        else:
            return self.act(user, channel, msg)
            return False

    def channel(self, user, channel, msg):
        to = channel
        if msg.startswith("!ping"):
            return 'msg', to, 'pong!'
        else:
            return self.act(user, channel, msg)
            return False

    def act(self, user, channel, msg):
        result = ()
        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nick + ":"):
            result += 'msg', channel, "%s: I am a bot" % user.split('!',1)[0]

        regex ='((http[s]?://)?[A-Za-z0-9\-]+(\.(com|net|org|edu|gov|mil|aero'+\
            '|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel'+\
            '|travel|xxx|us|io|uk|ko)(:[0-9]{0,5})?)(/\S*)?)'

        urls = re.findall(regex, msg)
        if urls:
            print('uri detected')
            for domain in urls:
                wiki = re.findall('wikipedia\.org/wiki/([A-Za-z0-9_]+)',
                    str(domain))
                if wiki:
                    result += self.say(channel, wiki)
                    print('yeah, it\'s a wiki... I should do something here.')

        # Join command
        if msg.startswith('!join #'):
            channel = msg.split(' ',1)[1]
            result += self.joinChannel(channel)
        # Part command
        if msg.startswith('!part') and channel != "#cmdline":
            result += self.partChannel(channel, user + " made me do it!")

        # Owner commands
        if self.owner(user):
            #admin mode
            if msg.startswith('!quit'):
                if msg.split()[1].startswith('#'):
                    target = msg.split()[1]
                else:
                    target = channel
                result += self.quit(target, 'Quitting as ordered!')

        return result

    def partChannel(self, channel, reason=None):
        print('Parting: '+ channel)
        if reason:
            return 'leave', channel, reason
        else:
            return 'leave', channel

    def joinChannel(self, channel, key=None):
        print('Joining: '+ channel)
        return 'join', channel, key

    def speak(self, target, msg):
        print('Speaking: '+ msg)
        return 'msg', target, msg