
def store_to_mongodb(filename, hostname, port, db, logger):
    logger.info(
        "Storing %s to MongoDB database %s on %s port %d" %
        (filename, db, hostname, port)
    )
    try:
        import pymongo
        import gridfs
    except ImportError:
        logger.warn("Could not import MongoDB modules")
        return

    try:
        connection = pymongo.Connection(host=hostname, port=port)
        gfs = gridfs.GridFS(connection[db])
        new_file = gfs.new_file(filename=filename)
        with open(filename, "r") as f:
            new_file.write(f)
        new_file.close()
        connection.close()
    except Exception, e:
        logger.warn("Could not store image to MongoDB: %s" % (str(e)))