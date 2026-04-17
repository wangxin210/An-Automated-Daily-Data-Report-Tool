# An-Automated-Daily-Data-Report-Tool
A simple and efficient Python script that automatically generates daily TV and movie viewership reports.

## Technology
- **Python 3.7+**
- **MySQL** 
- **openpyxl** 
- **APScheduler** 

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure database connection

Edit the `db_config.py` file and fill in your MySQL connection information

### 3. Run report generation

#### Method 1: Run Manually

```bash
python main.py
```

#### Method 2: Run Automatically on a Schedule

**Windows System:**
1. Open "Task Scheduler"
2. Create a basic task, set the trigger to "Daily"
3. Set the action to "Start a program"
4. Program path: `python`

**Linux/Mac System:**
Add to crontab:

```bash
crontab -e
```

Add the following content:

```
0 8 * * * /usr/bin/python3 /path/to/main.py >> /path/to/logs/cron.log 2>&1
```

### 4. View Results

Reports will be generated in the `output/` directory:

```
output/
├── 卫视收视排行榜_20231227.xlsx
├── 剧集收视排行榜_20231227.xlsx
└── 城市分级收视对比_20231227.xlsx
```

Log files are stored in the `logs/` directory:

```
logs/
└── report_assistant.log
```

## Module
### db_config.py - Database Connection
- Manages database connections
- Provides a unified query interface

### data_query.py - Data Query
- Satellite ratings ranking queries
- Series ratings ranking queries
- City-level comparison analysis queries

### excel_report.py - Excel Generation
- Report formatting
- Style settings
- Supports multiple report types

### schedule.py - Scheduled Tasks
- Implements scheduled execution using APScheduler
- Error handling and logging
- Manual and automatic run modes

### main.py - Main Program
- Program entry point
- Data validation
- Report generation coordination

## Log
Program runtime logs will be recorded in `logs/report_assistant.log`:

## Output Report
### 1. 卫视收视竞争市场排行榜 (Top10)
- 频道排名、收视率、收视份额
- 与上周排名对比（↑/↓标记）
- 网络类型统计

### 2. 剧集收视排行榜
- 电视剧收视率、收视份额
- 播出类型（首播/重播/网台）
- 开始时间信息

### 3. 城市分级收视对比分析
- 重点城市 vs 普通城市
- 覆盖城市数、平均收视率、总收视人数
