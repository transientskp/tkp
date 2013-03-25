#! /usr/bin/env python


def timing(deconv):
    deconv(1, 1, 0, 1, 1, 0)
    deconv(1, 1, 0, 1, 1, 180)
    deconv(1, 1, 0, 1, 1, 90)
    deconv(1, 1, 0, 1, 1, 45)

    deconv(2., 2., 0, 1, 1, 0)
    deconv(2., 2., 0, 1, 1, 180)
    deconv(2., 2., 0, 1, 1, 90)
    deconv(2., 2., 0, 1, 1, 45)

    deconv(2.7, 1.7, 0, 1, 1, 0)
    deconv(2.7, 1.7, 0, 1, 1, 180)
    deconv(2.7, 1.7, 0, 1, 1, 90)
    deconv(2.7, 1.7, 0, 1, 1, 45)

    deconv(2.7, 1.7, 10, 1, 1, 0)
    deconv(2.7, 1.7, 20, 1, 1, 180)
    deconv(2.7, 1.7, 30, 1, 1, 90)
    deconv(2.7, 1.7, 40, 1, 1, 45)



def correctness(deconv):

    print deconv(1, 1, 0, 1, 1, 0)
    print deconv(1, 1, 0, 1, 1, 180)
    print deconv(1, 1, 0, 1, 1, 90)
    print deconv(1, 1, 0, 1, 1, 45)

    print deconv(2., 2., 0, 1, 1, 0)
    print deconv(2., 2., 0, 1, 1, 180)
    print deconv(2., 2., 0, 1, 1, 90)
    print deconv(2., 2., 0, 1, 1, 45)

    print deconv(2.7, 1.7, 0, 1, 1, 0)
    print deconv(2.7, 1.7, 0, 1, 1, 180)
    print deconv(2.7, 1.7, 0, 1, 1, 90)
    print deconv(2.7, 1.7, 0, 1, 1, 45)

    print deconv(2.7, 1.7, 10, 1, 1, 0)
    print deconv(2.7, 1.7, 20, 1, 1, 180)
    print deconv(2.7, 1.7, 30, 1, 1, 90)
    print deconv(2.7, 1.7, 40, 1, 1, 45)

# The following routines all generate an error
# and should therefore only be used to test for
# correctness of the error being raised; not for
# timing purposes
#    print deconv(0.5, 0.5, 0, 1, 1, 0)
#    print deconv(0.5, 0.5, 0, 1, 1, 180)
#    print deconv(0.5, 0.5, 0, 1, 1, 90)
#    print deconv(0.5, 0.5, 0, 1, 1, 45)
#    print deconv(1.2, 0.7, 0, 1, 1, 0)
#    print deconv(1.2, 0.7, 0, 1, 1, 180)
#    print deconv(1.2, 0.7, 0, 1, 1, 90)
#    print deconv(1.2, 0.7, 0, 1, 1, 45)


def run():
    #print 'Timing'
    #print '5 times 100000 executions, FORTRAN routine:',
    #print Timer('timing(deconv)', 'from __main__ import timing; from deconv import deconv').repeat(repeat=5, number=100000)
    #print
    #print '5 times 100000 executions, Python routine:',
    #print Timer('timing(deconv)', 'from __main__ import timing; from deconv2 import deconv').repeat(repeat=5, number=100000)
    #print
    print 'checking correctness'
    print 'FORTRAN routine:'
    from deconv import deconv
    correctness(deconv)
    print
    print 'Python routine:'
    correctness(deconv)

	
if __name__ == "__main__":
    run()
