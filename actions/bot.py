#!/usr/bin/python
## called from client server to process commands.
from actions import security

import sys, time, re, random

authentication = security.authentication

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

    def queue(self, fx=None):
        if fx:
            self._queue += (fx,)
        else:
            out = self._queue
            self._queue = ()
            return out

    # TODO roll into one command
    def msgin(self, user, channel, msg):
        if channel == self.nick:
            to = user.split('!',1)[0]
        else:
            to = channel

        if msg.startswith("!"):
            arg = msg.split(' ',1)
            command = arg[0]
            if len(arg) > 1:
                arg = arg[1]
            else:
                arg = None
            self.command(user, channel, to, command, arg)

        self.act(user, msg, channel, to)
        self.roster.monolouge(channel, user)
        return False


    def command(self, user, channel, to, command, arg):
        # Quick ping check
        print('null', "user: %s channel: %s to: %s command: %s arg: %s " % (user, channel, to, command, arg))
        if command == '!ping':
            self.speak(to, 'pong!')
        # Take ownershp
        if command == '!owner':
            if self.auth.takeOwner(user, arg):
                self.speak(channel, "Mommy")
            else:
                self.speak(channel, "You're not my mommy!")
        # Join command
        if command == '!join':
            self.joinChannel(arg)
        # Part command
        if command == '!part' and channel != "#cmdline":
            self.partChannel(channel, user + " made me do it!")

        if command == '!quit' and self.auth.owner(user):
            self.quit(target, 'Quitting as ordered!')
        if command == '!monolouge':
            mono = self.roster.monolougeReport(channel, user)
            self.speak(to, mono)
        return False

    def act(self, user, msg, channel, to):
        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nick + ":"):
            self.speak(channel, user.split('!',1)[0] + ': I am a bot')

        urlregex ='((http[s]?://)?[A-Za-z0-9\-]+(\.(com|net|org|edu|gov|mil|aero'+\
            '|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel'+\
            '|travel|xxx|us|io|uk|ko)(:[0-9]{0,5})?)(/\S*)?)'

        urls = re.findall(urlregex, msg)
        if urls:
            print('uri detected')
            for domain in urls:
                wiki = re.findall('wikipedia\.org/wiki/([A-Za-z0-9_]+)',
                    str(domain))
                if wiki:
                    self.say(channel, wiki)
                    print('yeah, it\'s a wiki... I should do something here.')

    def partChannel(self, channel, reason=None):
        print('Parting: '+ channel)
        if reason:
            self.queue(('leave', channel, reason))
        else:
            self.queue(('leave', channel))

    def joinChannel(self, channel, key=None):
        print('Joining: '+ channel)
        self.queue(('join', channel, key))

    def speak(self, target, msg):
        print('Speaking: '+ msg)
        self.queue(('msg', target, msg))

    def wisper(self, target, msg):
        print('Speaking: '+ msg)
        self.queue(('notice', target, msg))

class channelPool:
    """Maintail a list of active channel, and hold settings for them as well."""
    def __init__(self):
        self.listOfChannels = set()
        self.listOfActiveChannels = set()
        pass
        # self.channels
    def chanList(self, channel):
        pass

    def join(self, channel):
        if channel in self.listOfActiveChannels:
            pass
        else:
            self.listOfActiveChannels.add(channel)
        self.listOfChannels.add(channel)

    def part(self, channel):
        if channel in self.listOfActiveChannels:
            self.listOfActiveChannels.discard(channel)
        pass

    def nickChange():
        pass

class userRoster:
    """Maintains a list of users, theier settings and notes on them."""
    def __init__(self):
        self.lastActive = {}
        self.roster     = {}
        pass

    def watch(self, user, channel, msg):
        '''Watch members do everything, keep logs, write to file every so often'''
        self.monolouge(channel, user)

    def stats(self):
        pass

    def monolouge(self, channel, user):
        if channel in self.lastActive:
            if user == self.lastActive[channel][0]:
                self.lastActive[channel][1] +=1
            else:
                self.lastActive[channel][0] = user
                self.lastActive[channel][1] = 1
        else:
            self.lastActive[channel] = [user, 1]

    def monolougeReport(self, channel, user):
        result = "Last streak was " + str(self.lastActive[channel][1]) + " lines set "+\
            "by " + self.lastActive[channel][0].split('!',1)[0]
        if user == self.lastActive[channel][0]:
            result += " Keep it up, you can highscore it!"
        else:
            result += "! But you just broke the streak... :("
        return result

    def roster(self, user):
        '''Keeps the roster, does things when called, never returns'''
        pass
