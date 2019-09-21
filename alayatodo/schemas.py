from alayatodo import ma
from alayatodo.models import Todo, User


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username")


class TodoSchema(ma.Schema):
    class Meta:
        model = Todo
        fields = ("id", "user_id", "description", "is_completed")


user_schema = UserSchema()
todo_schema = TodoSchema()
