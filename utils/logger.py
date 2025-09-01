import json, logging, sys
from typing import Any, Dict

def setup_logger(name: str = "kp5", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload: Dict[str, Any] = {
                "lvl": record.levelname,
                "msg": record.getMessage(),
                "name": record.name,
                "ts": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            }
            if record.exc_info:
                payload["exc"] = self.formatException(record.exc_info)
            extra = getattr(record, "_extra", None)
            if isinstance(extra, dict):
                payload.update(extra)
            return json.dumps(payload, ensure_ascii=False)

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger

log = setup_logger()
