# 会员管理系统

一个基于 Python 和 PyQt5 开发的会员管理系统，提供会员管理、消费记录、数据统计等功能。本软件给我朋友店里使用，如果需要二次开发，请联系我！
QQ：2027883286

## 功能特点

- 会员信息管理
  - 会员注册与信息维护
  - 会员搜索（支持姓名和手机号模糊搜索）
  - 会员删除功能
- 消费管理
  - 会员消费记录
  - 散客消费记录
  - 手动订单录入
- 服务项目管理
  - 服务项目配置
  - 价格管理
- 数据统计
  - 消费数据统计
  - 订单记录查询
- 数据库支持
  - JSON 本地存储
  - MySQL 数据库支持（可选）
- 会员余额管理
  - 余额充值
  - 消费扣款
- 简洁直观的用户界面
  - 自适应界面大小
  - 清晰的导航标签

## 系统要求

- Python 3.8 或更高版本
- PyQt5
- 操作系统：Windows 10/11, macOS, Linux
- 最小内存要求：4GB RAM
- 磁盘空间：50MB 可用空间

### 依赖包

- PyQt5
- mysql-connector-python (可选，用于MySQL支持)

## 项目结构

```
MF_System/
├── Main.py              # 主程序入口
├── db/                  # 数据库相关
│   ├── json_db.py      # JSON数据库实现
│   └── db_interface.py # 数据库接口定义
├── data/               # 数据存储目录
│   ├── members.json    # 会员数据
│   ├── consumes.json   # 消费记录
│   ├── recharges.json  # 充值记录
│   └── services.json   # 服务项目配置
├── models/             # 数据模型
├── build/              # 构建输出目录
└── dist/               # 发布目录
```

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/tAoi386/MF_System
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行

```bash
python Main.py
```

## 数据存储

系统默认使用JSON文件存储数据，所有数据文件保存在`data`目录下：
- `members.json`: 会员信息
- `consumes.json`: 消费记录
- `recharges.json`: 充值记录
- `services.json`: 服务项目配置

## 数据库迁移

系统支持从JSON存储迁移到MySQL数据库：
1. 在系统设置中选择数据库连接
2. 配置MySQL连接信息
3. 执行数据同步

## 许可证

MIT License 