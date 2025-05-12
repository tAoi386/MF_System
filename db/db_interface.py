import abc

class DBInterface(abc.ABC):
    @abc.abstractmethod
    def get_member(self, phone_or_name):
        pass

    @abc.abstractmethod
    def add_member(self, member_info):
        pass

    @abc.abstractmethod
    def update_member(self, member_id, update_info):
        pass

    @abc.abstractmethod
    def add_recharge(self, member_id, amount):
        pass

    @abc.abstractmethod
    def get_recharge_records(self, member_id):
        pass

    @abc.abstractmethod
    def add_consume_record(self, member_id, record):
        pass

    @abc.abstractmethod
    def get_consume_records(self, member_id):
        pass 