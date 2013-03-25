import unittest
import os
import sys
import shutil
import tempfile

import tkp.management


project_name = 'test_project'
job_name = 'test_job'
parent = tempfile.mkdtemp()
target = os.path.join(parent, project_name)


class TestManagement(unittest.TestCase):
    def test_init_project(self):
        """
        test the creation of a TRAP project
        """
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)

        # test with target
        os.mkdir(target)
        tkp.management.init_project(project_name, target)
        self.assertTrue(os.access(target, os.W_OK))

        # test called from current working dir
        shutil.rmtree(target)
        os.chdir(parent)
        tkp.management.init_project(project_name)
        self.assertTrue(os.access(target, os.W_OK))

        self.assertRaises(tkp.management.CommandError,
                            tkp.management.init_project, project_name, target)

        self.assertRaises(tkp.management.CommandError,
                    tkp.management.init_project, job_name, "DOESNOTEXISTS")


    def test_init_job(self):
        """
        test the creation of a TRAP job
        """
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        tkp.management.init_project(project_name)
        os.chdir(target)

        # test called from current working dir
        tkp.management.init_job(job_name)
        tkp.management.clean_job(job_name)
        tkp.management.info_job(job_name)

        self.assertRaises(tkp.management.CommandError, tkp.management.init_job,
                                                job_name, "DOESNOTEXISTS")

    @unittest.skip("dont work yet somehow")
    def test_run_job(self):
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        tkp.management.init_project(project_name)
        os.chdir(target)
        tkp.management.init_job(job_name)
        # we don't want no images!
        images_file = open(os.path.join(target, job_name, 'images_to_process.py'), 'w')
        images_file.write("images=[]\n")
        tkp.management.run_job(job_name)

    def test_check_if_exists(self):
        file = tempfile.NamedTemporaryFile()
        self.assertTrue(tkp.management.check_if_exists(file.name))
        file.close()
        self.assertRaises(tkp.management.CommandError,
                                    tkp.management.check_if_exists, file.name)

    def test_parse_arguments(self):
        # should raise error if no arguments
        self.assertRaises(SystemExit, tkp.management.parse_arguments)

    def test_get_template_dir(self):
        tkp.management.get_template_dir()

    def test_make_writeable(self):
        t = tempfile.NamedTemporaryFile()
        tkp.management.make_writeable(t.name)

    def test_line_replace(self):
        substitutes = [('gijs', 'bart'), ('john', 'tim')]
        line = "gijs john"
        result = tkp.management.line_replace(substitutes, line)


    def test_copy_template(self):
        target = tempfile.mkdtemp()
        tkp.management.copy_template("project", project_name, target)
        target = tempfile.mkdtemp()
        tkp.management.copy_template("job", job_name, target)

    def test_prepare_job(self):
        tkp.management.prepare_job(job_name)
        tkp.management.prepare_job(job_name, debug=True)

    @unittest.skip("dont work yet somehow")
    def test_runlocal_job(self):
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        tkp.management.init_project(project_name)
        os.chdir(target)
        tkp.management.init_job(job_name)

        images_file = open(os.path.join(target, job_name, 'images_to_process.py'), 'w')
        images_file.write("images=[]\n")
        sys.path.append(os.path.join(target, job_name))
        import logging
        logging.debug(sys.path)
        tkp.management.runlocal_job(job_name)
        #tkp.management.runlocal_job(job_name, debug=True)

    def test_clean_job(self):
        tkp.management.clean_job(job_name)

    def test_info_job(self):
        t = tempfile.mkdtemp()
        os.chdir(t)
        tkp.management.init_job(job_name)
        tkp.management.info_job(job_name)

    def test_main(self):
        # should raise exception when no arguments
        self.assertRaises(SystemExit, tkp.management.main)


if __name__ == '__main__':
    unittest.main()
