import sys
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QDialog, QSpinBox, QInputDialog, QComboBox, QFrame, QCompleter, QTabWidget,
    QTextBrowser, QDialogButtonBox, QGridLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QStringListModel, QSize, QEvent, QTimer
from PyQt5.QtGui import QFont
from db.json_db import JsonDB
import json
from datetime import datetime, timedelta
import random

import sqlite3


#测试提交   哈哈哈

def resource_path(relative_path):
    # 总是使用exe同级目录，确保数据文件存取在外部
    # 获取应用程序所在的目录
    base_path = ''
    if hasattr(sys, '_MEIPASS'):  # PyInstaller环境
        # 获取exe所在目录，而不是临时目录
        base_path = os.path.dirname(sys.executable)
    else:  # 开发环境
        # 如果是python Main.py运行，使用脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"应用程序目录: {base_path}")
    path = os.path.join(base_path, relative_path)
    print(f"数据文件路径: {path}")
    return path

def ensure_data_files():
    try:
        print(f"当前工作目录: {os.getcwd()}")
        data_dir = resource_path('data')
        print(f"数据目录路径: {data_dir}")
        
        if not os.path.exists(data_dir):
            print(f"数据目录不存在，正在创建: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
            print(f"数据目录创建完成: {data_dir}")
        else:
            print(f"数据目录已存在: {data_dir}")
            
        files_defaults = {
            'members.json': [],
            'consumes.json': [],
            'recharges.json': [],
            'services.json': [
                {"name": "剪发", "price": 30},
                {"name": "烫发", "price": 120},
                {"name": "染发", "price": 150}
            ]
        }
        
        for fname, default in files_defaults.items():
            fpath = os.path.join(data_dir, fname)
            print(f"检查文件: {fpath}")
            try:
                if not os.path.exists(fpath):
                    print(f"文件不存在，正在创建: {fpath}")
                    with open(fpath, 'w', encoding='utf-8') as f:
                        json.dump(default, f, ensure_ascii=False, indent=2)
                    print(f"文件创建成功: {fpath}")
                else:
                    print(f"文件已存在: {fpath}")
            except Exception as e:
                print(f"创建文件 {fname} 出错: {str(e)}")
                print(traceback.format_exc())
                # 尝试用绝对路径创建
                try:
                    abs_path = os.path.join(os.path.dirname(sys.executable), 'data', fname)
                    print(f"尝试使用绝对路径创建文件: {abs_path}")
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        json.dump(default, f, ensure_ascii=False, indent=2)
                    print(f"使用绝对路径创建文件成功: {abs_path}")
                except Exception as e2:
                    print(f"使用绝对路径创建文件也失败: {abs_path}, 错误: {str(e2)}")
                    print(traceback.format_exc())
    except Exception as e:
        print(f"确保数据文件时出错: {str(e)}")
        print(traceback.format_exc())

def ensure_data_directory():
    # 确保data目录存在
    try:
        data_dir = resource_path('data')
        print(f"确保数据目录存在: {data_dir}")
        
        if not os.path.exists(data_dir):
            print(f"数据目录不存在，尝试创建: {data_dir}")
            try:
                os.makedirs(data_dir, exist_ok=True)
                print(f"数据目录创建成功: {data_dir}")
            except PermissionError:
                print(f"权限不足，无法创建目录: {data_dir}")
                # 尝试用管理员权限创建目录的代码
                # 在Windows上，这需要UAC提示，可能不适合所有场景
                QMessageBox.warning(None, "权限不足", 
                    f"无法在 {data_dir} 创建数据目录。\n请检查目录权限或手动创建data文件夹。")
            except Exception as e:
                print(f"创建目录异常: {data_dir}, 错误: {str(e)}")
                print(traceback.format_exc())
                # 尝试在其他可写位置创建目录
                try:
                    alt_data_dir = os.path.join(os.path.dirname(sys.executable), 'data')
                    print(f"尝试在可执行文件目录创建data: {alt_data_dir}")
                    os.makedirs(alt_data_dir, exist_ok=True)
                    print(f"在可执行文件目录创建data成功: {alt_data_dir}")
                except Exception as e2:
                    print(f"备选位置创建目录也失败: {alt_data_dir}, 错误: {str(e2)}")
                    print(traceback.format_exc())
                    QMessageBox.critical(None, "严重错误", 
                        f"无法创建数据目录，应用程序可能无法正常工作。\n错误: {str(e2)}")
        else:
            print(f"数据目录已存在: {data_dir}")
    except Exception as e:
        print(f"确保数据目录时出错: {str(e)}")
        print(traceback.format_exc())

class RegisterDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle('会员注册')
        self.layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.gender_edit = QLineEdit()
        self.birthday_edit = QLineEdit()
        self.layout.addRow('姓名:', self.name_edit)
        self.layout.addRow('手机号:', self.phone_edit)
        self.layout.addRow('性别:', self.gender_edit)
        self.layout.addRow('生日:', self.birthday_edit)
        self.submit_btn = QPushButton('注册')
        self.submit_btn.clicked.connect(self.register)
        self.layout.addRow(self.submit_btn)

    def register(self):
        info = {
            'name': self.name_edit.text(),
            'phone': self.phone_edit.text(),
            'gender': self.gender_edit.text(),
            'birthday': self.birthday_edit.text(),
            'balance': 0
        }
        if not info['name'] or not info['phone']:
            QMessageBox.warning(self, '提示', '姓名和手机号不能为空')
            return
        self.db.add_member(info)
        QMessageBox.information(self, '成功', '注册成功')
        self.accept()

class ConsumeDialog(QDialog):
    def __init__(self, db, member_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.member_id = member_id
        self.setWindowTitle('新增消费')
        self.layout = QFormLayout(self)
        # 生成订单号
        self.order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
        self.order_id_label = QLabel(self.order_id)
        self.layout.addRow('订单号:', self.order_id_label)
        # 加载服务项目
        services_path = resource_path('data/services.json')
        with open(services_path, 'r', encoding='utf-8') as f:
            self.services = json.load(f)
        self.service_box = QComboBox()
        for s in self.services:
            self.service_box.addItem(f"{s['name']} (￥{s['price']})", s)
        self.layout.addRow('服务项目:', self.service_box)
        self.amount_label = QLabel(str(self.services[0]['price']))
        self.layout.addRow('金额:', self.amount_label)
        self.service_box.currentIndexChanged.connect(self.update_amount)
        self.submit_btn = QPushButton('提交')
        self.submit_btn.clicked.connect(self.submit)
        self.layout.addRow(self.submit_btn)
    def update_amount(self):
        s = self.service_box.currentData()
        self.amount_label.setText(str(s['price']))
    def submit(self):
        s = self.service_box.currentData()
        record = {
            'order_id': self.order_id,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'item': s['name'],
            'amount': s['price']
        }
        self.db.add_consume_record(self.member_id, record)
        QMessageBox.information(self, '成功', '消费记录已添加')
        self.accept()

class ServiceSettingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('服务设置')
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['项目名称', '金额'])
        self.layout.addWidget(self.table)
        btns = QHBoxLayout()
        self.add_btn = QPushButton('添加')
        self.add_btn.clicked.connect(self.add_row)
        btns.addWidget(self.add_btn)
        self.del_btn = QPushButton('删除')
        self.del_btn.clicked.connect(self.del_row)
        btns.addWidget(self.del_btn)
        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.save)
        btns.addWidget(self.save_btn)
        self.layout.addLayout(btns)
        self.load_services()
    def load_services(self):
        self.table.setRowCount(0)
        try:
            with open(resource_path('data/services.json'), 'r', encoding='utf-8') as f:
                services = json.load(f)
        except Exception:
            services = []
        for s in services:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(s.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(str(s.get('price', 0))))
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(''))
        self.table.setItem(row, 1, QTableWidgetItem('0'))
    def del_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
    def save(self):
        services = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().strip() if self.table.item(row, 0) else ''
            try:
                price = float(self.table.item(row, 1).text())
            except Exception:
                price = 0
            if name:
                services.append({'name': name, 'price': price})
        with open(resource_path('data/services.json'), 'w', encoding='utf-8') as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, '成功', '服务项目已保存')

