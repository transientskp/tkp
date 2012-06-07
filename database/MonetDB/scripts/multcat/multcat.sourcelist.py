import os, errno, time, sys,pylab
import numpy as np
from datetime import datetime
import monetdb.sql as db
from monetdb.sql import Error as Error
#import MySQLdb as db
#from MySQLdb import Error as Error
import logging

host = sys.argv[1] # number of sources per image
#ns = int(sys.argv[2]) # number of sources per image
#iter = int(sys.argv[3]) # number of images to process

db_type = "MonetDB"
db_host = host
db_port = 50000
db_dbase = "multcat"
db_user = "multcat" 
db_passwd = "ch4"

monetdbtkphome = os.getenv('MONETDBTKPHOME') 
#monetdbtkphome = '/scratch/bscheers'
path = monetdbtkphome + '/scripts/multcat'

#f = '/copy.into.extractedsources.' + str(ns) + '.csv'
#infile = path + f

logtime = time.strftime("%Y%m%d-%H%M")
lf = '/logs/multcat.sourcelist.' + host + '.log'
logfile = path + lf
logf = open(logfile, 'w')
row = 'csv log file of processing times of the multi-catalog association. \n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)
row = '| iter | imageid | query5_time | query8_time | query9_time | query10_time | query12_time |\n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)
#conn = db.connect(host=db_host,db=db_dbase,user=db_user,passwd=db_passwd, unix_socket="/scratch/bscheers/databases/mysql/var/mysql.sock")

