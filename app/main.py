import logging

from dateutil import tz

from .line_client import push_line_text
from .gpt_client import build_prompt, summarize_with_openai


JST = tz.gettz("Asia/Tokyo")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    prompt = build_prompt()
    summary = summarize_with_openai(prompt)

    push_line_text(summary)
    logger.info("Successfully pushed summary to LINE. Summary length: %d characters", len(summary))


if __name__ == "__main__":
    main()
