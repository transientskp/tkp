--SELECT NOW();
CALL InsertVersion();

--SELECT NOW();
--CALL BuildZones(1);

--SELECT NOW();
CALL BuildFrequencyBands();

CALL BuildNodes(-90,90, FALSE);

--SELECT NOW();
--CALL BuildAssociationClass();

--SELECT NOW();
--CALL LoadLSM(158,164.5,18.5,24.5,'NVSS','VLSS','');


