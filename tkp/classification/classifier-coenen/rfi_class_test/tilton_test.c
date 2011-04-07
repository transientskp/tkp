/*
 * C snippet for reading test data.
 */


/*
 * Read data.
 */

#include <stdio.h>
#include <math.h>
#include <sys/errno.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>

#define MAXFREQ  128                    /* very VLA specific */
#define MAXTIME  2880                   /* 8-hr, 10-s sampling */

int main(void)
{
 unsigned int data[MAXFREQ][MAXTIME];
 int nf, nt, it, jf, fd;
 size_t nsize;
 union {
   unsigned char *c;
   unsigned int *u;
   int *i;
   float *f;
 } array;

 nsize = MAXFREQ*sizeof(float);
 array.c = (unsigned char *)malloc(nsize);
 if (array.c == (unsigned char *)NULL)
   exit(errno);
 /* */
 fd = open("tilton_test.dat", O_RDWR|O_CREAT, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
 if (fd == -1)
   exit(errno);
 /* */
 nsize = 2*sizeof(unsigned int);
 (void)read(fd, array.u, nsize);
 nf = array.i[0];  nt = array.i[1];
 /* */
 nsize = (size_t)nf*sizeof(float);
 for (it=0; it<nt; it++) {
   (void)read(fd, array.c, nsize);
   for (jf=0; jf<nf; jf++) data[jf][it] = array.u[jf];
 }
 /* */
 if (close(fd) == -1)
   exit(errno);
 else
   exit(0);
}
