ALTER TABLE extractedsource ADD FOREIGN KEY (ff_runcat) REFERENCES runningcatalog (id);
ALTER TABLE extractedsource ADD FOREIGN KEY (ff_monitor) REFERENCES runningcatalog (id);
