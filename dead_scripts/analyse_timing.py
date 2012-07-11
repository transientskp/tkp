# -*- coding: utf-8 -*-

outfile = 'tatlgash'

#-------------------------run this to process a tatlgash file -----------------------------------------------------
# it will sum each function's runtime to get a total elapse time in that funtions
# note that functions called may include other tatl'd functions so the sum of the 
#  inner function's contributes to the outer
# also returned is the number of calls to the function
# will probably add a simple average for that function in a later version of this
#--------------------------------------------------------------------------------------------------------------------------------

#handle class labels eg <class 'tkp.sourcefinder.extract.Detection'> __init__ 0.0003850460052490 c = '<'
#handles different class labels eg tkp.sourcefinder.extract.ParamSet __init__ 0.0000159740447998 c = '  '
def getcid(lst, c ):
    #check for class end
    ce = lst.find( c)
    ld = 7
    i = 7
    while (ld != -1) & (i < ce) :
        ld =lst.find('.',i)
        if ld <ce:
            i = ld +1
        else:
            ld = -1
    cln = lst[i : ce -1]
    n = lst.find('.', ce +2)
    fid = lst[ce +2:n]
    #now get the elapsed time
    elap = lst[n+1: -2]
    return [cln,fid, elap]


def updatecl(ent,lst):
    for each in lst:
        if (each[0] == ent[0]):
            if (each[1] == ent[1]):
                try:
                    each[2] += float(ent[2])
                    each[3] +=1
                    return
                except ValueError:
                    print "bad value in update class"
                    return
    try: 
        lst.append([ent[0], ent[1], float(ent[2]),0])
    except ValueError:
        print "bad value ", ent[1]
    
    
    
def updatefn(ent, lst):
     for each in lst:
        if (each[0] == ent[0]):
             try:
                each[1] += float(ent[1])
                each [2] += 1
                return
             except ValueError:
                print "bad value"
                return
     try: 
        lst.append([ent[0], float(ent[1]), 0])
     except ValueError:
        print "bad value in update function ", ent[1]
       
def processdata():
    fob = open(outfile, 'r')
    newlist = []
    print fob
    i = 0
    lines = fob.readlines() #read all lines into memory!
    fob.close()
    sz =len(lines)
    while i < sz :
        num  =0
        n =0
        n = lines[i].find('<') 
        if  n <> -1:
            #< is after the tabs 
            res = getcid(lines[i], '>')
            updatecl(res, newlist)
        else:
            num = lines[i].find('\t', num)
            num1 = num
            #skip indentation
            while num1 != -1:
                num = num1
                num1 = lines[i].find('\t', num1+ 1)
            num1 = lines[i].find(' ', num)
            num2 = lines[i].find(' ', num1 +1)
            if  num2  <> -1:
                res = getcid(lines[i], ' ')
                updatecl(res, newlist)
            else:
                res = [lines[i][num +1: num1 ],lines[i][num1+1:-2]]
                updatefn(res,newlist)
        i +=1
    for each in newlist:
        print each, "\n"
            
    

    
#if __name__ == '__main__'
print "starting"
processdata()
