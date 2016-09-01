import random

def generateRandomString(length):
    result = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    for index in range(length):
        result += random.choice(possible)

    return result
