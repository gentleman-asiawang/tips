// utils/logger.ts
import log from 'loglevel';
import prefix from 'loglevel-plugin-prefix';

prefix.reg(log);
log.enableAll();

const loggers: Record<string, log.Logger> = {};

export function getLogger(name: string): log.Logger {
  if (!loggers[name]) {
    const logger = log.getLogger(name);
    prefix.apply(logger, {
      template: `[${name}] %t %l:`,
    });
    logger.setLevel('silent'); // 默认关闭，防止无关模块输出
    loggers[name] = logger;
  }
  return loggers[name];
}