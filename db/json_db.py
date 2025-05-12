import os
import json
from .db_interface import DBInterface
from datetime import datetime
import traceback
import sys

# 获取当前文件的目录
print(f"db/json_db.py 当前路径: {os.path.abspath('.')}")

# 导入Main.py中的resource_path函数
# 由于循环引用问题，我们在此重新定义resource_path函数
def resource_path(relative_path):
    # 总是使用exe同级目录，确保数据文件存取在外部
    # 获取应用程序所在的目录
    base_path = ''
    if hasattr(sys, '_MEIPASS'):  # PyInstaller环境
        # 获取exe所在目录，而不是临时目录
        base_path = os.path.dirname(sys.executable)
    else:  # 开发环境
        # 如果是python Main.py运行，使用脚本所在目录
        main_file = os.path.abspath(sys.argv[0])
        base_path = os.path.dirname(main_file)
    
    # 所有路径都直接使用基础路径，不考虑是否是data目录
    path = os.path.join(base_path, relative_path)
    print(f"数据文件路径(json_db): {path}")
    return path

MEMBER_FILE = resource_path('data/members.json')
RECHARGE_FILE = resource_path('data/recharges.json')
CONSUME_FILE = resource_path('data/consumes.json')

print(f"db/json_db.py 会员文件: {MEMBER_FILE}")
print(f"db/json_db.py 充值文件: {RECHARGE_FILE}")
print(f"db/json_db.py 消费文件: {CONSUME_FILE}")

def ensure_file(path, default):
    try:
        print(f"确保文件存在: {path}")
        if not os.path.exists(path):
            print(f"文件不存在，正在创建: {path}")
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default, f)
            print(f"文件创建完成: {path}")
        else:
            print(f"文件已存在: {path}")
    except Exception as e:
        print(f"创建文件异常: {path}, 错误: {str(e)}")
        print(traceback.format_exc())

def load_json(path):
    try:
        print(f"加载JSON文件: {path}")
        ensure_file(path, [])
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"JSON加载成功: {path}, 数据条数: {len(data)}")
        return data
    except Exception as e:
        print(f"加载JSON异常: {path}, 错误: {str(e)}")
        print(traceback.format_exc())
        return []

def save_json(path, data):
    try:
        print(f"保存JSON文件: {path}, 数据条数: {len(data)}")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON保存成功: {path}")
    except Exception as e:
        print(f"保存JSON异常: {path}, 错误: {str(e)}")
        print(traceback.format_exc())

class JsonDB(DBInterface):
    def get_member(self, phone_or_name):
        members = load_json(MEMBER_FILE)
        for m in members:
            if phone_or_name in (m.get('phone'), m.get('name')):
                return m
        return None

    def add_member(self, member_info):
        members = load_json(MEMBER_FILE)
        member_info['id'] = str(len(members) + 1)
        members.append(member_info)
        save_json(MEMBER_FILE, members)
        return member_info['id']

    def update_member(self, member_id, update_info):
        members = load_json(MEMBER_FILE)
        for m in members:
            if m['id'] == member_id:
                m.update(update_info)
                save_json(MEMBER_FILE, members)
                return True
        return False

    def add_recharge(self, member_id, amount):
        recharges = load_json(RECHARGE_FILE)
        recharges.append({'member_id': member_id, 'amount': amount, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        save_json(RECHARGE_FILE, recharges)
        # 更新余额
        members = load_json(MEMBER_FILE)
        for m in members:
            if m['id'] == member_id:
                m['balance'] = m.get('balance', 0) + amount
                save_json(MEMBER_FILE, members)
                break

    def get_recharge_records(self, member_id):
        recharges = load_json(RECHARGE_FILE)
        return [r for r in recharges if r['member_id'] == member_id]

    def add_consume_record(self, member_id, record):
        consumes = load_json(CONSUME_FILE)
        consumes.append({'member_id': member_id, **record})
        save_json(CONSUME_FILE, consumes)
        # 扣除余额
        members = load_json(MEMBER_FILE)
        for m in members:
            if m['id'] == member_id:
                m['balance'] = m.get('balance', 0) - record.get('amount', 0)
                save_json(MEMBER_FILE, members)
                break

    def get_consume_records(self, member_id):
        consumes = load_json(CONSUME_FILE)
        return [c for c in consumes if c['member_id'] == member_id]

    def get_all_consume_records(self):
        return load_json(CONSUME_FILE)

    def get_all_recharge_records(self):
        return load_json(RECHARGE_FILE)

    def get_all_members(self):
        """获取所有会员"""
        return load_json(MEMBER_FILE)

    def delete_member(self, member_id):
        """删除会员及其所有消费和充值记录"""
        try:
            # 读取所有会员
            members = load_json(MEMBER_FILE)
            
            # 找到并删除会员
            for i, m in enumerate(members):
                if str(m.get('id', '')) == str(member_id):
                    del members[i]
                    save_json(MEMBER_FILE, members)
                    break
            
            # 删除该会员的消费和充值记录
            self.delete_member_records(member_id)
            
            return True
        except Exception as e:
            print(f"删除会员时出错: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def delete_member_records(self, member_id):
        """删除会员相关的所有消费和充值记录"""
        try:
            # 删除消费记录
            consumes = load_json(CONSUME_FILE)
            new_consumes = [c for c in consumes if str(c.get('member_id', '')) != str(member_id)]
            save_json(CONSUME_FILE, new_consumes)
            
            # 删除充值记录
            recharges = load_json(RECHARGE_FILE)
            new_recharges = [r for r in recharges if str(r.get('member_id', '')) != str(member_id)]
            save_json(RECHARGE_FILE, new_recharges)
                
        except Exception as e:
            print(f"删除会员记录时出错: {str(e)}")
            print(traceback.format_exc()) 