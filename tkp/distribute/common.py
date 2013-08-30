import ConfigParser
import os
import tarfile
import cStringIO
import tempfile


def load_job_config(pipe_config):
    """Pulls the parset filenames as defined in the tasks.cfg config file.

    Since each parset has its own section, these can all be read into a
    combined ConfigParser object representing the 'job settings', i.e.
    the parameters relating to this particular data reduction run.
    """
    task_parsets_to_read = ['persistence',
                            'quality_check',
                            'source_association',
                            'source_extraction',
                            'null_detections',
                            'transient_search']
    parset_directory = pipe_config.get('layout', 'parset_directory')
    parset_files_to_read = [os.path.join(parset_directory, taskname + '.parset')
                                for taskname in task_parsets_to_read]
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(parset_files_to_read)
    return job_config


def dump_job_config_to_logdir(pipe_config, job_config):
    log_dir = os.path.dirname(pipe_config.get('logging', 'log_file'))
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'jobpars.parset'), 'w') as f:
        job_config.write(f)


def serialize(path):
    """
    Tars and base64 encodes a file or folder.
    """
    tar_buf = cStringIO.StringIO()
    tar = tarfile.open(fileobj=tar_buf, mode='w:')
    basename = os.path.basename(path)
    tar.add(path, arcname=basename)
    tar.close()
    data = tar_buf.getvalue()
    encoded = data.encode("base64")
    return encoded


def deserialize(encoded, path=False):
    """
    extracts a base64 encoded tar archive in a temporary folder, and returns
    the path. path is used for extraction location, of False a temporary folder
    is created.
    """
    if not path:
        path = tempfile.mkdtemp()
    data = encoded.decode("base64")
    tar_buf = cStringIO.StringIO()
    tar_buf.write(data)
    tar_buf.seek(0)
    tar = tarfile.open(fileobj=tar_buf, mode='r:')
    tar.extractall(path)
    return path

