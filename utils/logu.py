import logging
import os
import sys
import loguru
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

LOG_LEVEL='info'
LOG_DIR=Path(__file__).absolute().parent.parent/'output'/'log'
LOG_DIR.mkdir(parents=True, exist_ok=True)
# python_xx/site-packages/loguru/_handler.py  _serialize_record
FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{file}:{line}</cyan> :<cyan>{function}</cyan> - {message}'
loguru.logger.remove()
# logger.add(sys.stderr, format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>')
# logger.add(sys.stderr, format=FORMAT)
# logger.add(LOG_FILE, format=FORMAT)

loggers = {} 
FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{file}:{line}</cyan> :<cyan>{function}</cyan> - {message}'

def get_logger(name, console=True, console_level="INFO", file=True, file_level="DEBUG"):  
    '''
    用法
        # 创建普通日志，并且启用控制台输出，默认保存到 {LOG_DIR}/default.log 文件  
        logger = get_logger("default", console=True) 
        
        # 创建特定名称的日志和日志文件，保存到 {LOG_DIR}/斌的世界/gift.log 文件
        user_log = get_logger("斌的世界/gift")

        # 输出打印测试
        user_log.info("将控制台日志器、文件日志器，添加进日志器对象中")
        logger.info("这是一条info消息")
    '''
    global loggers  
    if name in loggers:  
        return loggers[name]  # 如果已经存在，则直接返回      # 创建用户特定的日志文件  
    log_file = f"{name}.log"  
    # 添加日志处理器，过滤出只包含该用户名的日志记录  
    if file:
        loguru.logger.add(LOG_DIR/log_file,level=file_level, format=FORMAT, filter=lambda record: record["extra"].get("name") == name)
    if console:
        loguru.logger.add(sys.stderr, format=FORMAT,level=console_level, filter=lambda record: record["extra"].get("name") == name)
    user_logger = loguru.logger.bind(name=name)  
    user_logger.info(f"日志文件路径：{LOG_DIR/log_file}")
    loggers[name] = user_logger  
    return user_logger  

logger = get_logger('main')

if __name__ == '__main__':
    user_log = get_logger("斌的世界/gift")
    user_log.info("将控制台日志器、文件日志器，添加进日志器对象中")
    logger.info("这是一条info消息")
