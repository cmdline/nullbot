# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys

# Local imports
from actions import config, bot, security

class client(irc.IRCClient):
    """
    An IRC bot...

    That does stuff...
    """
    def __init__(self, nick, **k):
        '''Call the other functions we\'ll need to do stuff'''
        self.nick     = nick
        self.nickname = nick
        self.bot      = bot.worker(self.nick)
        # self.logger = bot.logger
        self.channels = bot.channelPool()


    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        print ('/joined '+ channel)
        self.bot.channelPool.joined(channel)

    def left(self, channel):
        """This will get called when the bot joins the channel."""
        print ('/left '+ channel)
        self.bot.channelPool.parted(channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        print("user: '%s' channel: '%s' message: '%s' " % (user, channel, msg))

        def restart():
            print('Trying to restart')
            self.msg(suser, 'attempting reload bot...')
            self.bot.wisper(suser, 'storeing session...')
            self.bot.save()
            reload(bot)
            self.msg(suser, 'reload complete!')
            self.bot = bot.worker(self.nick)
            self.bot.wisper(suser, 'handeler reset...')
            self.bot.wisper(suser, 'loading session...')
            self.bot.load()
            self.bot.wisper(suser, 'session loaded...')

        if channel == self.nick:
            suser = user.split('!',1)[0]
            pvmsg = True
        else:
            suser = channel
            pvmsg = False

        if msg == "!backdoor" and pvmsg:
            restart()
        elif msg == '!restart':
            if self.bot.auth.owner(user):
                restart()
            else:
                self.msg(suser, 'you\'re not my mommy...')
        else:
            self.bot.msgin(user, channel, msg)


        jobs = self.bot.queue()
        for job in jobs:
            do, target, params = job
            action = getattr(self, do, None)
            try:
                if action is not None:
                    action(target, params)
            except:
                print action
                print target
                print params
            
                print('!!!!!Not implemented: ' + do + ' !!!!!')


    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        pass

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        pass

    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

class clientFactory(protocol.ClientFactory):
    """
    A factory for irc Bots.

    A new protocol instance will be created each time we connect to the server.
    """
    def __init__(self, channel, nick):
        self.channel  = channel
        self.nick     = nick

    def buildProtocol(self, addr):
        p = client(self.nick)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason)
        reactor.stop()

def connect(server, port, channel, nick):
    # initialize logging to stdout
    log.startLogging(sys.stdout)
    # create factory protocol and application
    factory = clientFactory(channel, nick)
    # connect factory to this host and port
    ## todo error checking for port
    reactor.connectTCP(server, port, factory)
    # run bot
    ## start running in ractorbase in base.py (good luck)
    reactor.run()


def main():
    connect(config.server, config.port, config.channel, config.nick)

if __name__ == '__main__':
    main()
