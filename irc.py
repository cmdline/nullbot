# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys

# Local imports
from actions import config, bot

class client(irc.IRCClient):
    """
    An IRC bot...

    That does stuff...
    """
    def __init__(self, nick, **k):
        self.nick     = nick
        self.nickname = nick
        self.bot      = bot.worker(self.nick)

    def actOnBot(self, do, target, params):
        action = getattr(self, do, None)
        try:
            if action is not None:
                action(target, params)
        except:
            print('Not implemented')
            raise NotImplemented

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        print ('/joined '+self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        pass

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        print('null', "user: %s channel: %s message: %s " % (user, channel, msg))

        if channel == self.nick:
            origin = user.split('!',1)[0]
            pvtmsg =1
        else:
            origin = channel
            pvtmsg =0

        if self.bot.owner(user) and msg == '!reload':
            print('Trying to reload')
            self.msg(origin, 'attempting reload...')
            reload(bot)
            self.msg(origin, 'reload complete!')
            self.bot = bot.worker(self.nick)
            self.msg(origin, 'handeler reloaded.')
        elif msg == '!reload':
            self.msg(origin, 'you\'re not my mommy...')

        response = False
        if pvtmsg:
            response = self.bot.privmsg(user, channel, msg)
        else:
            response = self.bot.channel(user, channel, msg)

        if response and isinstance(response, tuple):
            print(response)
            if isinstance(response[0], tuple):
                if not isinstance(response[0][0],str):
                    raise EnvironmentError('To many responses, from the irc bot.')
                    reactor.stop()
                    sys.exit(99)
                else:
                    for action in response:
                        do, target, params = action
                        self.actOnBot(do, target, params)
            else:
                do, target, params = response
                self.actOnBot(do, target, params)


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
