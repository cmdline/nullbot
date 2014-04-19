#!/usr/bin/python
import sys, time, random

class authentication():
    '''
    Maintins all of the owners and admins of the bot.
    '''
    def __init__(self):
        self.hasOwner = False
        self.__ownerOTP = random.randint(0,999999)
        print('====================================================')
        print("||| OTP for owner: %06d" % self.__ownerOTP)
        print('====================================================')

    def takeOwner(self, user, OTP):
        if self.hasOwner:
            print('====================================================')
            print('||| Hacking Attempt by: '+user )
            print('====================================================')
            return False
        if int(OTP) == self.__ownerOTP:
            print('====================================================')
            print('||| Gave ownership to: ' +user)
            print('====================================================')
            self.__masterOwner = user
            self.hasOwner = True
            self.__ownerOTP = None
            return True

    def giveOwner(self):
        pass

    def addOwner(self):
        pass

    def dropOwner(self):
        pass

    def owner(self, test=None):
        if not self.hasOwner:
            print('====================================================')
            print("||| Request for owner, but no owner set")
            print("||| OTP for owner: %06d" % self.__ownerOTP)
            print('====================================================')
            return False
        else:
            if test and (test == self.__masterOwner):
                return True
            else:
                return False
        # TODO this is less secure then it should be.
        return False
