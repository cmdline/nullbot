# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys

class client(irc.IRCClient):
    """
    An IRC bot...

    That does stuff...
    """
    def __init__(self, **k):
        self.nickname = "irc_bot"
        for v in k:
            if v == 'nick':
                self.nickname = k[v]

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
        pass

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
    def __init__(self, channel, handeler):
        self.channel  = channel
        self.handeler = handeler

    def buildProtocol(self, addr):
        p = client(handeler = self.handeler)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason)
        reactor.stop()

def connect(server, port, channel, nick, handeler = None):
    # initialize logging to stdout
    log.startLogging(sys.stdout)
    # create factory protocol and application
    factory = clientFactory(channel, handeler)
    # connect factory to this host and port
    ## todo error checking for port
    reactor.connectTCP(server, port, factory)
    # run bot
    ## start running in ractorbase in base.py (good luck)
    reactor.run()

if __name__ == '__main__':
    print('This module is not yet ready to be called as __main__')
    sys.exit(1)