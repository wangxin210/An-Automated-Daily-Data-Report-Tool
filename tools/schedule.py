from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import os
from config import LOG_DIR, OUTPUT_DIR, FILE_NAME_TEMPLATE
from data_query import (
    get_channel_ranking,
    get_episode_ranking,
    get_city_analysis,
    get_channel_summary,
    get_best_episode_channels
)
from excel_report import ExcelReport

# config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'report_assistant.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ReportScheduler:

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(
            self.generate_daily_reports,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_report',
            name='每日报表生成',
            replace_existing=True
        )
        self.report_gen = ExcelReport(OUTPUT_DIR)

    def generate_daily_reports(self):
        logger.info("="*50)
        logger.info("Starting to generate the daily data report...")
        logger.info("="*50)

        try:
            today = datetime.now().strftime('%Y-%m-%d')
            logger.info(f"生成日期: {today}")

            logger.info("卫视收视排行榜...")
            channel_data = get_channel_ranking(today)
            headers = ['日期', '频道', '网络', '平台', '收视率', '收视份额', '排名', '上周排名', '排名变化']
            self.report_gen.generate_report('卫视收视排行榜', channel_data, headers)
            logger.info("Success!")

            logger.info("剧集收视排行榜...")
            episode_data = get_episode_ranking(today)
            headers = ['日期', '频道', '剧集名称', '收视率', '收视份额', '播出类型', '开始时间']
            self.report_gen.generate_report('剧集收视排行榜', episode_data, headers)
            logger.info("Success!")

            logger.info("城市分级收视对比分析...")
            city_data = get_city_analysis(today)

            group1_data = []
            group2_data = []
            for item in city_data:
                if item[0] == '重点城市':
                    group1_data.append([item[0], item[1]])
                else:
                    group2_data.append([item[0], item[1]])

            self.report_gen.generate_comparison_report(
                '城市分级收视对比',
                group1_data,
                group2_data,
                '重点城市',
                '普通城市'
            )
            logger.info("Success!")

            logger.info("频道收视概况...")
            channel_summary = get_channel_summary(today)
            best_episodes = get_best_episode_channels(today)

            summary_dict = {
                '生成日期': today,
                '卫视总数': len(channel_summary),
                '首播剧数量': len(best_episodes),
                '总频道数': len(channel_summary),
            }

            self.report_gen.generate_summary_report('频道收视概况', summary_dict)

            if channel_summary:
                headers = ['频道', '播出天数', '平均收视率', '峰值收视率', '最低收视率', '平均收视份额']
                self.report_gen.generate_report('频道收视详细', channel_summary, headers)

            if best_episodes:
                headers = ['频道', '剧集名称', '播出天数', '平均收视率', '平均收视份额']
                self.report_gen.generate_report('剧集收视详细', best_episodes, headers)

            logger.info("="*50)
            logger.info("All Success!")
            logger.info("="*50)

        except Exception as e:
            logger.error(f"Generation Error: {e}", exc_info=True)

    def start(self):
        logger.info("Starting...")
        logger.info("Scheduled task: starts daily at XX.")
        self.scheduler.start()


def run_single_report():
    """
    Test
    """
    logger.info("="*50)
    logger.info("Generating...")
    logger.info("="*50)

    scheduler = ReportScheduler()
    scheduler.generate_daily_reports()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test
        run_single_report()
    else:
        # Scheduled task
        scheduler = ReportScheduler()
        scheduler.start()
