from extensions import mongo

def get_user_by_username(username):
    try:
        user = mongo.db.users.find_one({'username': username}, {'_id': 0})
        if user:
            return user, None
        return None, {"message": "User not found"}
    except Exception as e:
        return None, {"message": str(e)}

def update_user_profile(username, name, new_username, bio):
    try:
        mongo.db.users.update_one({'username': username}, {'$set': {'name': name, 'username': new_username, 'bio': bio}})
        return {"message": "Profile updated successfully"}, None
    except Exception as e:
        return None, {"message": str(e)}


def update_user_problem_status(username, problem_id, status):
    print(f"[User Service] Updating status for user {username}, problem {problem_id} to {status}")
    return True, None