class ManualOrderDialog(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle('手写单号录入')
        self.resize(350, 220)
        layout = QFormLayout(self)
        self.order_id_edit = QLineEdit()
        # 服务项目下拉框
        self.service_box = QComboBox()
        self.services = self.load_services()
        for s in self.services:
            self.service_box.addItem(f"{s['name']} (￥{s['price']})", s)
        self.service_box.currentIndexChanged.connect(self.update_amount)
        self.amount_edit = QLineEdit()
        self.amount_edit.setReadOnly(True)
        self.update_amount()
        self.time_label = QLabel(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        layout.addRow('订单号:', self.order_id_edit)
        layout.addRow('项目:', self.service_box)
        layout.addRow('金额:', self.amount_edit)
        layout.addRow('时间:', self.time_label)
        self.submit_btn = QPushButton('录入')
        self.submit_btn.clicked.connect(self.submit)
        layout.addRow(self.submit_btn)
    def load_services(self):
        try:
            with open(resource_path('data/services.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    def update_amount(self):
        s = self.service_box.currentData()
        if s:
            self.amount_edit.setText(str(s['price']))
        else:
            self.amount_edit.setText('0')
    def submit(self):
        order_id = self.order_id_edit.text().strip()
        s = self.service_box.currentData()
        item = s['name'] if s else ''
        try:
            amount = float(self.amount_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, '提示', '金额必须为数字')
            return
        if not order_id or not item:
            QMessageBox.warning(self, '提示', '订单号和项目不能为空')
            return
        record = {
            'order_id': order_id,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'item': item,
            'amount': amount
        }
        self.db.add_consume_record('manual', record)
        QMessageBox.information(self, '成功', '手写单号消费已录入')
        self.order_id_edit.clear()
        self.service_box.setCurrentIndex(0)
        self.amount_edit.clear()
        self.time_label.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class StatsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle('数据统计')
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        # 统计汇总tab
        self.summary_widget = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_widget)
        self.range_box = QComboBox()
        self.range_box.addItems(['今日', '本周', '本月'])
        self.range_box.currentIndexChanged.connect(self.update_stats)
        self.summary_layout.addWidget(self.range_box)
        self.result_label = QLabel()
        self.summary_layout.addWidget(self.result_label)
        self.tabs.addTab(self.summary_widget, '统计汇总')
        # 订单浏览tab
        self.orders_widget = QWidget()
        self.orders_layout = QVBoxLayout(self.orders_widget)
        self.orders_table = QTableWidget(0, 5)
        self.orders_table.setHorizontalHeaderLabels(['订单号', '时间', '项目', '金额', '会员ID'])
        self.orders_layout.addWidget(self.orders_table)
        self.orders_summary = QLabel()
        self.orders_layout.addWidget(self.orders_summary)
        self.tabs.addTab(self.orders_widget, '订单浏览')
        layout.addWidget(self.tabs)
        self.update_stats()
        self.update_orders()
        self.tabs.currentChanged.connect(self.on_tab_changed)
    def update_stats(self):
        now = datetime.now()
        choice = self.range_box.currentText()
        if choice == '今日':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif choice == '本周':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif choice == '本月':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now
        # 消费统计
        consumes = self.db.get_all_consume_records()
        total_consume = 0
        consume_count = 0
        for c in consumes:
            try:
                t = datetime.strptime(c.get('time', ''), '%Y-%m-%d %H:%M:%S')
            except Exception:
                continue
            if t >= start:
                total_consume += float(c.get('amount', 0))
                consume_count += 1
        # 充值统计
        recharges = self.db.get_all_recharge_records()
        total_recharge = 0
        recharge_count = 0
        for r in recharges:
            try:
                t = datetime.strptime(r.get('time', ''), '%Y-%m-%d %H:%M:%S')
            except Exception:
                continue
            if t >= start:
                total_recharge += float(r.get('amount', 0))
                recharge_count += 1
        text = f"统计范围：{choice}\n"
        text += f"消费总额：￥{total_consume:.2f}  （{consume_count} 单）\n"
        text += f"充值总额：￥{total_recharge:.2f}  （{recharge_count} 单）"
        self.result_label.setText(text)
    def update_orders(self):
        consumes = self.db.get_all_consume_records()
        self.orders_table.setRowCount(len(consumes))
        total = 0
        for row, c in enumerate(consumes):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(c.get('order_id', ''))))
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(c.get('time', ''))))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(c.get('item', ''))))
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(c.get('amount', 0))))
            self.orders_table.setItem(row, 4, QTableWidgetItem(str(c.get('member_id', ''))))
            try:
                total += float(c.get('amount', 0))
            except Exception:
                pass
        self.orders_summary.setText(f"订单总数：{len(consumes)}  消费总额：￥{total:.2f}")
    def on_tab_changed(self, idx):
        if idx == 1:
            self.update_orders()

class AboutWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # 创建文本浏览器
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        
        # 设置关于信息和免责声明
        about_text = """
        <h2 style="text-align:center">美发店会员管理系统</h2>
        <p style="text-align:center">版本：v1.0</p>
        
        <h3>关于作者</h3>
        <p>本软件由Tao开发</p>
        <p>联系方式：15575949809</p>
        
        <h3>软件说明</h3>
        <p>本软件是一个美发店会员管理系统，主要功能包括：</p>
        <ul>
            <li>会员管理：注册、查询、信息展示</li>
            <li>消费记录：新增消费、散客消费、手写单号录入</li>
            <li>充值管理：会员充值、余额显示</li>
            <li>数据统计：按日/周/月统计消费和充值</li>
            <li>服务设置：可自定义服务项目和价格</li>
        </ul>
        
        <h3>功能开发说明</h3>
        <p style="color:orange; font-weight:bold">数据库功能目前正在开发中，尚未完全完善。如需使用数据库功能，请联系开发者获取支持。</p>
        
        <h3>免责声明</h3>
        <p>1. 本软件为免费软件，仅用于美发店会员管理。</p>
        <p>2. 用户应自行确保输入数据的准确性和完整性，开发者不对因数据错误导致的任何损失负责。</p>
        <p>3. 请定期备份数据文件，开发者不对数据丢失承担责任。</p>
        <p>4. 本软件不收集任何个人隐私信息，所有数据均保存在本地。</p>
        <p>5. 使用本软件即表示您已阅读并同意本免责声明的所有条款。</p>
        
        <h3>注意事项</h3>
        <p style="color:red; font-weight:bold">软件运行在本地，请勿随意删除当前目录下的data数据文件夹，本软件不是云服务器上，请注意数据保存。如果需要数据库支持，请联系我帮助添加数据库。</p>
        """
        
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)

class DeleteMemberWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.layout = QVBoxLayout(self)
        
        # 顶部提示信息
        self.notice_label = QLabel("请谨慎操作！删除会员将同时删除其所有消费和充值记录，且无法恢复。")
        self.notice_label.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(self.notice_label)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('输入手机号或姓名')
        self.search_btn = QPushButton('查询会员')
        self.search_btn.clicked.connect(self.search_member)
        search_layout.addWidget(QLabel('会员查询:'))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)
        
        # 会员信息表格
        self.member_table = QTableWidget(0, 5)
        self.member_table.setHorizontalHeaderLabels(['ID', '姓名', '手机号', '性别', '余额'])
        self.layout.addWidget(self.member_table)
        
        # 删除按钮
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()
        self.delete_btn = QPushButton('删除选中会员')
        self.delete_btn.setStyleSheet("background-color: #ffcccc;")
        self.delete_btn.clicked.connect(self.delete_member)
        delete_layout.addWidget(self.delete_btn)
        self.layout.addLayout(delete_layout)
        
        # 刷新会员列表
        self.refresh_members()
        
        # 设置自动补全
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(False)
        self.completer.setFilterMode(Qt.MatchContains)
        self.search_edit.setCompleter(self.completer)
        self.search_edit.textEdited.connect(self.update_completer)
    
    def update_completer(self, text):
        # 模糊匹配会员姓名或手机号
        if not text:
            self.completer_model.setStringList([])
            return
        matches = []
        for m in self.db.get_all_members():
            if text in m.get('name', '') or text in m.get('phone', ''):
                matches.append(f"{m.get('name','')}（{m.get('phone','')}）")
        self.completer_model.setStringList(matches)
    
    def refresh_members(self):
        # 刷新会员列表
        members = self.db.get_all_members()
        self.member_table.setRowCount(len(members))
        for row, member in enumerate(members):
            self.member_table.setItem(row, 0, QTableWidgetItem(str(member.get('id', ''))))
            self.member_table.setItem(row, 1, QTableWidgetItem(member.get('name', '')))
            self.member_table.setItem(row, 2, QTableWidgetItem(member.get('phone', '')))
            self.member_table.setItem(row, 3, QTableWidgetItem(member.get('gender', '')))
            self.member_table.setItem(row, 4, QTableWidgetItem(str(member.get('balance', 0))))
    
    def search_member(self):
        key = self.search_edit.text().strip()
        if not key:
            self.refresh_members()
            return
            
        # 支持"姓名（手机号）"格式
        if '（' in key and '）' in key:
            key = key.split('（')[1].split('）')[0]
            
        member = self.db.get_member(key)
        if not member:
            QMessageBox.information(self, '提示', '未找到会员')
            return
            
        # 只显示搜索到的会员
        self.member_table.setRowCount(1)
        self.member_table.setItem(0, 0, QTableWidgetItem(str(member.get('id', ''))))
        self.member_table.setItem(0, 1, QTableWidgetItem(member.get('name', '')))
        self.member_table.setItem(0, 2, QTableWidgetItem(member.get('phone', '')))
        self.member_table.setItem(0, 3, QTableWidgetItem(member.get('gender', '')))
        self.member_table.setItem(0, 4, QTableWidgetItem(str(member.get('balance', 0))))
    
    def delete_member(self):
        selected_rows = self.member_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请先选择要删除的会员')
            return
            
        row = selected_rows[0].row()
        member_id = self.member_table.item(row, 0).text()
        member_name = self.member_table.item(row, 1).text()
        member_phone = self.member_table.item(row, 2).text()
        
        # 二次确认
        reply = QMessageBox.question(self, '确认删除', 
                                     f'确定要删除会员 "{member_name}({member_phone})" 吗？\n此操作将删除该会员的所有记录且不可恢复！', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除会员
            if self.db.delete_member(member_id):
                QMessageBox.information(self, '成功', f'会员 "{member_name}" 已删除')
                self.refresh_members()
            else:
                QMessageBox.warning(self, '错误', '删除失败，请重试')

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理员验证")
        self.setMinimumWidth(300)
        
        # 设置对话框布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        message = QLabel("请输入管理员密码以访问会员删除功能")
        message.setStyleSheet("font-weight: bold;")
        layout.addWidget(message)
        
        # 添加密码输入框
        form_layout = QFormLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # 设置为密码模式（显示为圆点）
        form_layout.addRow("密码:", self.password_edit)
        layout.addLayout(form_layout)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.check_password)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def check_password(self):
        # 设定的管理员密码
        admin_password = "123456"  # 可以根据需要修改密码
        
        if self.password_edit.text() == admin_password:
            self.accept()
        else:
            QMessageBox.warning(self, "验证失败", "密码错误，无法访问会员删除功能！")
            self.password_edit.clear()
            self.password_edit.setFocus()

class DatabaseConnectWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.layout = QVBoxLayout(self)
        
        # 顶部提示信息
        self.notice_label = QLabel("MySQL数据库连接设置")
        self.notice_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.notice_label)
        
        # 添加驱动状态指示和调试按钮
        status_layout = QHBoxLayout()
        self.driver_status = QLabel()
        self.driver_status.setWordWrap(True)
        status_layout.addWidget(self.driver_status)
        
        self.debug_btn = QPushButton("诊断驱动问题")
        self.debug_btn.clicked.connect(self.debug_driver)
        status_layout.addWidget(self.debug_btn)
        
        self.layout.addLayout(status_layout)
        
        # 添加驱动说明
        self.driver_tips = QLabel("提示: 请将pymysql文件夹放在程序同级目录下，然后重启应用")
        self.driver_tips.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(self.driver_tips)
        
        # 数据库连接参数
        self.db_params_group = QWidget()
        self.db_params_layout = QGridLayout(self.db_params_group)
        
        # 主机和端口
        self.host_label = QLabel("主机:")
        self.host_edit = QLineEdit("localhost")
        self.db_params_layout.addWidget(self.host_label, 0, 0)
        self.db_params_layout.addWidget(self.host_edit, 0, 1)
        
        self.port_label = QLabel("端口:")
        self.port_edit = QLineEdit("3306")  # MySQL默认端口
        self.db_params_layout.addWidget(self.port_label, 0, 2)
        self.db_params_layout.addWidget(self.port_edit, 0, 3)
        
        # 用户名和密码
        self.username_label = QLabel("用户名:")
        self.username_edit = QLineEdit("root")
        self.db_params_layout.addWidget(self.username_label, 1, 0)
        self.db_params_layout.addWidget(self.username_edit, 1, 1)
        
        self.password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.db_params_layout.addWidget(self.password_label, 1, 2)
        self.db_params_layout.addWidget(self.password_edit, 1, 3)
        
        # 数据库名称
        self.dbname_label = QLabel("数据库名称:")
        self.dbname_edit = QLineEdit("hairsalon")
        self.db_params_layout.addWidget(self.dbname_label, 2, 0)
        self.db_params_layout.addWidget(self.dbname_edit, 2, 1)
        
        # 添加获取数据库列表按钮
        self.refresh_db_btn = QPushButton("获取数据库列表")
        self.refresh_db_btn.clicked.connect(self.fetch_database_list)
        self.db_params_layout.addWidget(self.refresh_db_btn, 2, 2, 1, 2)
        
        # 添加数据库选择下拉框
        self.db_list_label = QLabel("选择已有数据库:")
        self.db_list_combo = QComboBox()
        self.db_list_combo.currentTextChanged.connect(self.on_db_selected)
        self.db_params_layout.addWidget(self.db_list_label, 3, 0)
        self.db_params_layout.addWidget(self.db_list_combo, 3, 1, 1, 3)
        
        # 默认隐藏数据库选择控件
        self.db_list_label.setVisible(False)
        self.db_list_combo.setVisible(False)
        
        self.layout.addWidget(self.db_params_group)
        
        # 连接测试按钮
        self.connect_btn = QPushButton("测试连接")
        self.connect_btn.clicked.connect(self.test_connection)
        self.layout.addWidget(self.connect_btn)
        
        # 初始化数据库区域
        self.init_widget = QWidget()
        self.init_layout = QVBoxLayout(self.init_widget)
        
        self.init_btn = QPushButton("初始化数据库")
        self.init_btn.clicked.connect(self.init_database)
        self.init_btn.setEnabled(False)  # 默认禁用
        self.init_layout.addWidget(self.init_btn)
        
        self.init_status = QLabel("数据库未连接")
        self.init_status.setStyleSheet("color: gray;")
        self.init_layout.addWidget(self.init_status)
        
        self.layout.addWidget(self.init_widget)
        
        # 同步数据区域
        self.sync_widget = QWidget()
        self.sync_layout = QVBoxLayout(self.sync_widget)
        
        self.sync_btn = QPushButton("同步数据")
        self.sync_btn.clicked.connect(self.sync_data)
        self.sync_btn.setEnabled(False)  # 默认禁用
        self.sync_layout.addWidget(self.sync_btn)
        
        self.sync_progress = QProgressBar()
        self.sync_progress.setVisible(False)
        self.sync_layout.addWidget(self.sync_progress)
        
        self.sync_status = QLabel("未同步")
        self.sync_layout.addWidget(self.sync_status)
        
        self.layout.addWidget(self.sync_widget)
        
        # 添加说明
        self.help_text = QTextBrowser()
        self.help_text.setMaximumHeight(100)
        self.help_text.setHtml("""
        <p><b>MySQL数据库说明：</b></p>
        <p>使用MySQL数据库可以实现多设备数据共享和备份。</p>
        <p style="color:red">如果在程序目录下没有pymysql文件夹，程序将无法连接MySQL。</p>
        <p>1. 首先测试连接</p>
        <p>2. 连接成功后初始化数据库</p>
        <p>3. 同步本地数据到数据库</p>
        """)
        self.layout.addWidget(self.help_text)
        
        # 更新驱动状态
        self.check_mysql_driver()
    
    def check_mysql_driver(self):
        """检查MySQL驱动状态"""
        # 更新驱动状态显示
        if MYSQL_AVAILABLE:
            self.driver_status.setText("<b>MySQL驱动状态:</b> <span style=\"color:green\">已安装</span>")
            self.refresh_db_btn.setEnabled(True)
            self.connect_btn.setEnabled(True)
        else:
            self.driver_status.setText("<b>MySQL驱动状态:</b> <span style=\"color:red\">未安装</span>")
            self.refresh_db_btn.setEnabled(False)
            self.connect_btn.setEnabled(False)
            
            # 添加驱动安装提示
            if not hasattr(self, 'driver_tips'):
                self.driver_tips = QLabel("请将pymysql文件夹放在程序同级目录下，然后重启应用")
                self.driver_tips.setStyleSheet("color: red; font-weight: bold;")
                self.layout.insertWidget(1, self.driver_tips)
    
    def on_db_selected(self, db_name):
        """当用户从下拉列表选择数据库时触发"""
        if db_name:
            self.dbname_edit.setText(db_name)
    
    def fetch_database_list(self):
        """获取服务器上的数据库列表"""
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # 检查连接参数
        if not host or not port or not username:
            QMessageBox.warning(self, "参数不足", "请填写主机、端口和用户名")
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 连接MySQL服务器
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password
            )
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW DATABASES")
                    db_list = [row[0] for row in cursor.fetchall()]
            finally:
                connection.close()
            
            # 清空并重新填充下拉框
            self.db_list_combo.clear()
            self.db_list_combo.addItems(db_list)
            
            # 显示数据库选择控件
            self.db_list_label.setVisible(True)
            self.db_list_combo.setVisible(True)
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "成功", f"已获取到 {len(db_list)} 个数据库")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "失败", f"获取数据库列表失败: {str(e)}")
    
    def test_connection(self):
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 收集连接参数
        params = {
            'host': self.host_edit.text().strip(),
            'port': self.port_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'dbname': self.dbname_edit.text().strip()
        }
        
        # 为MySQL设置默认值
        if not params['dbname']:
            params['dbname'] = "hairsalon"
            self.dbname_edit.setText(params['dbname'])
        
        try:
            # 检查参数
            if not params['host'] or not params['port'] or not params['username'] or not params['dbname']:
                raise ValueError("请填写所有必要的连接参数")
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 执行连接测试
            connection = pymysql.connect(
                host=params['host'],
                port=int(params['port']),
                user=params['username'],
                password=params['password'],
                database=params['dbname']
            )
            connection.close()
            
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "连接成功", "数据库连接测试成功！")
            
            # 启用初始化和同步按钮
            self.init_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
            self.init_status.setText("可以初始化数据库")
            self.init_status.setStyleSheet("color: green;")
            
        except pymysql.err.OperationalError as e:
            QApplication.restoreOverrideCursor()
            
            # 检查是否为"未知数据库"错误，这意味着服务器连接成功，但数据库不存在
            if e.args[0] == 1049:  # 未知数据库错误代码
                reply = QMessageBox.question(self, "数据库不存在", 
                                           f"数据库 '{params['dbname']}' 不存在。是否要创建它？",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    self.create_database(params)
                else:
                    self.init_btn.setEnabled(False)
                    self.sync_btn.setEnabled(False)
            else:
                QMessageBox.critical(self, "连接失败", f"无法连接到数据库: {str(e)}")
                self.init_btn.setEnabled(False)
                self.sync_btn.setEnabled(False)
                self.init_status.setText("数据库连接失败")
                self.init_status.setStyleSheet("color: red;")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "连接失败", f"无法连接到数据库: {str(e)}")
            self.init_btn.setEnabled(False)
            self.sync_btn.setEnabled(False)
            self.init_status.setText("数据库连接失败")
            self.init_status.setStyleSheet("color: red;")
    
    def create_database(self, params):
        """创建数据库"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 连接到MySQL服务器而不指定数据库
            connection = pymysql.connect(
                host=params['host'],
                port=int(params['port']),
                user=params['username'],
                password=params['password']
            )
            
            try:
                with connection.cursor() as cursor:
                    # 创建数据库
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{params['dbname']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
                
                QApplication.restoreOverrideCursor()
                QMessageBox.information(self, "创建成功", f"数据库 '{params['dbname']}' 已创建")
                
                # 启用初始化按钮
                self.init_btn.setEnabled(True)
                self.init_status.setText("请初始化数据库")
                self.init_status.setStyleSheet("color: green;")
                
            finally:
                connection.close()
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "创建失败", f"创建数据库失败: {str(e)}")
    
    def init_database(self):
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 确认初始化
        reply = QMessageBox.question(self, "确认初始化", 
                                    "初始化将创建新的数据库表结构，如果表已存在，可能会清除现有数据。是否继续？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            host = self.host_edit.text().strip()
            port = self.port_edit.text().strip()
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            dbname = self.dbname_edit.text().strip()
            
            # 如果数据库名为空，使用默认值
            if not dbname:
                dbname = "hairsalon"
                self.dbname_edit.setText(dbname)
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=dbname
            )
            
            try:
                with connection.cursor() as cursor:
                    # 创建会员表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS members (
                        id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        gender VARCHAR(10),
                        birthday VARCHAR(20),
                        balance DECIMAL(10, 2) DEFAULT 0
                    )
                    """)
                    
                    # 创建消费记录表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS consumes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id VARCHAR(50),
                        order_id VARCHAR(50) NOT NULL,
                        time DATETIME NOT NULL,
                        item VARCHAR(100) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                    )
                    """)
                    
                    # 创建充值记录表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recharges (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id VARCHAR(50) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        time DATETIME NOT NULL,
                        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                    )
                    """)
                    
                    # 创建服务项目表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL
                    )
                    """)
                    
                connection.commit()
            finally:
                connection.close()
            
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "初始化成功", "数据库表结构创建成功！")
            self.init_status.setText("数据库已初始化")
            self.init_status.setStyleSheet("color: green;")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "初始化失败", f"数据库初始化失败: {str(e)}")
            self.init_status.setText("数据库初始化失败")
            self.init_status.setStyleSheet("color: red;")
    
    def sync_data(self):
        # 与原来的功能相同，只是需要检查MySQL驱动
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 确认同步
        reply = QMessageBox.question(self, "确认同步", 
                                    "将本地JSON数据同步到数据库可能会覆盖数据库中的现有数据。是否继续？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # 显示进度条
            self.sync_progress.setValue(0)
            self.sync_progress.setVisible(True)
            self.sync_status.setText("同步中...")
            
            # 获取数据库连接参数
            host = self.host_edit.text().strip()
            port = self.port_edit.text().strip()
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            dbname = self.dbname_edit.text().strip()

            # 连接到MySQL数据库
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=dbname
            )
            
            try:
                # 读取本地会员数据
                members = self.db.get_all_members()
                total_items = len(members)
                if total_items == 0:
                    self.sync_progress.setVisible(False)
                    self.sync_status.setText("没有会员数据可同步")
                    return
                
                progress_step = 100 / (total_items + 2)  # +2 for services and other steps
                progress = 0
                
                with connection.cursor() as cursor:
                    # 1. 同步服务项目
                    services_path = resource_path('data/services.json')
                    self.sync_status.setText("同步服务项目...")
                    if os.path.exists(services_path):
                        with open(services_path, 'r', encoding='utf-8') as f:
                            services = json.load(f)
                        
                        # 清空服务表
                        cursor.execute("TRUNCATE TABLE services")
                        
                        # 插入服务项目
                        for service in services:
                            cursor.execute(
                                "INSERT INTO services (name, price) VALUES (%s, %s)", 
                                (service.get('name', ''), service.get('price', 0))
                            )
                    
                    # 更新进度
                    progress += progress_step
                    self.sync_progress.setValue(int(progress))
                    QApplication.processEvents()  # 保持UI响应
                    
                    # 2. 同步会员数据
                    self.sync_status.setText("同步会员数据...")
                    
                    # 清空会员相关表(需要按照外键约束顺序)
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")  # 暂时禁用外键检查
                    cursor.execute("TRUNCATE TABLE consumes")
                    cursor.execute("TRUNCATE TABLE recharges")
                    cursor.execute("TRUNCATE TABLE members")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")  # 重新启用外键检查
                    
                    # 插入会员数据
                    for i, member in enumerate(members):
                        # 插入会员基本信息
                        cursor.execute(
                            "INSERT INTO members (id, name, phone, gender, birthday, balance) VALUES (%s, %s, %s, %s, %s, %s)",
                            (
                                member.get('id', ''),
                                member.get('name', ''),
                                member.get('phone', ''),
                                member.get('gender', ''),
                                member.get('birthday', ''),
                                member.get('balance', 0)
                            )
                        )
                        
                        # 获取这个会员的消费记录
                        consume_records = self.db.get_consume_records(member['id'])
                        for record in consume_records:
                            cursor.execute(
                                "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                                (
                                    member.get('id', ''),
                                    record.get('order_id', ''),
                                    record.get('time', ''),
                                    record.get('item', ''),
                                    record.get('amount', 0)
                                )
                            )
                        
                        # 获取这个会员的充值记录
                        recharge_records = self.db.get_recharge_records(member['id'])
                        for record in recharge_records:
                            cursor.execute(
                                "INSERT INTO recharges (member_id, time, amount) VALUES (%s, %s, %s)",
                                (
                                    member.get('id', ''),
                                    record.get('time', ''),
                                    record.get('amount', 0)
                                )
                            )
                        
                        # 更新进度
                        progress = progress_step + (i + 1) * progress_step
                        self.sync_progress.setValue(int(progress))
                        QApplication.processEvents()  # 保持UI响应
                    
                    # 3. 同步散客消费
                    self.sync_status.setText("同步散客消费...")
                    guest_records = self.db.get_consume_records('guest')
                    for record in guest_records:
                        cursor.execute(
                            "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                            (
                                'guest',
                                record.get('order_id', ''),
                                record.get('time', ''),
                                record.get('item', ''),
                                record.get('amount', 0)
                            )
                        )
                    
                    # 4. 同步手动录入消费
                    manual_records = self.db.get_consume_records('manual')
                    for record in manual_records:
                        cursor.execute(
                            "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                            (
                                'manual',
                                record.get('order_id', ''),
                                record.get('time', ''),
                                record.get('item', ''),
                                record.get('amount', 0)
                            )
                        )
                
                # 提交所有更改
                connection.commit()
                
                # 完成进度条
                self.sync_progress.setValue(100)
                QApplication.processEvents()  # 保持UI响应
                
            finally:
                connection.close()
            
            # 隐藏进度条，显示成功状态
            self.sync_progress.setVisible(False)
            self.sync_status.setText(f"同步完成！共同步 {total_items} 名会员及相关记录")
            self.sync_status.setStyleSheet("color: green;")
            
            QMessageBox.information(self, "同步成功", "数据已成功同步到数据库！")
            
        except Exception as e:
            self.sync_progress.setVisible(False)
            self.sync_status.setText("同步失败")
            self.sync_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "同步失败", f"数据同步过程中出错: {str(e)}")
            print(f"同步错误: {str(e)}")
            print(traceback.format_exc())

    def debug_driver(self):
        """显示驱动相关调试信息"""
        # 获取系统路径信息
        if hasattr(sys, '_MEIPASS'):  # PyInstaller环境
            app_path = os.path.dirname(sys.executable)
        else:  # 开发环境
            app_path = os.path.dirname(os.path.abspath(__file__))
            
        # 检查各种可能的pymysql路径
        paths_to_check = [
            app_path,
            os.path.join(app_path, 'pymysql'),
            r"D:\Work\DevDemos\PythonDemos\MF_System\dist",
            os.path.join(r"D:\Work\DevDemos\PythonDemos\MF_System\dist", 'pymysql'),
            os.path.abspath('.')
        ]
        
        # 构建调试信息
        debug_info = f"应用路径: {app_path}\n\n"
        debug_info += f"MySQL可用: {MYSQL_AVAILABLE}\n\n"
        debug_info += "检查pymysql路径:\n"
        
        for path in paths_to_check:
            exists = os.path.exists(path)
            debug_info += f"{path}: {'存在' if exists else '不存在'}\n"
            
            if exists and os.path.isdir(path):
                try:
                    files = os.listdir(path)
                    if path.endswith('pymysql') and '__init__.py' in files:
                        debug_info += f"  - 包含__init__.py: 是\n"
                    elif 'pymysql' in files:
                        pymysql_path = os.path.join(path, 'pymysql')
                        if os.path.isdir(pymysql_path):
                            pymysql_files = os.listdir(pymysql_path)
                            debug_info += f"  - pymysql子文件夹: 存在\n"
                            debug_info += f"  - pymysql文件夹内容: {pymysql_files[:5]}等\n"
                except Exception as e:
                    debug_info += f"  - 无法读取目录内容: {str(e)}\n"
        
        debug_info += "\nsys.path内容:\n"
        for p in sys.path[:5]:
            debug_info += f"- {p}\n"
        
        # 创建一个简单的对话框显示信息
        debug_dialog = QDialog(self)
        debug_dialog.setWindowTitle("驱动诊断信息")
        debug_dialog.resize(600, 400)
        layout = QVBoxLayout(debug_dialog)
        
        text_display = QTextBrowser()
        text_display.setText(debug_info)
        layout.addWidget(text_display)
        
        # 添加一个刷新按钮，手动尝试再次导入
        refresh_btn = QPushButton("尝试手动加载驱动")
        refresh_btn.clicked.connect(self.try_manual_load)
        layout.addWidget(refresh_btn)
        
        # 添加一个确定按钮关闭对话框
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(debug_dialog.accept)
        layout.addWidget(close_btn)
        
        debug_dialog.exec_()
    
    def try_manual_load(self):
        """尝试手动加载驱动"""
        global MYSQL_AVAILABLE
        
        # 请用户选择pymysql文件夹位置
        folder_path = QFileDialog.getExistingDirectory(self, "选择pymysql文件夹所在目录")
        
        if not folder_path:
            return
            
        try:
            # 检查选择的路径是否包含pymysql
            pymysql_path = os.path.join(folder_path, 'pymysql')
            
            if not os.path.exists(pymysql_path):
                QMessageBox.warning(self, "错误", f"所选文件夹 {folder_path} 中未找到pymysql文件夹")
                return
                
            # 检查是否是有效的pymysql包
            init_file = os.path.join(pymysql_path, '__init__.py')
            if not os.path.exists(init_file):
                QMessageBox.warning(self, "错误", f"pymysql文件夹中未找到__init__.py文件，不是有效的Python包")
                return
                
            # 将路径添加到sys.path
            if folder_path not in sys.path:
                sys.path.insert(0, folder_path)
                
            # 尝试导入
            try:
                # 先卸载可能已经导入的模块
                if 'pymysql' in sys.modules:
                    del sys.modules['pymysql']
                    
                import pymysql
                MYSQL_AVAILABLE = True
                
                # 更新UI状态
                self.check_mysql_driver()
                
                QMessageBox.information(self, "成功", "成功导入pymysql驱动！现在您可以使用MySQL功能了。")
            except ImportError as e:
                QMessageBox.critical(self, "导入失败", f"尝试导入pymysql失败: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"尝试加载驱动时发生错误: {str(e)}")
            
    def check_mysql_driver(self):
        """检查MySQL驱动状态"""
        # 更新驱动状态显示
        if MYSQL_AVAILABLE:
            self.driver_status.setText("<b>MySQL驱动状态:</b> <span style=\"color:green\">已安装</span>")
            self.refresh_db_btn.setEnabled(True)
            self.connect_btn.setEnabled(True)
        else:
            self.driver_status.setText("<b>MySQL驱动状态:</b> <span style=\"color:red\">未安装</span>")
            self.refresh_db_btn.setEnabled(False)
            self.connect_btn.setEnabled(False)
            
            # 添加驱动安装提示
            if not hasattr(self, 'driver_tips'):
                self.driver_tips = QLabel("请将pymysql文件夹放在程序同级目录下，然后重启应用")
                self.driver_tips.setStyleSheet("color: red; font-weight: bold;")
                self.layout.insertWidget(1, self.driver_tips)
    
    def on_db_selected(self, db_name):
        """当用户从下拉列表选择数据库时触发"""
        if db_name:
            self.dbname_edit.setText(db_name)
    
    def fetch_database_list(self):
        """获取服务器上的数据库列表"""
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # 检查连接参数
        if not host or not port or not username:
            QMessageBox.warning(self, "参数不足", "请填写主机、端口和用户名")
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 连接MySQL服务器
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password
            )
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW DATABASES")
                    db_list = [row[0] for row in cursor.fetchall()]
            finally:
                connection.close()
            
            # 清空并重新填充下拉框
            self.db_list_combo.clear()
            self.db_list_combo.addItems(db_list)
            
            # 显示数据库选择控件
            self.db_list_label.setVisible(True)
            self.db_list_combo.setVisible(True)
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "成功", f"已获取到 {len(db_list)} 个数据库")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "失败", f"获取数据库列表失败: {str(e)}")
    
    def test_connection(self):
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 收集连接参数
        params = {
            'host': self.host_edit.text().strip(),
            'port': self.port_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'dbname': self.dbname_edit.text().strip()
        }
        
        # 为MySQL设置默认值
        if not params['dbname']:
            params['dbname'] = "hairsalon"
            self.dbname_edit.setText(params['dbname'])
        
        try:
            # 检查参数
            if not params['host'] or not params['port'] or not params['username'] or not params['dbname']:
                raise ValueError("请填写所有必要的连接参数")
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 执行连接测试
            connection = pymysql.connect(
                host=params['host'],
                port=int(params['port']),
                user=params['username'],
                password=params['password'],
                database=params['dbname']
            )
            connection.close()
            
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "连接成功", "数据库连接测试成功！")
            
            # 启用初始化和同步按钮
            self.init_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
            self.init_status.setText("可以初始化数据库")
            self.init_status.setStyleSheet("color: green;")
            
        except pymysql.err.OperationalError as e:
            QApplication.restoreOverrideCursor()
            
            # 检查是否为"未知数据库"错误，这意味着服务器连接成功，但数据库不存在
            if e.args[0] == 1049:  # 未知数据库错误代码
                reply = QMessageBox.question(self, "数据库不存在", 
                                           f"数据库 '{params['dbname']}' 不存在。是否要创建它？",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    self.create_database(params)
                else:
                    self.init_btn.setEnabled(False)
                    self.sync_btn.setEnabled(False)
            else:
                QMessageBox.critical(self, "连接失败", f"无法连接到数据库: {str(e)}")
                self.init_btn.setEnabled(False)
                self.sync_btn.setEnabled(False)
                self.init_status.setText("数据库连接失败")
                self.init_status.setStyleSheet("color: red;")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "连接失败", f"无法连接到数据库: {str(e)}")
            self.init_btn.setEnabled(False)
            self.sync_btn.setEnabled(False)
            self.init_status.setText("数据库连接失败")
            self.init_status.setStyleSheet("color: red;")
    
    def create_database(self, params):
        """创建数据库"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 连接到MySQL服务器而不指定数据库
            connection = pymysql.connect(
                host=params['host'],
                port=int(params['port']),
                user=params['username'],
                password=params['password']
            )
            
            try:
                with connection.cursor() as cursor:
                    # 创建数据库
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{params['dbname']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
                
                QApplication.restoreOverrideCursor()
                QMessageBox.information(self, "创建成功", f"数据库 '{params['dbname']}' 已创建")
                
                # 启用初始化按钮
                self.init_btn.setEnabled(True)
                self.init_status.setText("请初始化数据库")
                self.init_status.setStyleSheet("color: green;")
                
            finally:
                connection.close()
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "创建失败", f"创建数据库失败: {str(e)}")
    
    def init_database(self):
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 确认初始化
        reply = QMessageBox.question(self, "确认初始化", 
                                    "初始化将创建新的数据库表结构，如果表已存在，可能会清除现有数据。是否继续？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            host = self.host_edit.text().strip()
            port = self.port_edit.text().strip()
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            dbname = self.dbname_edit.text().strip()
            
            # 如果数据库名为空，使用默认值
            if not dbname:
                dbname = "hairsalon"
                self.dbname_edit.setText(dbname)
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=dbname
            )
            
            try:
                with connection.cursor() as cursor:
                    # 创建会员表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS members (
                        id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        gender VARCHAR(10),
                        birthday VARCHAR(20),
                        balance DECIMAL(10, 2) DEFAULT 0
                    )
                    """)
                    
                    # 创建消费记录表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS consumes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id VARCHAR(50),
                        order_id VARCHAR(50) NOT NULL,
                        time DATETIME NOT NULL,
                        item VARCHAR(100) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                    )
                    """)
                    
                    # 创建充值记录表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recharges (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id VARCHAR(50) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        time DATETIME NOT NULL,
                        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                    )
                    """)
                    
                    # 创建服务项目表
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL
                    )
                    """)
                    
                connection.commit()
            finally:
                connection.close()
            
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "初始化成功", "数据库表结构创建成功！")
            self.init_status.setText("数据库已初始化")
            self.init_status.setStyleSheet("color: green;")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "初始化失败", f"数据库初始化失败: {str(e)}")
            self.init_status.setText("数据库初始化失败")
            self.init_status.setStyleSheet("color: red;")
    
    def sync_data(self):
        # 与原来的功能相同，只是需要检查MySQL驱动
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "驱动缺失", "未找到MySQL驱动，请将pymysql文件夹放在程序同级目录下，然后重启应用")
            return
            
        # 确认同步
        reply = QMessageBox.question(self, "确认同步", 
                                    "将本地JSON数据同步到数据库可能会覆盖数据库中的现有数据。是否继续？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # 显示进度条
            self.sync_progress.setValue(0)
            self.sync_progress.setVisible(True)
            self.sync_status.setText("同步中...")
            
            # 获取数据库连接参数
            host = self.host_edit.text().strip()
            port = self.port_edit.text().strip()
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            dbname = self.dbname_edit.text().strip()

            # 连接到MySQL数据库
            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=dbname
            )
            
            try:
                # 读取本地会员数据
                members = self.db.get_all_members()
                total_items = len(members)
                if total_items == 0:
                    self.sync_progress.setVisible(False)
                    self.sync_status.setText("没有会员数据可同步")
                    return
                
                progress_step = 100 / (total_items + 2)  # +2 for services and other steps
                progress = 0
                
                with connection.cursor() as cursor:
                    # 1. 同步服务项目
                    services_path = resource_path('data/services.json')
                    self.sync_status.setText("同步服务项目...")
                    if os.path.exists(services_path):
                        with open(services_path, 'r', encoding='utf-8') as f:
                            services = json.load(f)
                        
                        # 清空服务表
                        cursor.execute("TRUNCATE TABLE services")
                        
                        # 插入服务项目
                        for service in services:
                            cursor.execute(
                                "INSERT INTO services (name, price) VALUES (%s, %s)", 
                                (service.get('name', ''), service.get('price', 0))
                            )
                    
                    # 更新进度
                    progress += progress_step
                    self.sync_progress.setValue(int(progress))
                    QApplication.processEvents()  # 保持UI响应
                    
                    # 2. 同步会员数据
                    self.sync_status.setText("同步会员数据...")
                    
                    # 清空会员相关表(需要按照外键约束顺序)
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")  # 暂时禁用外键检查
                    cursor.execute("TRUNCATE TABLE consumes")
                    cursor.execute("TRUNCATE TABLE recharges")
                    cursor.execute("TRUNCATE TABLE members")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")  # 重新启用外键检查
                    
                    # 插入会员数据
                    for i, member in enumerate(members):
                        # 插入会员基本信息
                        cursor.execute(
                            "INSERT INTO members (id, name, phone, gender, birthday, balance) VALUES (%s, %s, %s, %s, %s, %s)",
                            (
                                member.get('id', ''),
                                member.get('name', ''),
                                member.get('phone', ''),
                                member.get('gender', ''),
                                member.get('birthday', ''),
                                member.get('balance', 0)
                            )
                        )
                        
                        # 获取这个会员的消费记录
                        consume_records = self.db.get_consume_records(member['id'])
                        for record in consume_records:
                            cursor.execute(
                                "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                                (
                                    member.get('id', ''),
                                    record.get('order_id', ''),
                                    record.get('time', ''),
                                    record.get('item', ''),
                                    record.get('amount', 0)
                                )
                            )
                        
                        # 获取这个会员的充值记录
                        recharge_records = self.db.get_recharge_records(member['id'])
                        for record in recharge_records:
                            cursor.execute(
                                "INSERT INTO recharges (member_id, time, amount) VALUES (%s, %s, %s)",
                                (
                                    member.get('id', ''),
                                    record.get('time', ''),
                                    record.get('amount', 0)
                                )
                            )
                        
                        # 更新进度
                        progress = progress_step + (i + 1) * progress_step
                        self.sync_progress.setValue(int(progress))
                        QApplication.processEvents()  # 保持UI响应
                    
                    # 3. 同步散客消费
                    self.sync_status.setText("同步散客消费...")
                    guest_records = self.db.get_consume_records('guest')
                    for record in guest_records:
                        cursor.execute(
                            "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                            (
                                'guest',
                                record.get('order_id', ''),
                                record.get('time', ''),
                                record.get('item', ''),
                                record.get('amount', 0)
                            )
                        )
                    
                    # 4. 同步手动录入消费
                    manual_records = self.db.get_consume_records('manual')
                    for record in manual_records:
                        cursor.execute(
                            "INSERT INTO consumes (member_id, order_id, time, item, amount) VALUES (%s, %s, %s, %s, %s)",
                            (
                                'manual',
                                record.get('order_id', ''),
                                record.get('time', ''),
                                record.get('item', ''),
                                record.get('amount', 0)
                            )
                        )
                
                # 提交所有更改
                connection.commit()
                
                # 完成进度条
                self.sync_progress.setValue(100)
                QApplication.processEvents()  # 保持UI响应
                
            finally:
                connection.close()
            
            # 隐藏进度条，显示成功状态
            self.sync_progress.setVisible(False)
            self.sync_status.setText(f"同步完成！共同步 {total_items} 名会员及相关记录")
            self.sync_status.setStyleSheet("color: green;")
            
            QMessageBox.information(self, "同步成功", "数据已成功同步到数据库！")
            
        except Exception as e:
            self.sync_progress.setVisible(False)
            self.sync_status.setText("同步失败")
            self.sync_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "同步失败", f"数据同步过程中出错: {str(e)}")
            print(f"同步错误: {str(e)}")
            print(traceback.format_exc())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = JsonDB()
        self.setWindowTitle('美发店会员管理系统_v1.0')
        self.resize(900, 600)
        self.manual_win = None
        self.members_cache = self.load_all_members()
        # 设置问号按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)
        self.init_ui()
        # 设置固定的界面元素大小
        self.set_fixed_ui_size()
    
    # 重写帮助事件，显示作者信息
    def event(self, event):
        if event.type() == QEvent.WhatsThis:
            QMessageBox.about(self, "关于", "美发店会员管理系统\n\n版本: v1.0\n© 2023-2025 美发店管理系统")
            return True
        return super().event(event)
    
    # 设置固定的UI大小
    def set_fixed_ui_size(self):
        # 设置默认字体大小和控件大小
        default_font = QFont()
        default_font.setPointSize(11)  # 使用正常大小的字体

        # 设置按钮
        buttons = [
            self.search_btn, self.recharge_btn, self.add_consume_btn, 
            self.guest_consume_btn, self.register_btn, self.manual_btn
        ]
        for button in buttons:
            button.setFont(default_font)
            button.setFixedHeight(35)  # 固定高度
            button.setStyleSheet("padding: 4px 10px;")  # 适当的内边距
            
        # 设置表格
        self.consume_table.setFont(default_font)
        self.recharge_table.setFont(default_font)
        self.consume_table.verticalHeader().setDefaultSectionSize(30)  # 固定行高
        self.recharge_table.verticalHeader().setDefaultSectionSize(30)  # 固定行高
        
        # 设置所有标签和输入框
        for label in [self.name_label, self.phone_label, self.gender_label, 
                    self.birthday_label, self.balance_label]:
            label.setFont(default_font)
        
        self.search_edit.setFont(default_font)
        self.search_edit.setFixedHeight(35)  # 固定输入框高度
        
        # 查找并设置所有QLabel的字体
        self.set_all_labels_font(self, default_font)
    
    # 递归设置所有QLabel的字体
    def set_all_labels_font(self, parent_widget, font):
        # 设置当前控件下的所有QLabel字体
        for child in parent_widget.findChildren(QLabel):
            child.setFont(font)
        
        # 递归处理所有QTabWidget的内容
        for tab_widget in parent_widget.findChildren(QTabWidget):
            for i in range(tab_widget.count()):
                tab_page = tab_widget.widget(i)
                self.set_all_labels_font(tab_page, font)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        # 会员管理Tab
        self.member_widget = QWidget()
        self.member_layout = QVBoxLayout(self.member_widget)
        # 查询区
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('输入手机号或姓名')
        self.search_btn = QPushButton('查询')
        self.search_btn.clicked.connect(self.search_member)
        search_layout.addWidget(QLabel('会员查询:'))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        self.member_layout.addLayout(search_layout)
        # 自动补全
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(False)
        self.completer.setFilterMode(Qt.MatchContains)
        self.search_edit.setCompleter(self.completer)
        self.search_edit.textEdited.connect(self.update_completer)
        # 信息区
        info_layout = QFormLayout()
        self.name_label = QLabel('-')
        self.phone_label = QLabel('-')
        self.gender_label = QLabel('-')
        self.birthday_label = QLabel('-')
        self.balance_label = QLabel('0')
        self.recharge_btn = QPushButton('充值')
        self.recharge_btn.clicked.connect(self.recharge)
        info_layout.addRow('姓名:', self.name_label)
        info_layout.addRow('手机号:', self.phone_label)
        info_layout.addRow('性别:', self.gender_label)
        info_layout.addRow('生日:', self.birthday_label)
        h_balance = QHBoxLayout()
        h_balance.addWidget(self.balance_label)
        h_balance.addWidget(self.recharge_btn)
        info_layout.addRow('余额:', h_balance)
        self.member_layout.addLayout(info_layout)
        # 消费记录和充值记录横向并排
        table_layout = QHBoxLayout()
        # 消费记录区
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel('消费记录:'))
        self.consume_table = QTableWidget(0, 4)
        self.consume_table.setHorizontalHeaderLabels(['订单号', '时间', '项目', '金额'])
        left_layout.addWidget(self.consume_table)
        btn_layout = QHBoxLayout()
        self.add_consume_btn = QPushButton('新增消费')
        self.add_consume_btn.clicked.connect(self.add_consume)
        btn_layout.addWidget(self.add_consume_btn)
        self.guest_consume_btn = QPushButton('散客消费')
        self.guest_consume_btn.clicked.connect(self.guest_consume)
        btn_layout.addWidget(self.guest_consume_btn)
        left_layout.addLayout(btn_layout)
        table_layout.addLayout(left_layout)
        # 充值记录区
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel('充值记录:'))
        self.recharge_table = QTableWidget(0, 2)
        self.recharge_table.setHorizontalHeaderLabels(['时间', '金额'])
        right_layout.addWidget(self.recharge_table)
        table_layout.addLayout(right_layout)
        self.member_layout.addLayout(table_layout)
        # 注册按钮和手动入单按钮
        btns_layout = QHBoxLayout()
        self.register_btn = QPushButton('会员注册')
        self.register_btn.clicked.connect(self.open_register)
        btns_layout.addWidget(self.register_btn)
        self.manual_btn = QPushButton('手动入单')
        self.manual_btn.clicked.connect(self.open_manual)
        btns_layout.addWidget(self.manual_btn)
        self.member_layout.addLayout(btns_layout)
        self.member_widget.setLayout(self.member_layout)
        self.tabs.addTab(self.member_widget, '会员管理')
        # 数据统计Tab
        self.stats_dialog = StatsDialog(self.db, self)
        self.tabs.addTab(self.stats_dialog, '数据统计')
        # 服务设置Tab
        self.service_setting = ServiceSettingWidget(self)
        self.tabs.addTab(self.service_setting, '服务设置')
        # 会员删除Tab
        self.delete_member_widget = DeleteMemberWidget(self.db, self)
        self.tabs.addTab(self.delete_member_widget, '会员删除')
        # 关于Tab
        self.about_widget = AboutWidget(self)
        self.tabs.addTab(self.about_widget, '关于')
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.current_member = None
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def load_all_members(self):
        # 读取所有会员，返回列表
        try:
            import json
            members_path = resource_path('data/members.json')
            with open(members_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def update_completer(self, text):
        # 模糊匹配会员姓名或手机号
        if not text:
            self.completer_model.setStringList([])
            return
        matches = []
        for m in self.load_all_members():
            if text in m.get('name', '') or text in m.get('phone', ''):
                matches.append(f"{m.get('name','')}（{m.get('phone','')}）")
        self.completer_model.setStringList(matches)

    def search_member(self):
        key = self.search_edit.text().strip()
        # 支持"姓名（手机号）"格式
        if '（' in key and '）' in key:
            key = key.split('（')[1].split('）')[0]
        member = self.db.get_member(key)
        if not member:
            QMessageBox.information(self, '提示', '未找到会员')
            self.show_member(None)
            return
        self.show_member(member)

    def show_member(self, member):
        self.current_member = member
        if not member:
            self.name_label.setText('-')
            self.phone_label.setText('-')
            self.gender_label.setText('-')
            self.birthday_label.setText('-')
            self.balance_label.setText('0')
            self.consume_table.setRowCount(0)
            self.recharge_table.setRowCount(0)
            return
        self.name_label.setText(member.get('name', '-'))
        self.phone_label.setText(member.get('phone', '-'))
        self.gender_label.setText(member.get('gender', '-'))
        self.birthday_label.setText(member.get('birthday', '-'))
        self.balance_label.setText(str(member.get('balance', 0)))
        # 加载消费记录
        records = self.db.get_consume_records(member['id'])
        self.consume_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.consume_table.setItem(row, 0, QTableWidgetItem(str(rec.get('order_id', ''))))
            self.consume_table.setItem(row, 1, QTableWidgetItem(str(rec.get('time', ''))))
            self.consume_table.setItem(row, 2, QTableWidgetItem(str(rec.get('item', ''))))
            self.consume_table.setItem(row, 3, QTableWidgetItem(str(rec.get('amount', 0))))
        # 加载充值记录
        recharges = self.db.get_recharge_records(member['id'])
        self.recharge_table.setRowCount(len(recharges))
        for row, rec in enumerate(recharges):
            self.recharge_table.setItem(row, 0, QTableWidgetItem(str(rec.get('time', ''))))
            self.recharge_table.setItem(row, 1, QTableWidgetItem(str(rec.get('amount', 0))))

    def recharge(self):
        if not self.current_member:
            QMessageBox.warning(self, '提示', '请先查询会员')
            return
        amount, ok = QInputDialog.getInt(self, '充值', '请输入充值金额', min=1)
        if ok:
            self.db.add_recharge(self.current_member['id'], amount)
            member = self.db.get_member(self.current_member['phone'])
            self.show_member(member)
            QMessageBox.information(self, '成功', '充值成功')

    def open_register(self):
        dlg = RegisterDialog(self.db, self)
        if dlg.exec_():
            QMessageBox.information(self, '成功', '会员注册成功')

    def add_consume(self):
        if not self.current_member:
            QMessageBox.warning(self, '提示', '请先查询会员')
            return
        dlg = ConsumeDialog(self.db, self.current_member['id'], self)
        if dlg.exec_():
            member = self.db.get_member(self.current_member['phone'])
            self.show_member(member)

    def guest_consume(self):
        dlg = ConsumeDialog(self.db, 'guest', self)
        dlg.setWindowTitle('散客消费')
        dlg.submit_btn.setText('记录消费')
        dlg.exec_()

    def open_manual(self):
        if self.manual_win is None:
            self.manual_win = ManualOrderDialog(self.db)
        self.manual_win.show()
        self.manual_win.raise_()
        self.manual_win.activateWindow()

    def on_tab_changed(self, idx):
        tab_text = self.tabs.tabText(idx)
        if tab_text == '数据统计':
            self.stats_dialog.update_stats()
            self.stats_dialog.update_orders()
        elif tab_text == '服务设置':
            self.service_setting.load_services()
        elif tab_text == '会员删除':
            # 切换到会员删除选项卡时，先验证密码
            dialog = PasswordDialog(self)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # 密码正确，刷新会员列表
                self.delete_member_widget.refresh_members()
            else:
                # 密码错误或取消，切换回前一个选项卡
                # 找到上一个活动的选项卡索引
                prev_idx = self.tabs.currentIndex() - 1
                if prev_idx < 0:  # 如果没有前一个选项卡，则默认切换到第一个
                    prev_idx = 0
                self.tabs.setCurrentIndex(prev_idx)

if __name__ == '__main__':
    print("程序开始运行...")
    # 确保数据目录存在
    ensure_data_files()
    # 启动应用程序
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
