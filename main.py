from config import OUTPUT_DIR, LOG_DIR
import os
import sys
import logging
from data_query import get_today_date
from excel_report import ExcelReport


# config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'report_assistant.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_database_connection():
    try:
        from db_config import db
        db.connect()
        db.close()
        return True
    except Exception as e:
        logger.error(f"DB connection error: {e}")
        return False


def verify_data_exists(stat_date):
    try:
        from data_query import get_channel_ranking
        data = get_channel_ranking(stat_date)
        if len(data) > 0:
            logger.info(f"Data verification successful for the day, a total of {len(data)} records.")
            return True
        else:
            logger.warning(f"Data for the day is empty: {stat_date}")
            return False
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        return False


def generate_single_report(report_name, query_func, headers):
    try:
        logger.info(f"Generating {report_name}...")

        today = get_today_date()

        data = query_func(today)

        if not data:
            logger.warning(f"{report_name} is null, skipping generation.")
            return False

        # 生成报表
        report_gen = ExcelReport(OUTPUT_DIR)
        report_gen.generate_report(report_name, data, headers)

        logger.info(f"{report_name} generated successfully! A total of {len(data)} records.")
        return True

    except Exception as e:
        logger.error(f"{report_name} generation failed: {e}", exc_info=True)
        return False


def main():
    logger.info("="*60)
    logger.info("                自动化每日数据报表工具")
    logger.info("="*60)

    logger.info("Check the database connection...")
    if not check_database_connection():
        logger.error("Database connection failed, program exiting.")
        sys.exit(1)

    today = get_today_date()
    logger.info(f"Current date: {today}")
    logger.info("Verify the data of the day...")
    if not verify_data_exists(today):
        logger.warning("The data for the day is empty, the data may not have been updated yet.")

    results = []

    from data_query import get_channel_ranking
    result1 = generate_single_report(
        '卫视收视排行榜',
        get_channel_ranking,
        ['日期', '频道', '网络', '平台', '收视率', '收视份额', '排名', '上周排名', '排名变化']
    )
    results.append(('卫视收视排行榜', result1))

    from data_query import get_episode_ranking
    result2 = generate_single_report(
        '剧集收视排行榜',
        lambda d: get_episode_ranking(d, 20),
        ['日期', '频道', '剧集名称', '收视率', '收视份额', '播出类型', '开始时间']
    )
    results.append(('剧集收视排行榜', result2))

    from data_query import get_city_analysis
    result3 = generate_single_report(
        '城市分级收视对比',
        get_city_analysis,
        None 
    )
    results.append(('城市分级收视对比', result3))

    logger.info("="*60)
    logger.info("Summary of results:")
    logger.info("="*60)

    success_count = 0
    for report_name, success in results:
        status = "success" if success else "error"
        logger.info(f"{report_name}: {status}")
        if success:
            success_count += 1

    logger.info("="*60)
    logger.info(f"Total: {success_count}/{len(results)} reports generated successfully!")
    logger.info("="*60)

    return 0 if success_count == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
