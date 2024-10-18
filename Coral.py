import os
import threading
import time
import logging
import asyncio
from pyfiglet import Figlet
from colorama import init, Fore

import utils.commands
import utils.install_requirements
from utils.auto_prompt import AutoPrompt
from utils.reverse_ws import ReverseWS
from utils.config import Config
from utils.process_reply import ProcessReply

from core.register import Register
from core.plugin_manager import PluginManager

class Coral:
    def __init__(self):
        textrender=Figlet(font="larry3d")
        print(Fore.GREEN + textrender.renderText("Project Coral") + Fore.RESET)
        asyncio.run(self.initialize())
        self.run()
        
    async def initialize(self):
        plugin_dir = "./plugins"
        config_file = "./config.json"
        self.config = Config(config_file)
        self.register = Register()
        self.plugin_manager = PluginManager(self.register, self.config)

        self.plugin_manager.plugins.append("base_commands")
        utils.commands.register_command(self.register, self.config)
        utils.install_requirements.register_function(self.register, self.config)
        await self.plugin_manager.load_plugins()

        self.process_reply = ProcessReply(self.register, self.config)
        threading.Thread(target=self.ws_thread, args=(self.config,self.register,self.process_reply.process_message),).start()
        
        AutoPrompt.load_commands(self.register.commands)

    def run(self):
        try:
            while True:
                im_text = AutoPrompt.prompt()
                response = self.register.execute_command(im_text)
                print(response)
        except KeyboardInterrupt:
            os._exit(0)

    def ws_thread(self, config, register, process_reply):
        logging.info("Starting WebSocket Server...")
        try:
            ReverseWS(config, register, process_reply).start()
        except KeyboardInterrupt:
            pass
