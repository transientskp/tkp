import unittest
import os
import shutil
import tempfile
import argparse

import tkp.management
from tkp.testutil import nostderr


project_name = 'test_project'
job_name = 'test_job'


class TestManagement(unittest.TestCase):

    def setUp(self):
        self.parent = tempfile.mkdtemp()
        self.target = os.path.join(self.parent, project_name)
        self.start_dir = os.getcwd()

    def tearDown(self):
        shutil.rmtree(self.parent, ignore_errors=True)
        os.chdir(self.start_dir)

    def test_init_project(self):
        """
        test the creation of a TRAP project
        """
        # forced target, target needs to exist
        namespace = argparse.Namespace()
        namespace.name = project_name
        os.mkdir(self.target)
        namespace.target = self.target
        tkp.management.init_project(namespace)
        self.assertTrue(os.access(self.target, os.W_OK))

        # test called from current working dir, target will be created
        shutil.rmtree(self.target)
        os.chdir(self.parent)
        namespace.target = None
        tkp.management.init_project(namespace)
        self.assertTrue(os.access(self.target, os.W_OK))

        self.assertRaises(tkp.management.CommandError,
                            tkp.management.init_project, namespace)
        namespace.target = "DOESNOTEXISTS"
        self.assertRaises(tkp.management.CommandError,
                    tkp.management.init_project, namespace)


    def test_init_job(self):
        """
        test the creation of a TRAP job
        """
        os.chdir(self.parent)
        namespace = argparse.Namespace()
        namespace.name = project_name
        namespace.target = None
        tkp.management.init_project(namespace)
        os.chdir(self.target)

        # test called from current working dir
        tkp.management.init_job(namespace)

        namespace.target = "DOESNOTEXISTS"

        self.assertRaises(tkp.management.CommandError, tkp.management.init_job,
                          namespace)

    def test_run_job(self):
        os.chdir(self.parent)
        namespace = argparse.Namespace()
        namespace.name = project_name
        namespace.target = None
        target = tkp.management.init_project(namespace)
        os.chdir(target)
        job_namespace = argparse.Namespace()
        job_namespace.name = job_name
        job_namespace.method = 'test'
        job_namespace.debug = False
        tkp.management.init_job(job_namespace)
        # we don't want no images!
        images_file = open(os.path.join(self.target,  job_name,
                                        'images_to_process.py'), 'w')
        images_file.write("images=[]\n")
        images_file.close()
        tkp.management.run_job(job_namespace)


    def test_check_if_exists(self):
        file = tempfile.NamedTemporaryFile()
        self.assertTrue(tkp.management.check_if_exists(file.name))
        file.close()
        self.assertRaises(tkp.management.CommandError,
                                    tkp.management.check_if_exists, file.name)

    def test_parse_arguments(self):
        # should raise error if no arguments
        with nostderr():  # don't clutter test results
            self.assertRaises(SystemExit, tkp.management.parse_arguments)

    def test_get_template_dir(self):
        tkp.management.get_template_dir()

    def test_make_writeable(self):
        t = tempfile.NamedTemporaryFile()
        tkp.management.make_writeable(t.name)
        t.close()

    def test_line_replace(self):
        substitutes = [('gijs', 'bart'), ('john', 'tim')]
        line = "gijs john"
        result = tkp.management.line_replace(substitutes, line)

    def test_copy_template(self):
        project_folder = tempfile.mkdtemp()
        tkp.management.copy_template("project", project_name, project_folder)
        shutil.rmtree(project_folder)
        job_folder = tempfile.mkdtemp()
        tkp.management.copy_template("job", job_name, job_folder)
        shutil.rmtree(job_folder)

    def test_prepare_job(self):
        os.chdir(self.parent)
        tkp.management.prepare_job(job_name)
        tkp.management.prepare_job(job_name, debug=True)

    def test_main(self):
        # should raise exception when no arguments
        with nostderr():  # don't clutter test results
            self.assertRaises(SystemExit, tkp.management.main)


if __name__ == '__main__':
    unittest.main()
