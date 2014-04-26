#!/usr/bin/python
## called from client server to process commands.

#local
from actions import security

#system
import sys, time, re, random
import urllib as urll
import cPickle as pickle

authentication = security.authentication

class worker:
    """This does all our work for us."""
    def __init__(self, nick):
        self.nick        = nick
        self.auth        = authentication()
        self.cmdprefix   = "!"
        self._queue      = ()
        self.channelPool = channelPool()
        self.roster      = userRoster()
        self.pdata       = pdata()
        self.log         = logging()

    def queue(self, fx=None):
        if fx:
            self._queue += (fx,)
        else:
            out = self._queue
            self._queue = ()
            return out

    def save(self):
        with open('./session.pk1', 'wb') as f:
            pickle.dump(self.auth, f)
            pickle.dump(self.channelPool, f)
            pickle.dump(self.roster, f)
            f.flush()
        return True

    def load(self):
        with open('./session.pk1', 'rb') as f:
            self.auth = pickle.load(f)
            self.channelPool = pickle.load(f)
            self.roster = pickle.load(f)
        return True

    def panic(self, msg):
        print msg
        sys.exit(9)

    def reloadModules(self):
        try:
            reload(security)
        except:
            self.panic('!PANIC! reloadModules')
            sys.exit(55)

    # TODO roll into one command
    def msgin(self, user, channel, msg):
        if channel == self.nick:
            to = user.split('!',1)[0]
        else:
            to = channel

        if msg.startswith(self.cmdprefix):
            arg = msg.split(' ',1)
            command = arg[0]
            if len(arg) > 1:
                arg = arg[1]
            else:
                arg = None
            self.command(user, channel, to, command, arg)

        self.roster.watch(user, channel, msg)
        self.channelPool.watch(user, channel, msg)

        if self.channelPool.channel(channel, 'mute'):
            self.autoAct(user, msg, channel, '')
        else:
            self.autoAct(user, msg, channel, to)

        return True

    def command(self, user, channel, to, command, arg):
        # Quick ping check
        print('null', "user: %s channel: %s to: %s command: %s arg: %s " % (user, channel, to, command, arg))
        if command == '!ping':
            self.speak(to, 'pong!')
        # Take ownershp
        if command == '!owner':
            if self.auth.takeOwner(user, arg):
                self.wisper(channel, "Mommy")
            else:
                self.wisper(channel, "You're not my mommy!")

        # channel/server jobs
        if command == '!tell':
            self.tell(user, channel, to, arg)
        if command == '!introduce':
            self.introduce(to, arg)
        if command == '!lastseen':
            self.lastSeen(to, arg)

        # look up information 
        if command == '!wiki':
            print '"'+arg+'"'
            self.speak(to, self.pdata.wiki(arg))
        if command == '!google' or command == '!g':
            pass

        # bot jobs
        if command == '!set':
            self.putSetting(to, arg)
        if command == '!save':
            self.save()
            self.speak(to, 'saved')
        if command == '!join':
            self.joinChannel(arg)
        if command == '!part' and channel != "#cmdline":
            self.partChannel(channel, user + " made me do it!")
        if command == '!mute':
            self.channelPool.setChannel(channel, 'mute', True)
        if command == '!unmute':
            self.channelPool.setChannel(channel, 'mute', False)

        if command.startswith('!!') and self.auth.owner(user):
            if command == '!!quit':
                self.quit(target, 'Quitting as ordered!')
            if command == '!!reloadall':
                self.reloadModules();

        # external fxns
        if command == '!monolouge':
            mono = self.roster.monolouge(channel, user)
            self.speak(to, mono)
        return False

    def autoAct(self, user, msg, channel, to):
        username = user.split('!',1)[0]
        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nick + ":"):
            self.speak(channel, user.split('!',1)[0] + ': I am a bot')

        urlregex =r'((http[s]?://)?[A-Za-z0-9\-\.]+(\.(com|net|org|edu|gov|mil'+\
            '|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|'+\
            'tel|travel|xxx|us|io|uk|ko|fm)(:[0-9]{0,5})?)(/\S*)?)'

        msgs = msg.split()
        for m in msgs:
            urls = re.search(urlregex, m)
            if urls:
                uri = urls.group()
                wiki = re.findall('wikipedia\.org/wiki/([A-Za-z0-9_]+)', uri)
                if wiki:
                    wikisent = self.pdata.wiki(wiki[0])
                    self.speak(to, wikisent)
                else:
                    if not uri.lower().startswith('http'):
                        uri = 'http://'+uri
                    title = self.pdata.httpTitle(uri)
                    if title:
                        self.speak(to, title)
                        self.log.saveLink(uri, channel, title)
                    else:
                        self.log.saveLink(uri, channel, uri)


    def partChannel(self, channel, reason=None):
        print('Parting: '+ channel)
        if reason:
            self.queue(('leave', channel, reason))
        else:
            self.queue(('leave', channel))
        # self.auth.tellOwner('ordered to part '+channel)

    def joinChannel(self, channel, key=None):
        print('Joining: '+ channel)
        self.queue(('join', channel, key))

    def changeNick(self):
        pass

    def kickUser(self):
        pass

    def speak(self, target, msg):
        self.queue(('msg', target, msg))

    def wisper(self, target, msg):
        print('Speaking: '+ msg)
        self.queue(('notice', target, msg))

    def tell(self, user, channel, send, msg):
        '''TODO
        feature light for now, but should track down this user and tell
        them publicly, for now it will address the user in the from channel
        '''
        who = msg.split(' ',1)[0]
        msg = msg.split(' ',1)[1]
        self.queue(('msg', send, who+": <"+user.split('!',1)[0] + \
            "> wants me to tell you: \"" + msg + '"'))

    def lastSeen(self, to, user):
        locLastSeen = self.roster.lastSeen(user)
        if locLastSeen:
            mins = (time.time() - locLastSeen['time']) / 60
            self.speak(to, "I last saw " + user + " in " +locLastSeen['where']+\
                " " + str(int(mins)) + 'minutes ago saying: "' +\
                locLastSeen['action'] + '"')
        else:
            self.speak(to, "I don't think I've ever seen " + user)

    def introduce(self, to, nick):
        if nick == self.nick or nick == 'yourself':
            self.speak(to, "Hello, I'm a python bot with a modular backend"+\
                " I'm bound to user: " + self.auth.printOwner().split('!')[0] + " Who are you?")
        else:
            if self.roster.getSetting(nick, 'intro'):
                self.speak(to, self.roster.getSetting(nick, 'intro'))
            else:
                self.speak(to, "I don't know who " + nick + " Is.")

    def putSetting(self, to, arg):
        tv, msg = arg.split(' ',1)
        target, val = tv.split(':',1)
        self.roster.storeSetting(target, val, msg)

