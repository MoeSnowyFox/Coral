import os
import importlib.util
import logging

logger = logging.getLogger(__name__)
PluginManager_Version = "1.0"

class PluginManager:
    register = None
    config = None

    def __init__(self, register, config):
        self.config = config
        self.plugin_dir = self.config.get("plugin_dir", "./plugins")
        self.register = register
        self.plugins = []

    async def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist, skipping plugin loading")
        else:
            for plugin_name in os.listdir(self.plugin_dir):
                plugin_path = os.path.join(self.plugin_dir, plugin_name)
                if not os.path.isdir(plugin_path):
                    continue
                main_file = os.path.join(plugin_path, 'main.py')
                if not os.path.exists(main_file):
                    continue
                requirements_file = os.path.join(plugin_path,'requirements.txt')
                if os.path.exists(requirements_file):
                    if not await self.register.execute_function("check_pip_requirements", requirements_file):
                        logger.warning(f"Plugin {plugin_name} has unmet requirements, trying to install them")
                        if not await self.register.execute_function("install_pip_requirements", requirements_file):
                            logger.error(f"Failed to install requirements for plugin {plugin_name}, skipping")
                            continue
                spec = importlib.util.spec_from_file_location("main", main_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins.append(plugin_name)
                if hasattr(module, 'register_command'):
                    module.register_command(self.register, self.config)
                if hasattr(module, 'register_event'):
                    module.register_event(self.register, self.config)
                if hasattr(module, 'register_function'):
                    module.register_function(self.register, self.config)
        self.register.register_command("plugins", "List all available plugins", self.show_plugins)
        logger.info(f"Loaded {len(self.plugins)} plugins")

    def show_plugins(self, *args):
        return  "Available plugins:\n" + str(self.plugins) + "\n Running Plugin Manager version "+ PluginManager_Version