# str
def refresh_token(user_id, device_id):
    return f"rt:user:{user_id}:device:{device_id}"


def otp_shash_token(user_id):
    return f"otp:shash:{user_id}"


# pubsub
def sync_vault_pubsub(user_id):
    return f"sync:v:{user_id}"
