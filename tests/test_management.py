

import unittest
import trap.management
import os
import os.path
import shutil

project_name = 'test_project'
job_name = 'test_job'
parent = '/tmp'
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

        # raise error when dir already exists
        #trap.management.initproject(project_name, target=target)
        self.assertRaises(trap.management.CommandError, trap.management.init_project, project_name, target)

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

if __name__ == '__main__':
    unittest.main()
