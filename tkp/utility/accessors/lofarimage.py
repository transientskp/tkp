
from tkp.utility.accessors.dataaccessor import DataAccessor

class LofarImage(DataAccessor):
    def __init__(self, source, plane=False, beam=False, hdu=0):
        super(LofarImage, self).__init__()  # Set defaults

        self.data = source["map"]
        coordinfo = source["/coordinfo"]
        attrgroups = source["/ATTRGROUPS"]

        lofar_antenna = attrgroups["LOFAR_ANTENNA"]
        lofar_field = attrgroups['LOFAR_FIELD']
        lofar_history = attrgroups['LOFAR_HISTORY']
        lofar_observation = attrgroups['LOFAR_OBSERVATION']
        lofar_origin = attrgroups['LOFAR_ORIGIN']
        lofar_source = attrgroups['LOFAR_SOURCE']
        lofar_station = attrgroups['LOFAR_STATION']

        filename = source.attrs['FILENAME']
        filedate = source.attrs['FILEDATE']
        filetype = source.attrs['FILETYPE']
        telescope = source.attrs['TELESCOPE']
        observer = source.attrs['OBSERVER']
        project_id = source.attrs['PROJECT_ID']
        project_title = source.attrs['PROJECT_TITLE'],
        project_pi = source.attrs['PROJECT_PI']
        project_co_i = source.attrs['PROJECT_CO_I']
        project_contact = source.attrs['PROJECT_CONTACT']
        observation_id = source.attrs['OBSERVATION_ID']
        observation_start_mjd = source.attrs['OBSERVATION_START_MJD']
        observation_start_utc = source.attrs['OBSERVATION_START_UTC']
        observation_end_mjd = source.attrs['OBSERVATION_END_MJD']
        observation_end_utc = source.attrs['OBSERVATION_END_UTC']
        observation_nof_station = source.attrs['OBSERVATION_NOF_STATIONS']
        observation_stations_list = source.attrs['OBSERVATION_STATIONS_LIST']
        observation_frequency_max = source.attrs['OBSERVATION_FREQUENCY_MAX']
        observation_frequency_min = source.attrs['OBSERVATION_FREQUENCY_MIN']
        observation_frequency_center = source.attrs['OBSERVATION_FREQUENCY_CENTER']
        observation_frequency_unit = source.attrs['OBSERVATION_FREQUENCY_UNIT']
        observation_nof_bits_per_sample = source.attrs['OBSERVATION_NOF_BITS_PER_SAMPLE']
        clock_frequency = source.attrs['CLOCK_FREQUENCY']
        clock_frequency_unit = source.attrs['CLOCK_FREQUENCY_UNIT']
        antenna_set = source.attrs['ANTENNA_SET']
        filter_selection = source.attrs['FILTER_SELECTION']
        target = source.attrs['TARGET']
        system_version = source.attrs['SYSTEM_VERSION']
        pipeline_name = source.attrs['PIPELINE_NAME']
        pipeline_version = source.attrs['PIPELINE_VERSION']
        notes = source.attrs['NOTES']

