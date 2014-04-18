# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
import re


class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        print('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "bot"

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)
        #self.msg('grayhatter', "connected")

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        smsg = 0
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            smsg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, smsg)
            self.logger.log("<%s> %s" % (user, smsg))
            if msg.startswith("!ping"):
                self.msg(user, "pong!")
        else:
            if msg == ("!ping".strip()):
                self.msg(channel, "pong!")

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            smsg = "%s: I am a bot" % user
            self.msg(channel, smsg)
            self.logger.log("<%s> %s" % (self.nickname, smsg))

        regex = '((http[s]?://)?[A-Za-z0-9\-]+(\.(com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|us|io|uk|ko)(:[0-9]{0,5})?)(/\S*)?)'

        urls = re.findall(regex, msg)
        if urls:
            self.logger.log(urls[0])
            print('found a uri')
            for domain in urls:
                wiki = re.findall('wikipedia\.org/wiki/([A-Za-z0-9_]+)', str(domain))
                if wiki:
                    self.msg(channel, wiki)
                    print('yeah, it\'s a wiki link... I should do something here.')

        if user == 'grayhatter':
            #admin mode
            print('admin mode')
            if msg.startswith('!join #'):
                join_channel = msg.split(' ', 1)[1]
                self.join(join_channel)
            elif msg.startswith('!quit'):
                self.quit('Quitting as ordered!')

        if msg.startswith('!part') and channel != "#cmdline":
            self.part(channel, Reason = user + " made me do it!")


        print('grayhatter', "user: %s channel: %s message: %s smsg: %s" % (user, channel, msg, smsg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason)
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = LogBotFactory('#cmdline', 'tmp.txt')

    # connect factory to this host and port
    reactor.connectTCP("irc.thinstack.net", 6667, f)

    # run bot
    reactor.run()