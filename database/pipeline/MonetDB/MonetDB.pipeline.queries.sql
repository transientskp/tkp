call buildzones(1,1);
call initpipeline();

INSERT INTO observations (obsid,time_s,description) VALUES (1,20080403140303000,'test images');
INSERT INTO resolutions (resid,major,minor,pa) VALUES (1,1,1,1);
INSERT INTO datasets (dsid,obs_id,res_id,dstype,taustart_timestamp,dsinname) VALUES (1,1,1,1,20080403140303000,'random***');
INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (1,30000000,40000000);

insert into catalogues (catid, catname,fullname) values (1, 'WENSS', 'Westerbork Northern Sky Survey');
COPY 229420 RECORDS INTO cataloguesources FROM '/var/lib/mysql/pipeline/cataloguesources.txt' DELIMITERS ',', '\n';

call testassociatesource(1,1,1,1,330000000,80.1815715219192, 52.5746842083412,6.93139472503e-05 , 9.10939089636e-05,0.428941235911,0.00568632781642,0.227834526497,0.00407939546635,0.05);

select xtrsrcid, assoc_xtrsrcid,assoc_catsrcid,zone,q_peak from extractedsources;
