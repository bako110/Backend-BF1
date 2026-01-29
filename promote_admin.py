import asyncio
from app.models.user import User
import sys

async def promote_admin(email):
    user = await User.find_one({"email": email})
    if not user:
        print(f"Utilisateur avec l'email {email} non trouvé.")
        return
    user.is_admin = True
    await user.save()
    print(f"Utilisateur {email} promu admin.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <email>")
    else:
        email = sys.argv[1]
        asyncio.run(promote_admin(email))
