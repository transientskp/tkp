"""
functions for calculating noise levels of LOFAR equipment

more info:
http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti
"""
import math
import scipy.constants
import scipy.interpolate

def parse_antennafile(positionsFile):
    """
    This parses the files in LOFAR/MAC/Deployment/data/StaticMetaData/AntennaArrays in the LOFAR system software repo.
    """
    file_handler = open(positionsFile, 'r')
    parsed = {}
    state = 0
    array = None
    position = None # where is the station relative to the centre of the earth
    antennanum = 0
    positions = []
    antennacount = 0

    for line in file_handler:
        line = line.strip()

        if not line or line.startswith('#'):
            continue
        if state == 0: # array type
            array = line
            state = 1
        elif state == 1: # array position
            position = [float(x) for x in line.split()[2:5]]
            state = 2
        elif state == 2: # array properties meta data
            antennanum = int(line.split()[0])
            antennacount = antennanum
            state = 3
        elif state == 3:
            if antennacount > 0:
                positions.append([float(x) for x in line.split()])
                antennacount -= 1
            else:
                assert(line == "]")
                state = 0
                parsed[array] = positions
                positions = []
    return parsed

def shortest_distances(coordinates, full_array):
    """
    coordinates - a list of 3 value tuples that represent x,y and
                  z coordinates of a subset of the array
    full_array  - a list of x,y,z coordinates of a full array

    returns a list of distances for each antenna relative to its
    closest neighbour

    """
    distances = []
    for a in coordinates:
        shortest_distance = None
        for b in coordinates:
            distance = pow((a[0] - b[0]), 2) + pow((a[1] - b[1]), 2) + pow((a[2] - b[2]), 2)
            if distance > 0.1 and (distance < shortest_distance or not shortest_distance):
                shortest_distance = distance
        distances.append(shortest_distance)
    return [math.sqrt(x) for x in distances]

def noise_level(frequency, subbandwidth, intgr_time, subbands=1, channels=64, Ncore=24, Nremote=16, Nintl=8, inner=True):
    """
    bandwidth - in Hz (should be 144042.96875 (144 kHz) or 180053.7109375 (180 kHz))
    intgr_time - in seconds
    inner - in case of LBA, inner or outer
    """
    bandwidth = subbandwidth * subbands
    channelwidth = subbandwidth / channels

    baselines_core = (Ncore * (Ncore - 1)) / 2
    baselines_remote = (Nremote * (Nremote - 1)) / 2
    baselines_intl = (Nintl * (Nintl - 1)) / 2
    baselines_cr = (Ncore * Nremote)
    baselines_ci = (Ncore * Nintl)
    baselines_ri = (Nremote * Nintl)

    SEFD_core, SEFD_remote, SEFD_intl = SEFD(frequency, inner)

    SEFD_cr = math.sqrt(SEFD_core) * math.sqrt(SEFD_remote)
    SEFD_ci = math.sqrt(SEFD_core) * math.sqrt(SEFD_intl)
    SEFD_ri = math.sqrt(SEFD_remote) * math.sqrt(SEFD_intl)

    # factor for increase of noise due to the weighting scheme
    W = 1 # taken from PHP script

    t_core = baselines_core / pow(SEFD_core, 2)
    t_remote = baselines_remote / pow(SEFD_remote, 2)
    t_intl = baselines_intl / pow(SEFD_intl, 2)
    t_cr = baselines_cr / pow(SEFD_cr, 2)
    t_ci = baselines_ci / pow(SEFD_ci, 2)
    t_ri = baselines_ri / pow(SEFD_ri, 2)

    # The noise level in a LOFAR image
    image_sens = W / math.sqrt(4 * bandwidth * intgr_time * ( t_core + t_remote + t_intl + t_cr + t_ci + t_ri))

    # TODO: do we need this?
    #channel_sens = W / math.sqrt(4 * channelwidth * intgr_time * ( t_core + t_remote + t_intl + t_cr + t_ci + t_ri))

    return image_sens

def Aeff_dipole(frequency, distance):
    """
    The effective area of each dipole in the array is determined by its distance to the nearest dipole (d)
    within the full array.
    """
    wavelength = scipy.constants.c/frequency
    if wavelength > 3: # LBA dipole
        return min(pow(wavelength, 2) / 3, (math.pi * pow(distance, 2)) / 4)
    else: # HBA dipole
        return min(pow(wavelength, 2) / 3, 1.5625)

def system_sensitivity(frequency, Aeff):
    wavelength = scipy.constants.c/frequency

    # Ts0 = 60 +/- 20 K for Galactic latitudes between 10 and 90 degrees.
    Ts0 = 60

    # system efficiency factor (~ 1.0)
    n = 1

    # For all LOFAR frequencies the sky brightness temperature is dominated by the Galactic radiation, which depends
    # strongly on the wavelength
    Tsky = Ts0 * wavelength ** 2.55

    #The instrumental noise temperature follows from measurements or simulations
    Tinst = 1 # ?

    Tsys = Tsky + Tinst

    # the total collecting area
    Aeff = 1 # ?

    # SEFD or system sensitivity
    S = (2 * n * scipy.constants.k / Aeff) * Tsys

    return S

def DS():
    # The sensitivity DS (in Jy) of a single dipole (or half an 'antenna')
    DS_dipole = Ssys_dipole / (math.sqrt(2 * bandwidth, intgr_time))

    # An antenna that consists of two (equal) dipoles placed perpendicular to eac
    DS_antenna = DS_dipole / math.sqrt(2)

    # For one station, the overlap in effective area from different dipoles has to be taken into account.
    DS_station = Ssys_station / (math.sqrt(2 * bandwith, intgr_time))

