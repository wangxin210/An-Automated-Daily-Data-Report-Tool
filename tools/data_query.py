import datetime
from db_config import db

def get_today_date():
    return datetime.date.today().strftime('%Y-%m-%d')


def get_channel_ranking(stat_date=None):
    """
    卫视收视排行榜
    """
    if not stat_date:
        stat_date = get_today_date()

    query = """
    SELECT
        d.stat_date,
        c.name AS '频道',
        c.network AS '网络',
        c.platform AS '平台',
        d.rating AS '收视率',
        d.market_share AS '收视份额',
        d.rank AS '排名',
        d.prev_rank AS '上周排名',
        CASE
            WHEN d.rank < d.prev_rank THEN '↑ ' || d.prev_rank
            WHEN d.rank > d.prev_rank THEN '↓ ' || d.prev_rank
            ELSE d.prev_rank
        END AS '上周排名变化'
    FROM daily_market d
    JOIN channel c ON d.channel_id = c.id
    WHERE d.stat_date = %s
      AND c.status = 1
    ORDER BY d.rank ASC
    LIMIT 10
    """
    return db.execute_query(query, (stat_date,))


def get_episode_ranking(stat_date=None, top_n=10):
    """
    剧集收视排行榜
    """
    if not stat_date:
        stat_date = get_today_date()

    query = """
    SELECT
        d.stat_date,
        c.name AS '频道',
        e.name AS '剧集名称',
        d.rating AS '收视率',
        d.market_share AS '收视份额',
        eb.platform_type AS '播出类型',
        d.start_time AS '开始时间'
    FROM daily_ep_rank d
    JOIN channel c ON d.channel_id = c.id
    JOIN episode e ON d.episode_id = e.id
    LEFT JOIN episode_broadcast eb ON d.channel_id = eb.channel_id
        AND d.episode_id = eb.episode_id
    WHERE d.stat_date = %s
    ORDER BY d.rating DESC
    LIMIT %s
    """
    return db.execute_query(query, (stat_date, top_n))


def get_city_analysis(stat_date=None):
    """
    城市分级收视对比分析
    """
    if not stat_date:
        stat_date = get_today_date()

    # 重点城市数据
    query_key_town = """
    SELECT
        '重点城市' AS '城市类型',
        COUNT(DISTINCT d.city_id) AS '覆盖城市数',
        ROUND(AVG(d.rating), 3) AS '平均收视率',
        ROUND(AVG(d.market_share), 3) AS '平均收视份额',
        ROUND(SUM(d.audience)/10000, 2) AS '总收视人数(万)'
    FROM daily_citi d
    JOIN city_info ci ON d.city_id = ci.id
    WHERE d.stat_date = %s
      AND ci.key_town = 1
    """

    # 普通城市数据
    query_normal = """
    SELECT
        '普通城市' AS '城市类型',
        COUNT(DISTINCT d.city_id) AS '覆盖城市数',
        ROUND(AVG(d.rating), 3) AS '平均收视率',
        ROUND(AVG(d.market_share), 3) AS '平均收视份额',
        ROUND(SUM(d.audience)/10000, 2) AS '总收视人数(万)'
    FROM daily_citi d
    JOIN city_info ci ON d.city_id = ci.id
    WHERE d.stat_date = %s
      AND ci.key_town = 0
    """

    result_key_town = db.execute_query(query_key_town, (stat_date,))
    result_normal = db.execute_query(query_normal, (stat_date,))

    return result_key_town + result_normal


def get_channel_summary(stat_date=None):
    """
    频道整体收视概况
    """
    if not stat_date:
        stat_date = get_today_date()

    query = """
    SELECT
        c.name AS '频道',
        COUNT(DISTINCT d.stat_date) AS '播出天数',
        ROUND(AVG(d.rating), 3) AS '平均收视率',
        ROUND(MAX(d.rating), 3) AS '峰值收视率',
        ROUND(MIN(d.rating), 3) AS '最低收视率',
        ROUND(AVG(d.market_share), 3) AS '平均收视份额'
    FROM daily_market d
    JOIN channel c ON d.channel_id = c.id
    WHERE d.stat_date = %s
    GROUP BY c.id, c.name
    ORDER BY AVG(d.rating) DESC
    """
    return db.execute_query(query, (stat_date,))


def get_best_episode_channels(stat_date=None, top_n=5):
    """
    收视率top N剧集的频道信息
    """
    if not stat_date:
        stat_date = get_today_date()

    query = """
    SELECT
        c.name AS '频道',
        e.name AS '剧集名称',
        COUNT(DISTINCT d.stat_date) AS '播出天数',
        ROUND(AVG(d.rating), 3) AS '平均收视率',
        ROUND(AVG(d.market_share), 3) AS '平均收视份额'
    FROM daily_ep_rank d
    JOIN channel c ON d.channel_id = c.id
    JOIN episode e ON d.episode_id = e.id
    WHERE d.stat_date = %s
    GROUP BY c.id, c.name, e.id, e.name
    ORDER BY AVG(d.rating) DESC
    LIMIT %s
    """
    return db.execute_query(query, (stat_date, top_n))
