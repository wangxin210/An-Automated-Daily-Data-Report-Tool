import os
import sys
import logging
from datetime import datetime

# config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_database_connection():
    logger.info("="*50)
    logger.info("Test1: DB connection")
    logger.info("="*50)

    try:
        from db_config import db, DB_CONFIG
        logger.info(f"DB_CONFIG: {DB_CONFIG['database']}")

        db.connect()
        logger.info("DB connection success!")

        cursor = db.get_cursor()
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()
        logger.info(f"DB_VERSION: {version['version']}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.info(f"DB_TABLES: {len(tables)}")

        for table in tables:
            table_name = list(table.values())[0]
            logger.info(f"  - {table_name}")

        db.close()
        return True

    except Exception as e:
        logger.error(f"DB Test Error: {e}")
        return False


def test_data_query():
    logger.info("\n" + "="*50)
    logger.info("Test2: Query")
    logger.info("="*50)

    try:
        from data_query import (
            get_today_date,
            get_channel_ranking,
            get_episode_ranking,
            get_city_analysis,
            get_channel_summary,
            get_best_episode_channels
        )

        today = get_today_date()
        logger.info(f"Today: {today}")

        logger.info("  卫视收视排行榜...")
        channel_data = get_channel_ranking(today)
        logger.info(f"Query success, a total of {len(channel_data)} records.")
        if channel_data:
            logger.info(f"  example: {channel_data[0]}")

        logger.info("  剧集收视排行榜...")
        episode_data = get_episode_ranking(today, 5)
        logger.info(f"Query success, a total of {len(episode_data)} records.")
        if episode_data:
            logger.info(f"  example: {episode_data[0]}")

        logger.info("  城市分级对比分析...")
        city_data = get_city_analysis(today)
        logger.info(f"Query success, a total of {len(city_data)} records.")
        if city_data:
            logger.info(f"  example: {city_data[0]}")

        logger.info("  频道收视概况...")
        channel_summary = get_channel_summary(today)
        logger.info(f"Query success, a total of {len(channel_summary)} records.")
        if channel_summary:
            logger.info(f"  example: {channel_summary[0]}")

        logger.info("  Top5剧集...")
        best_episodes = get_best_episode_channels(today, 5)
        logger.info(f"Query success, a total of {len(best_episodes)} records.")
        if best_episodes:
            logger.info(f"  example: {best_episodes[0]}")

        return True

    except Exception as e:
        logger.error(f"Query Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_generation():
    logger.info("\n" + "="*50)
    logger.info("Test3: Excel Generation")
    logger.info("="*50)

    try:
        from data_query import get_channel_ranking, get_today_date
        from excel_report import ExcelReport

        today = get_today_date()
        logger.info(f"Today: {today}")

        data = get_channel_ranking(today)
        logger.info(f"Get data: {len(data)}")

        report_gen = ExcelReport('output')
        filename = report_gen.generate_report(
            'Test_卫视收视排行榜',
            data,
            ['日期', '频道', '网络', '平台', '收视率', '收视份额', '排名', '上周排名', '排名变化']
        )

        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            logger.info(f"Generation success: {filename}")
            logger.info(f" FILE_SIZE: {file_size/1024:.2f} KB")
        else:
            logger.error(f"Generation Error: {filename}")
            return False

        return True

    except Exception as e:
        logger.error(f"Generation Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_output_files():
    logger.info("\n" + "="*50)
    logger.info("Output")
    logger.info("="*50)

    output_dir = 'output'
    if not os.path.exists(output_dir):
        logger.warning(f"Output is not existing: {output_dir}")
        return

    files = []
    for filename in os.listdir(output_dir):
        if filename.endswith('.xlsx'):
            filepath = os.path.join(output_dir, filename)
            file_size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            files.append((filename, file_size, mtime))

    if files:
        logger.info(f"A total of {len(files)} Excel report files were found:")
        for filename, size, mtime in sorted(files, key=lambda x: x[2], reverse=True):
            logger.info(f"  {filename}")
            logger.info(f"    SIZE: {size/1024:.2f} KB, STRFTIME: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        logger.warning("Not Found")


def main():
    logger.info("="*60)
    logger.info("           自动化每日数据报表工具 - Test")
    logger.info("="*60)

    results = {}

    results['DB Connection'] = test_database_connection()
    results['Data Query'] = test_data_query()
    results['Excel Generation'] = test_excel_generation()

    logger.info("\n" + "="*60)
    logger.info("Test Results Summary")
    logger.info("="*60)

    for test_name, success in results.items():
        status = "Success" if success else "Error"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())

    show_output_files()

    logger.info("\n" + "="*60)
    if all_passed:
        logger.info("All tests passed! The report assistant is running normally.")
    else:
        logger.warning("Some tests failed, please check the configuration.")
    logger.info("="*60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
