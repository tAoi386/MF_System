class Member:
    def __init__(self, id, name, phone, gender=None, birthday=None, balance=0):
        self.id = id
        self.name = name
        self.phone = phone
        self.gender = gender
        self.birthday = birthday
        self.balance = balance

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'gender': self.gender,
            'birthday': self.birthday,
            'balance': self.balance
        }

    @staticmethod
    def from_dict(data):
        return Member(
            id=data.get('id'),
            name=data.get('name'),
            phone=data.get('phone'),
            gender=data.get('gender'),
            birthday=data.get('birthday'),
            balance=data.get('balance', 0)
        ) 