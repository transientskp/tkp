import unittest
import trap.management
import os
import sys
import os.path
import shutil
import tempfile

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
        trap.management.init_project(project_name, target)
        self.assertTrue(os.access(target, os.W_OK))

        # test called from current working dir
        shutil.rmtree(target)
        os.chdir(parent)
        trap.management.init_project(project_name)
        self.assertTrue(os.access(target, os.W_OK))

        self.assertRaises(trap.management.CommandError,
                            trap.management.init_project, project_name, target)

        self.assertRaises(trap.management.CommandError,
                    trap.management.init_project, job_name, "DOESNOTEXISTS")


    def test_init_job(self):
        """
        test the creation of a TRAP job
        """
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        trap.management.init_project(project_name)
        os.chdir(target)

        # test called from current working dir
        trap.management.init_job(job_name)
        trap.management.clean_job(job_name)
        trap.management.info_job(job_name)

        self.assertRaises(trap.management.CommandError, trap.management.init_job,
                                                job_name, "DOESNOTEXISTS")

    @unittest.skip("dont work yet somehow")
    def test_run_job(self):
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        trap.management.init_project(project_name)
        os.chdir(target)
        trap.management.init_job(job_name)
        # we don't want no images!
        images_file = open(os.path.join(target, job_name, 'images_to_process.py'), 'w')
        images_file.write("images=[]\n")
        trap.management.run_job(job_name)

    def test_check_if_exists(self):
        file = tempfile.NamedTemporaryFile()
        self.assertTrue(trap.management.check_if_exists(file.name))
        file.close()
        self.assertRaises(trap.management.CommandError,
                                    trap.management.check_if_exists, file.name)

    def test_parse_arguments(self):
        # should raise error if no arguments
        self.assertRaises(SystemExit, trap.management.parse_arguments)

    def test_get_template_dir(self):
        trap.management.get_template_dir()

    def test_make_writeable(self):
        t = tempfile.NamedTemporaryFile()
        trap.management.make_writeable(t.name)

    def test_line_replace(self):
        substitutes = [('gijs', 'bart'), ('john', 'tim')]
        line = "gijs john"
        result = trap.management.line_replace(substitutes, line)


    def test_copy_template(self):
        target = tempfile.mkdtemp()
        trap.management.copy_template("project", project_name, target)
        trap.management.copy_template("job", job_name, target)

    def test_prepare_job(self):
        trap.management.prepare_job(job_name)
        trap.management.prepare_job(job_name, debug=True)

    @unittest.skip("dont work yet somehow")
    def test_runlocal_job(self):
        # cleanup
        if os.access(target, os.X_OK):
            shutil.rmtree(target)
        os.chdir(parent)
        trap.management.init_project(project_name)
        os.chdir(target)
        trap.management.init_job(job_name)

        images_file = open(os.path.join(target, job_name, 'images_to_process.py'), 'w')
        images_file.write("images=[]\n")
        sys.path.append(os.path.join(target, job_name))
        import logging
        logging.debug(sys.path)
        trap.management.runlocal_job(job_name)
        #trap.management.runlocal_job(job_name, debug=True)

    def test_clean_job(self):
        trap.management.clean_job(job_name)

    def test_info_job(self):
        t = tempfile.mkdtemp()
        os.chdir(t)
        trap.management.init_job(job_name)
        trap.management.info_job(job_name)

    def test_main(self):
        # should raise exception when no arguments
        self.assertRaises(SystemExit, trap.management.main)


if __name__ == '__main__':
    unittest.main()
