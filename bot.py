#!/usr/bin/python
## called from client server to process commands.
from connection import manager

server  = 'irc.thinstack.net'
channel = '#cmdline'
nick    = 'null'
owner   = 'grayhatter'
port    = 6667

class bot:
    """
    This does all our work for us.
    """

    def __init__(self, owner):
        self.owner = owner

    def act():
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

        regex ='((http[s]?://)?[A-Za-z0-9\-]+(\.(com|net|org|edu|gov|mil|aero'+\
            '|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel'+\
            '|travel|xxx|us|io|uk|ko)(:[0-9]{0,5})?)(/\S*)?)'

        urls = re.findall(regex, msg)
        if urls:
            self.logger.log(urls[0])
            print('found a uri')
            for domain in urls:
                wiki = re.findall('wikipedia\.org/wiki/([A-Za-z0-9_]+)',
                    str(domain))
                if wiki:
                    self.msg(channel, wiki)
                    print('yeah, it\'s a wiki... I should do something here.')

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

def main():
    worker = bot(owner)
    manager.connect(server, port, channel, nick, worker)

if __name__ == '__main__':
    main()
