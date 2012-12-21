

import unittest
import trap.management
import os
import os.path
import shutil
import tempfile

project_name = 'test_project'
job_name = 'test_job'
parent = '/tmp'
target = os.path.join(parent, project_name)

@unittest.skip("not finished yet")
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


    def test_run_job(self):
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

        trap.management.run_job(job_name)

        trap.management.run_job(job_name, False)



    def test_check_if_exists(self):
        file = tempfile.NamedTemporaryFile()
        self.assertTrue(trap.management.check_if_exists(file.name))
        file.close()
        self.assertRaises(trap.management.CommandError,
                                    trap.management.check_if_exists, file.name)

    def test_parse_arguments(self):
        trap.management.parse_arguments()

    def test_get_template_dir(self):
        trap.management.get_template_dir()

    def test_make_writeable(self):
        filename = "TODO"
        trap.management.make_writeable(filename)

    def test_line_replace(self):
        substitutes = "TODO"
        line = "TODO"
        trap.management.line_replace(substitutes, line)

    def test_copy_template(self):
        name = "TODO"
        trap.management.copy_template(project_name, name)
        trap.management.copy_template(job_name, name)
        trap.management.copy_template(project_name, name, "DOESNOTEXISTS")

    def test_prepare_job(self):
        job_name = "TODO"
        debug = "TODO"
        trap.management.prepare_job(job_name)
        trap.management.prepare_job(job_name, debug)

    def test_runlocal_job(self):
        job_name = "TODO"
        debug = "TODO"
        trap.management.runlocal_job(job_name)
        trap.management.runlocal_job(job_name, debug)

    def test_clean_job(self):
        job_name = "TODO"
        trap.management.clean_job(job_name)

    def test_info_job(self):
        job_name = "TODO"
        trap.management.info_job(job_name)

    def test_main(self):
        trap.management.main()


if __name__ == '__main__':
    unittest.main()