try:
    iter_start = time.time()
    cursor = conn.cursor()
    
    # To select the sources that could be associated in all three catalogs
    query = 13
    fluxlim = 1
    sql_list_known_sources_3_assocs = """\
      select ac2.xtrsrc_id
            ,c3.cat_id
            ,c3.freq_eff
            ,c3.i_peak_avg
            ,c3.i_int_avg
            ,c3.i_int_avg_err
            ,ac2.assoc_catsrc_id
            ,c4.cat_id
            ,c4.freq_eff
            ,c4.i_peak_avg
            ,c4.i_int_avg 
            ,c4.i_int_avg_err
            ,ra2hms(m1.ra_avg)
            ,decl2dms(m1.decl_avg)
            ,c3.orig_catsrcid
            ,c4.orig_catsrcid
            ,3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c3.x) * (m1.x - c3.x)
                                         + (m1.y - c3.y) * (m1.y - c3.y)
                                         + (m1.z - c3.z) * (m1.z - c3.z)
                                         )
                                         / 2
                                    )
                           )
             /
             SQRT(m1.ra_err_avg * m1.ra_err_avg + c3.ra_err * c3.ra_err
                 + m1.decl_err_avg * m1.decl_err_avg + c3.decl_err * c3.decl_err)
             AS assoc_r_c3
            ,LOG10(EXP(-(3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c3.x) * (m1.x - c3.x)
                                                     + (m1.y - c3.y) * (m1.y - c3.y)
                                                     + (m1.z - c3.z) * (m1.z - c3.z)
                                                     )
                                                     / 2
                                                )
                                       )
                        /
                        SQRT(m1.ra_err_avg * m1.ra_err_avg + c3.ra_err * c3.ra_err
                            + m1.decl_err_avg * m1.decl_err_avg + c3.decl_err * c3.decl_err)
                        )
                        *
                        (3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c3.x) * (m1.x - c3.x)
                                                     + (m1.y - c3.y) * (m1.y - c3.y)
                                                     + (m1.z - c3.z) * (m1.z - c3.z)
                                                     )
                                                     / 2
                                                )
                                       )
                         /
                         SQRT(m1.ra_err_avg * m1.ra_err_avg + c3.ra_err * c3.ra_err
                             + m1.decl_err_avg * m1.decl_err_avg + c3.decl_err * c3.decl_err)
                        )
                        / 2
                      )
                 /
                 (2 * PI() * SQRT(m1.ra_err_avg * m1.ra_err_avg + c3.ra_err * c3.ra_err) 
                           * SQRT(m1.decl_err_avg * m1.decl_err_avg + c3.decl_err * c3.decl_err) 
                           * 4.02439375E-06)
                 ) AS assoc_lr_c3
            ,3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c4.x) * (m1.x - c4.x)
                                         + (m1.y - c4.y) * (m1.y - c4.y)
                                         + (m1.z - c4.z) * (m1.z - c4.z)
                                         )
                                         / 2
                                    )
                           )
             /
             SQRT(m1.ra_err_avg * m1.ra_err_avg + c4.ra_err * c4.ra_err
                 + m1.decl_err_avg * m1.decl_err_avg + c4.decl_err * c4.decl_err)
             AS assoc_r_c4
            ,LOG10(EXP(-(3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c4.x) * (m1.x - c4.x)
                                                     + (m1.y - c4.y) * (m1.y - c4.y)
                                                     + (m1.z - c4.z) * (m1.z - c4.z)
                                                     )
                                                     / 2
                                                )
                                       )
                        /
                        SQRT(m1.ra_err_avg * m1.ra_err_avg + c4.ra_err * c4.ra_err
                            + m1.decl_err_avg * m1.decl_err_avg + c4.decl_err * c4.decl_err)
                        )
                        *
                        (3600 * DEGREES(2 * ASIN(SQRT( (m1.x - c4.x) * (m1.x - c4.x)
                                                     + (m1.y - c4.y) * (m1.y - c4.y)
                                                     + (m1.z - c4.z) * (m1.z - c4.z)
                                                     )
                                                     / 2
                                                )
                                       )
                         /
                         SQRT(m1.ra_err_avg * m1.ra_err_avg + c4.ra_err * c4.ra_err
                             + m1.decl_err_avg * m1.decl_err_avg + c4.decl_err * c4.decl_err)
                        )
                        / 2
                      )
                 /
                 (2 * PI() * SQRT(m1.ra_err_avg * m1.ra_err_avg + c4.ra_err * c4.ra_err) 
                           * SQRT(m1.decl_err_avg * m1.decl_err_avg + c4.decl_err * c4.decl_err) 
                           * 4.02439375E-06)
                 ) AS assoc_lr_c4
        from assoccatsources ac2
            ,catalogedsources c3
            ,catalogedsources c4 
            ,multcatbasesources m1 
       where ac2.xtrsrc_id = c3.catsrcid 
         and ac2.xtrsrc_id = m1.xtrsrc_id
         and ac2.assoc_catsrc_id = c4.catsrcid 
         and ac2.xtrsrc_id in (select ac1.xtrsrc_id 
                                 from assoccatsources ac1
                                     ,catalogedsources c1
                                     ,catalogedsources c2 
                                where xtrsrc_id = c1.catsrcid 
                                  and assoc_catsrc_id = c2.catsrcid 
                                  and xtrsrc_id in (select xtrsrc_id 
                                                      from assoccatsources 
                                                    group by xtrsrc_id 
                                                    having count(*) > 1
                                                   ) 
                                  and c2.cat_id = 4 
                                  and c2.i_int_avg > %s -- having a flux at 74MHz > 10Jy
                              ) 
      order by ac2.xtrsrc_id
              ,ac2.assoc_catsrc_id
    """
    query_start = time.time()
    cursor.execute(sql_list_known_sources_3_assocs,(fluxlim,))
    query13_time = time.time() - query_start
    print "\tQuery ", query, ": ", str(round(query13_time*1000,2)), "ms"
    y=cursor.fetchall()
    print "len(y)", len(y)
    spec_index_avg = []
    
    sources = [[],[]]
    prev_id = 0
    vlssflux=0
    wenssflux=0
    nvssflux=0
    vlssfreq=0
    wenssfreq=0
    nvssfreq=0
    alpha_1=[]
    alpha_2=[]
    print "| source_id | spectral index | chi^2 | "
    for i in range(len(y)):
        base_id = y[i][0]
        if base_id != prev_id:
            if i > 0:
                # y = mx + c
                # logS = m lognu + c
                # Here we fit straight line through three points
                #                                                    vvv freq 
                m,c = np.linalg.lstsq(np.vstack([np.array([pylab.log10(base[2]),pylab.log10(assoc[2][0]),pylab.log10(assoc[2][1])]), np.ones(3)]).T \
                                                ,np.array([pylab.log10(base[3]),pylab.log10(assoc[3][0]),pylab.log10(assoc[3][1])]))[0]
                #                                                    ^^^ flux 
                spec_index = m
                chisq = ((pylab.log10(base[3]) - c - m * pylab.log10(base[2])) / base[4])**2 \
                      + ((pylab.log10(assoc[3][0]) - c - m * pylab.log10(assoc[2][0])) / assoc[4][0])**2 \
                      + ((pylab.log10(assoc[3][1]) - c - m * pylab.log10(assoc[2][1])) / assoc[4][1])**2
                spec_index_avg.append(spec_index)
                #if chisq > 3:
                #    print '\033[1;38m',base,assoc,spec_index,chisq, '\033[1;m'
                #else:
                #    print base,assoc,spec_index,chisq
                wenssastr = ''
                # If we want to have a two-spectral index distribution
                # alpha_1 (74/325), alpha_2 (325/1400)
                # we have to know the frequency :
                if base[1] == 3:
                    #nvssid = base[0]
                    nvssid = base[7]
                    nvssfreq = base[2]
                    nvssflux = base[3]
                    nvssfluxerror = base[4]
                    nvss_r = base[8]
                    nvss_logLR = base[9]
                elif assoc[1][0] == 3:
                    #nvssid = assoc[0][0]
                    nvssid = assoc[5][0]
                    nvssfreq = assoc[2][0]
                    nvssflux = assoc[3][0]
                    nvssfluxerror = assoc[4][0]
                    nvss_r = assoc[6][0]
                    nvss_logLR = assoc[7][0]
                elif assoc[1][1] == 3:
                    #nvssid = assoc[0][1]
                    nvssid = assoc[5][1]
                    nvssfreq = assoc[2][1]
                    nvssflux = assoc[3][1]
                    nvssfluxerror = assoc[4][1]
                    nvss_r = assoc[6][1]
                    nvss_logLR = assoc[7][1]
                if base[1] == 4:
                    #vlssid = base[0]
                    vlssid = base[7]
                    vlssfreq = base[2]
                    vlssflux = base[3]
                    vlssfluxerror = base[4]
                    vlss_r = base[8]
                    vlss_logLR = base[9]
                elif assoc[1][0] == 4:
                    #vlssid = assoc[0][0]
                    vlssid = assoc[5][0]
                    vlssfreq = assoc[2][0]
                    vlssflux = assoc[3][0]
                    vlssfluxerror = assoc[4][0]
                    vlss_r = assoc[6][0]
                    vlss_logLR = assoc[7][0]
                elif assoc[1][1] == 4:
                    #vlssid = assoc[0][1]
                    vlssid = assoc[5][1]
                    vlssfreq = assoc[2][1]
                    vlssflux = assoc[3][1]
                    vlssfluxerror = assoc[4][1]
                    vlss_r = assoc[6][1]
                    vlss_logLR = assoc[7][1]
                if base[1] == 5:
                    #wenssid = base[0]
                    wenssid = base[7]
                    if (base[2] == 352000000.):
                        wenssastr = '*'
                    wenssfreq = base[2]
                    wenssflux = base[3]
                    wenssfluxerror = base[4]
                    wenss_r = base[8]
                    wenss_logLR = base[9]
                elif assoc[1][0] == 5:
                    #wenssid = assoc[0][0]
                    wenssid = assoc[5][0]
                    if (assoc[2][0] == 352000000.):
                        wenssastr = '*'
                    wenssfreq = assoc[2][0]
                    wenssflux = assoc[3][0]
                    wenssfluxerror = assoc[4][0]
                    wenss_r = assoc[6][0]
                    wenss_logLR = assoc[7][0]
                elif assoc[1][1] == 5:
                    #wenssid = assoc[0][1]
                    wenssid = assoc[5][1]
                    if (assoc[2][0] == 352000000.):
                        wenssastr = '*'
                    wenssfreq = assoc[2][1]
                    wenssflux = assoc[3][1]
                    wenssfluxerror = assoc[4][1]
                    wenss_r = assoc[6][1]
                    wenss_logLR = assoc[7][1]
                alpha_1.append(round(pylab.log10(vlssflux/wenssflux)/pylab.log10(vlssfreq/wenssfreq),3))
                alpha_2.append(round(pylab.log10(wenssflux/nvssflux)/pylab.log10(wenssfreq/nvssfreq),3))
                if chisq > 3:
                    print '\033[1;38m',base[5] ,'&' \
                                      ,base[6] ,'&' \
                                      ,round(pylab.log10(vlssflux/wenssflux)/pylab.log10(vlssfreq/wenssfreq),3) ,'&' \
                                      ,round(pylab.log10(wenssflux/nvssflux)/pylab.log10(wenssfreq/nvssfreq),3) ,'&' \
                                      ,round(spec_index,3) ,'&' \
                                      ,round(chisq,3), '& \\multicolumn{4}{|c}{} \\\\ \n' \
                                      ,'\\multicolumn{4}{c|}{} & VLSS &', vlssid ,'&' \
                                      ,round(vlssflux,3) ,'$\pm$' \
                                      ,round(vlssfluxerror,3) ,'&' \
                                      ,round(vlss_r,3) ,'&' \
                                      ,round(vlss_logLR,3) ,'\\\\ \n' \
                                      ,'\\multicolumn{4}{c|}{} & WENSS &', wenssid , wenssastr ,'&' \
                                      ,round(wenssflux,3) ,'$\pm$' \
                                      ,round(wenssfluxerror,3) ,'&' \
                                      ,round(wenss_r,3) ,'&' \
                                      ,round(wenss_logLR,3) ,'&' \
                                      ,'\\multicolumn{4}{c|}{} & NVSS &', nvssid ,'&' \
                                      ,round(nvssflux,3) ,'$\pm$' \
                                      ,round(nvssfluxerror,3) ,'&' \
                                      ,round(nvss_r,3) ,'&' \
                                      ,round(nvss_logLR,3) ,'\\\\' \
                                      , '\033[1;m'
                else:
                    print base[5] ,'&' \
                                      ,base[6] ,'&' \
                                      ,round(pylab.log10(vlssflux/wenssflux)/pylab.log10(vlssfreq/wenssfreq),3) ,'&' \
                                      ,round(pylab.log10(wenssflux/nvssflux)/pylab.log10(wenssfreq/nvssfreq),3) ,'&' \
                                      ,round(spec_index,3) ,'&' \
                                      ,round(chisq,3), '& \\multicolumn{4}{|c}{} \\\\ \n' \
                                      ,'\\multicolumn{4}{c|}{} & VLSS &', vlssid ,'&' \
                                      ,round(vlssflux,3) ,'$\pm$' \
                                      ,round(vlssfluxerror,3) ,'&' \
                                      ,round(vlss_r,3) ,'&' \
                                      ,round(vlss_logLR,3) ,'\\\\ \n' \
                                      ,'\\multicolumn{4}{c|}{} & WENSS &', wenssid, wenssastr,'&' \
                                      ,round(wenssflux,3) ,'$\pm$' \
                                      ,round(wenssfluxerror,3) ,'&' \
                                      ,round(wenss_r,3) ,'&' \
                                      ,round(wenss_logLR,3) ,'\\\\ \n' \
                                      ,'\\multicolumn{4}{c|}{} & NVSS &', nvssid ,'&' \
                                      ,round(nvssflux,3) ,'$\pm$' \
                                      ,round(nvssfluxerror,3) ,'&' \
                                      ,round(nvss_r,3) ,'&' \
                                      ,round(nvss_logLR,3) ,'\\\\'
                #print base[0],spec_index,chisq
                #print '\t', base[1],base[2],assoc[1][0],assoc[2][0],assoc[1][1],assoc[2][1]
                #print '\t\t', np.linalg.lstsq(np.vstack([np.array([pylab.log10(base[1]),pylab.log10(assoc[1][0]),pylab.log10(assoc[1][1])]), np.ones(3)]).T,np.array([pylab.log10(base[2]),pylab.log10(assoc[2][0]),pylab.log10(assoc[2][1])]))[0][0]
                #sources[0].append(base)
                #sources[1].append(assoc)
            # base[0],[2],[4] := id,freq,int_flux, respectively
            base = []
            base.append(y[i][0]) # [0] id
            base.append(y[i][1]) # [1] cat_id
            base.append(y[i][2]) # [2] freq
            base.append(y[i][4]) # [3] int_flux
            base.append(y[i][5]) # [4] int_flux error
            base.append(y[i][12]) # [5]
            base.append(y[i][13]) # [6]
            base.append(y[i][14]) # [7] orig_catsrcid
            base.append(y[i][16]) # [8] assoc_r
            base.append(y[i][17]) # [9] assoc_lr
            assoc = [[],[],[],[],[],[],[],[]]
            assoc[0].append(y[i][6]) # id
            assoc[1].append(y[i][7]) # cat_id
            assoc[2].append(y[i][8]) # freq
            assoc[3].append(y[i][10]) # int_flux
            assoc[4].append(y[i][11]) # int_flux error
            assoc[5].append(y[i][15]) # orig_catsrcid
            assoc[6].append(y[i][18]) # assoc_r
            assoc[7].append(y[i][19]) # assoc_lr
        else:
            assoc[0].append(y[i][6])
            assoc[1].append(y[i][7])
            assoc[2].append(y[i][8])
            assoc[3].append(y[i][10])
            assoc[4].append(y[i][11])
            assoc[5].append(y[i][15]) 
            assoc[6].append(y[i][18])
            assoc[7].append(y[i][19])
        prev_id = base_id
    #print '\t',sources
    #print "len(sources)", len(sources)
    print "Average spectral index: ", sum(spec_index_avg)/len(spec_index_avg)

            
    conn.commit()

    cursor.close()
    
    print "len(a1) =",len(alpha_1),"; len(a2) =",len(alpha_2)
    print "min(a1) =",min(alpha_1),"; min(a2) =",min(alpha_2)
    print "max(a1) =",max(alpha_1),"; max(a2) =",max(alpha_2)
    
    plotfiles = []
    p=0
    fig=pylab.figure(figsize=(6,6))
    xmin=-4.
    ymin=-4.
    xmax=2.0
    ymax=2.0
    x = pylab.linspace(xmin,xmax,len(alpha_1))
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel(r'$\alpha_1$ (74-325)MHz')
    ax1.set_ylabel(r'$\alpha_2$ (325-1400)MHz')
    ax1.scatter(alpha_1,alpha_2,color='r',marker='o',s=5)
    ax1.plot(x,x,'b--')
    ax1.set_xlim(xmin=xmin,xmax=xmax)
    ax1.set_ylim(ymin=ymin,ymax=ymax)
    ax1.grid(True)
    plotfiles.append('dbtest_2indexdistr.eps')
    pylab.savefig(plotfiles[p],dpi=600)

    print plotfiles

    logf.close()
    print "Results stored in log file:\n", lf
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    logf.write("Failed on query nr %s reason: %s " % (query, e))
    logf.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

