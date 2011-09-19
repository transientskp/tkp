# Example data input file to be used with trap.py
#
# Quick way of priming the pipeline with a list of datafiles to be processed.
# Generate this file by, eg:
#
# $ obsid=L2010_20850; for i in `seq 0 7`; do ssh lce`printf %03d $((i*9+1))` ls /net/sub$((i+1))/lse*/data*/$obsid/* | grep SB >> to_process.py; done
#
# then tweak with your favourite text editor.


datafiles = [
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB101-uv.MS.dppp.dppp.dppp',
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB103-uv.MS.dppp.dppp.dppp',
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB104-uv.MS.dppp.dppp.dppp',
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB106-uv.MS.dppp.dppp.dppp',
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB107-uv.MS.dppp.dppp.dppp',
    '/zfs/heastro-plex/scratch/evert/trap/L2010_20850_1/L20850_SB108-uv.MS.dppp.dppp.dppp',
]
