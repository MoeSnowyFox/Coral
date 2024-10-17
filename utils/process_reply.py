import os
import json
import re
import random
import logging

class ProcessReply:
    register = None
    config = None
    def __init__(self, register, config):
        self.register = register
        self.config = config
        self.define_functions()

    def define_functions(self):
        if 'process_text' not in self.register.functions:
            logging.warning('process_text function is not registered, process text will not be working.')
            self.process_text = None
        else:
            self.process_text = self.register.execute_function('process_text')
        if 'process_image' not in self.register.functions:
            logging.warning('process_image function is not registered, process image will not be working.')
            self.process_image = None
        else:
            self.process_image = self.register.execute_function('process_image')
        if 'process_video' not in self.register.functions:
            logging.warning('process_video function is not registered, process video will not be working.')
            self.process_video = None
        else:
            self.process_video = self.register.execute_function('process_video')
        if 'process_audio' not in self.register.functions:
            logging.warning('process_audio function is not registered, process audio will not be working.')
            self.process_audio = None
        else:
            self.process_audio = self.register.execute_function('process_audio')
        
    async def process_message(self, message):
        """
        处理格式化消息。
        """
        raw_message = message['raw_message']
        sender_user_id = message['sender_user_id']
        group_id = message['group_id']
        
        is_at_message, at_matches, processed_message = self.process_at_message(raw_message)
        if is_at_message:
            if self.config.get('bot_qq_id') not in at_matches:
                logging.info(f'Received at message from {sender_user_id} in group {group_id}, but it is not for me.')
                return None
        else:
            if self.config.get('at_reply', False):
                logging.info(f'Received message from {sender_user_id} in group {group_id}, but it is not an at message.')
                return None
            
        is_image, image_url = self.is_image_message(processed_message)

        if not is_at_message and not self.config.get('at_reply', False) and not group_id == -1:
            if random.randint(1, 100) >= self.config.get('reply_rate', 100):
                logging.info(f'Received message from {sender_user_id} in group {group_id}, but it is not an at message and reply rate is too low.')
                return None
            
        if is_image and self.process_image:
            send_message = await self.process_image({"image_url": image_url, "sender_user_id": sender_user_id, "group_id": group_id})
        elif self.process_text:
            if 'process_message' in self.register.event_queues:
                processed_message, sender_user_id, group_id = await self.register.execute_event('process_message', {"message": processed_message, "sender_user_id": sender_user_id, "group_id": group_id})
            send_message = await self.process_text({"message": processed_message, "sender_user_id": sender_user_id, "group_id": group_id})
        else:
            logging.warning('No process function is registered, message will not be processed.')
            return None
        return send_message

    def is_image_message(self, message: str) -> tuple[bool, str]:
        """
        判断是否是图片消息。
        Args:
        - data (Any): 消息数据。
        Returns:
        - tuple: 包含两个元素：
            - is_image (bool): 是否是图片消息。
            - image_url (str): 图片 URL。
        """
        url_pattern = r"url=(https?[^,]+)"
        image_match = re.search(url_pattern, message)
        if image_match:
            image_url = image_match.group(1)
            return True, image_url
        url_pattern = r"url=(file[^,]+)"
        image_match = re.search(url_pattern, message)
        if image_match:
            image_url = image_match.group(1)
            return True, image_url
        else:
            return False, ''
        
    def process_at_message(self, message: str) -> tuple[bool, list, str]:
        """
        处理消息中的 @ 提及信息。
        Args:
        - message (Any): 输入的消息数据。
        Returns:
        - tuple: 包含三个元素：
            - is_at_message (bool): 是否是 @ 提及消息。
            - at_matches (list): 有匹配的 @ 提及集合。
            - processed_message (str): 处理后的消息字符串。
        """
        at_pattern = re.compile(r'\[CQ:at,qq=(\d+)(?:,name=\w+)?\]')
        at_matches = at_pattern.findall(message)
        if at_matches:
            processed_message = at_pattern.sub(lambda m: '', message)
            return True, at_matches, processed_message
        else:
            return False,at_matches, message