C FILE deconv.f
C 
C Deconvolves two Gaussians; originally from AIPS.
C Adapted for use with f2py, JDS, 14 Jan 2009.
C
C Build with:
C  $ f2py -c -m deconv deconv.f
C Then, in python:
C  from deconv import deconv
C  rmaj, rmin, rpa, ierr = deconv(fmaj, fmin, fpa, cmaj, cmin, cpa)
C
      SUBROUTINE DECONV (FMAJ, FMIN, FPA, CMAJ, CMIN, CPA, RMAJ, RMIN,
     *   RPA, IERR)
C-----------------------------------------------------------------------
C! deconvolves two gaussians
C# Modeling
C-----------------------------------------------------------------------
C;  Copyright (C) 1995, 2001, 2003
C;  Associated Universities, Inc. Washington DC, USA.
C;
C;  This program is free software; you can redistribute it and/or
C;  modify it under the terms of the GNU General Public License as
C;  published by the Free Software Foundation; either version 2 of
C;  the License, or (at your option) any later version.
C;
C;  This program is distributed in the hope that it will be useful,
C;  but WITHOUT ANY WARRANTY; without even the implied warranty of
C;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
C;  GNU General Public License for more details.
C;
C;  You should have received a copy of the GNU General Public
C;  License along with this program; if not, write to the Free
C;  Software Foundation, Inc., 675 Massachusetts Ave, Cambridge,
C;  MA 02139, USA.
C;
C;  Correspondence concerning AIPS should be addressed as follows:
C;         Internet email: aipsmail@nrao.edu.
C;         Postal address: AIPS Project Office
C;                         National Radio Astronomy Observatory
C;                         520 Edgemont Road
C;                         Charlottesville, VA 22903-2475 USA
C-----------------------------------------------------------------------
C   DECONV deconvolves a gaussian "beam" from a gaussian component.
C   Inputs:
C      FMAJ   R    Fitted major axis
C      FMIN   R    Fitted minor axis
C      FPA    R    Fitted position angle of major axis
C      CMAJ   R    Point source major axis
C      CMIN   R    Point source minor axis
C      CPA    R    Point source position angle of major axis
C   Outputs:
C      RMAJ   R    Real major axis; = 0 => unable to fit
C      RMIN   R    Real minor axis; = 0 => unable to fit
C      RPA    R    Real position angle of major axis
C      IERR   I    Error return: 0 => ok
C                         1,2-> # components unable to deconvolve
C-----------------------------------------------------------------------
      INTEGER   IERR
      DOUBLE PRECISION FMAJ, FMIN, FPA, CMAJ, CMIN, CPA, RMAJ, RMIN, 
     * RPA
Cf2py intent(in), docstring(foo) :: fmaj
Cf2py intent(out) rmaj
Cf2py intent(out) rmin
Cf2py intent(out) rpa
Cf2py intent(out) ierr
C
      DOUBLE PRECISION CMJ2, CMN2, FMJ2, FMN2, SINC, COSC, CONST, RHOC, 
     * SIGIC2, DET, RHOA, LFPA, LCPA
      DATA CONST /28.647888/
C-----------------------------------------------------------------------
C                                       Get useful constants
      LFPA = MOD (FPA+900.0, 180.0)
      LCPA = MOD (CPA+900.0, 180.0)
      CMJ2 = CMAJ * CMAJ
      CMN2 = CMIN * CMIN
      FMJ2 = FMAJ * FMAJ
      FMN2 = FMIN * FMIN
      SINC = (LFPA - LCPA) / CONST
      COSC = COS(SINC)
      SINC = SIN(SINC)
C                                       Trigonometry now
      RHOC = (FMJ2 - FMN2) * COSC - (CMJ2 - CMN2)
      IF (RHOC.EQ.0.0) THEN
         SIGIC2 = 0.0
         RHOA = 0.0
      ELSE
         SIGIC2 = ATAN((FMJ2 - FMN2) * SINC / RHOC)
         RHOA = ((CMJ2 - CMN2) - (FMJ2 - FMN2) * COSC) /
     *      (2.0 * COS(SIGIC2))
         END IF
      RPA = SIGIC2 * CONST + LCPA
      DET = ((FMJ2 + FMN2) -(CMJ2 + CMN2)) / 2.0
      RMAJ = DET - RHOA
      RMIN = DET + RHOA
      IERR = 0
      IF (RMAJ.LT.0.0) IERR = IERR + 1
      IF (RMIN.LT.0.0) IERR = IERR + 1
C                                       Swap to get major > minor
      RMAJ = MAX (0.0, RMAJ)
      RMIN = MAX (0.0, RMIN)
      RMAJ = SQRT (ABS (RMAJ))
      RMIN = SQRT (ABS (RMIN))
      IF (RMAJ.LT.RMIN) THEN
         SINC = RMAJ
         RMAJ = RMIN
         RMIN = SINC
         RPA = RPA+90.0
         END IF
C                                       Fix up PA
      RPA = MOD (RPA+900.0, 180.0)
      IF (RMAJ.EQ.0.0) THEN
         RPA = 0.0
      ELSE IF (RMIN.EQ.0.0) THEN
         IF ((ABS(RPA-LFPA).GT.45.0) .AND. (ABS(RPA-LFPA).LT.135.0))
     *      RPA = MOD (RPA+450.0, 180.0)
         END IF
C
      RETURN
      END
C END FILE deconv.f
