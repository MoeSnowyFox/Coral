import os
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def register_function(register, config):
    register.register_function('install_pip_requirements', InstallRequirements(config).install_pip_requirements)
    register.register_function('check_pip_requirements', InstallRequirements(config).check_pip_requirements)

class InstallRequirements:
    config = None

    def __init__(self, config):
        self.config = config
        
    async def install_pip_requirements(self, requirements_file):
        if not os.path.exists(requirements_file):
            logger.error("Requirements file not found: {}".format(requirements_file))
            return False
        index_url = self.config.get('index_url', 'https://pypi.tuna.tsinghua.edu.cn/simple')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-i', index_url, '-r', requirements_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to install requirements: {}".format(e))
            return False
        return True
    
    async def check_pip_requirements(self, requirements_file):
        if not os.path.exists(requirements_file):
            logger.error("Requirements file not found: {}".format(requirements_file))
            return False
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('#') or line.strip() == '':
                continue
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'show', line.strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                logger.error("Failed to check requirement: {}".format(line.strip()))
                return False
        return True