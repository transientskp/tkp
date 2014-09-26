"""
Logic for sorting the TRAP input data
"""

from collections import defaultdict

def group_per_timestep(images):
    """
    groups a list of TRAP images per time step.

    Per time step the images are order per frequency and then per stokes. The
    eventual order is:

    (t1, f1, s1), (t1, f1, s2), (t1, f2, s1), (t1, f2, s2), (t2, f1, s1), ...)
    where:

        * t is time sorted by old to new
        * f is frequency sorted from low to high
        * s is stokes, sorted by ID as defined in the database schema

    Args:
        List of images.

    Returns:
        List of tuples: The list is sorted by timestamp.
            Each tuple has the timestamp as a first element,
            and a list of images sorted by frequency and then stokes
            as the second element.

    """
    timestamp_to_images_map = defaultdict(list)
    for image in images:
        timestamp_to_images_map[image.taustart_ts].append(image)

    #List of (timestamp, [images_at_timestamp]) tuples:
    grouped_images = timestamp_to_images_map.items()

    # sort the tuples by first element (timestamps)
    grouped_images.sort()

    # and then sort the nested items per freq and stokes
    [l[1].sort(key=lambda x: (x.freq_eff, x.stokes)) for l in grouped_images]
    return grouped_images