class channelPool:
    """Maintail a list of active channel, and hold settings for them as well."""
    def __init__(self):
        self.listOfChannels       = set()
        self.listOfActiveChannels = set()
        self.channelSettings      = {}
        pass
        # self.channels

    def watch(self, user, channel, msg):
        pass

    def channel(self, channel, settings):
        '''retruns channel settings'''
        if channel in self.channelSettings:
            return self.channelSettings[channel][settings]
        return None

    def setChannel(self, channel, settings, value):
        '''set a value for this channel'''
        if channel in self.channelSettings:
            self.channelSettings[channel][settings] = value
        return None

    def listActive(self):
        return self.listOfActiveChannels

    def joined(self, channel):
        self.listOfActiveChannels.add(channel)
        self.listOfChannels.add(channel)
        self.channelSettings[channel] = {}
        self.channelSettings[channel]['mute'] = False

    def parted(self, channel):
        if channel in self.listOfActiveChannels:
            self.listOfActiveChannels.discard(channel)
    
    def lockChannel(self):
        '''Lock channel so that user's can't force a /part'''
        pass

    def nickChange():
        pass

    def storeSetting(self):
        pass

    def getSetting(self):
        pass

class userRoster:
    """Maintains a list of users, theier settings and notes on them."""
    def __init__(self):
        self.lastActive  = {}
        self.roster      = {}
        self.settings    = {}
        self.lastSeenVal = {}

    def watch(self, user, channel, msg):
        '''Watch members do everything, keep logs, write to file every so often'''
        self.monolougeLog(channel, user)
        self.lastSeenLog(user, channel, msg)

    def stats(self):
        pass

    def lastSeenLog(self, user, where, action):
        user = user.split('!',1)[0]
        if user not in self.lastSeenVal:
            self.lastSeenVal[user] = {}
        self.lastSeenVal[user]['where']  = where
        self.lastSeenVal[user]['time']   = time.time()
        self.lastSeenVal[user]['action'] = action

    def lastSeen(self, user):
        user = user.strip()
        if user in self.lastSeenVal:
            return self.lastSeenVal[user]
        else:
            return False

    def monolougeLog(self, channel, user):
        if channel in self.lastActive:
            if user == self.lastActive[channel][0]:
                self.lastActive[channel][1] +=1
            else:
                self.lastActive[channel][0] = user
                self.lastActive[channel][1] = 1
        else:
            self.lastActive[channel] = [user, 1]

    def monolouge(self, channel, user):
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

    def getSetting(self, nick, val):
        nick = nick.strip()
        if nick in self.settings:
            return self.settings[nick][val]
        else:
            return False

    def storeSetting(self, nick, val, msg):
        if nick in self.settings:
            self.settings[nick][val] = msg
        else:
            self.settings[nick] = {}
            self.settings[nick][val] = msg

class logging:
    """docstring for logging"""
    def __init__(self):
        pass

    def saveLink(self, uri, chan, title):
        link = '<a href="'+uri+'">'+chan+': '+title+'</a><br />'+"\n"
        with open('./urilog.txt', 'r+') as f:
            content = f.read()
            f.seek(0)
            f.write(link+content)
            f.flush()
        return True

class pdata:
    """pull data from other things"""
    def __init__(self):
        pass

    def httpRequest(self, uri):
        if not uri.lower().startswith('http'):
            uri = 'http://'+uri
        page = urll.urlopen(uri)
        return page.read()

    def httpTitle(self, uri):
        pagedata = self.httpRequest(uri)
        a = re.search(r'<title>(.+)</title>', pagedata, re.I + re.S)
        return a.group(1).strip()

    def wiki(self, topic):
        # compile the regex
        whitespace    = re.compile(r'\s')
        firstsentence = re.compile(r'<p>(.+?</b>.+?\.).+?</p>', flags=re.I)
        htmltag       = re.compile(r'(<.+?>)', flags=re.I)
        # strip the whitespace
        topic = whitespace.sub('_', topic)
        pagedata = self.httpRequest('https://en.wikipedia.com/wiki/'+topic)
        if pagedata:
            # pull the first sentence
            desc = firstsentence.search(pagedata)
            if desc:
                # strip html tags
                desc = desc.group(1)
                return htmltag.sub('', desc)
            else:
                crurl = "https://en.wikipedia.org/w/index.php?title="+topic+"&action=edit"
                return "Wikipedia doesn't have an entry for this. Would you like to create one? " + crurl
        else:
            return 'bad data'
        return False
