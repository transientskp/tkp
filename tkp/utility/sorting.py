"""
Logic for sorting the TRAP input data
"""


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

    """
    img_dict = {}
    for image in images:
        t = image.taustart_ts
        if t in img_dict:
            img_dict[t].append(image)
        else:
            img_dict[t] = [image]

    grouped_images = img_dict.items()

    # sort the timestamps
    grouped_images.sort()

    # and then sort the nested items per freq and stokes
    [l[1].sort(key=lambda x: (x.freq_eff, x.stokes)) for l in grouped_images]
    
    return grouped_images