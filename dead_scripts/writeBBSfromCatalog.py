import os
import tkp_lib.gsm2bbs as gsm2bbs
import tkp_lib.database as db

conn=db.connection()

outpath = os.getenv('HOME') + '/dumps/bbs'
outfile = outpath + '/gsm2bbs_decl.txt'

file = gsm2bbs.writeBBSFile(outfile, conn)
print file

