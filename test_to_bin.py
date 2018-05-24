'''
Output one ascii byte in binary per line. Takes single command line arg.

Created on 24 May 2018

@author: si
'''
def to_bin(s):
    """
    :param s: string to represent as binary
    """
    r = []
    for c in s:
        if not c:
            continue
        t = "{:08b}".format(ord(c))
        r.append(t)
    return '\n'.join(r)

if __name__ == '__main__':
    import sys
    print(to_bin(sys.argv[1]))

