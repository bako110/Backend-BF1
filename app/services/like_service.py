from app.models.like import Like
from app.models.user import User
from app.models.movie import Movie
from app.models.show import Show
from app.schemas.like import LikeCreate
from typing import List, Optional, Dict, Any

async def toggle_like(user_id: str, data: LikeCreate) -> Dict[str, any]:
    """Toggle like (ajouter ou retirer) - évite les doublons"""
    try:
        print(f"🔍 Toggle like - User: {user_id}, Content: {data.content_id}, Type: {data.content_type}")
        
        # Vérifier que le contenu existe
        if data.content_type == "movie":
            content = await Movie.get(data.content_id)
            print(f"📽️ Film trouvé: {content.title if content else 'None'}")
        else:
            content = await Show.get(data.content_id)
            print(f"📺 Émission trouvée: {content.title if content else 'None'}")
        
        if not content:
            print(f"❌ Contenu introuvable: {data.content_id}")
            return {"success": False, "message": "Contenu introuvable"}
        
        # Vérifier si le like existe déjà
        existing_like = await Like.find_one(
            Like.user_id == user_id,
            Like.content_id == data.content_id,
            Like.content_type == data.content_type
        )
        
        if existing_like:
            # Retirer le like
            print(f"💔 Retrait du like existant: {existing_like.id}")
            await existing_like.delete()
            return {"success": True, "action": "unliked", "message": "Like retiré"}
        else:
            # Ajouter le like
            print(f"❤️ Ajout d'un nouveau like")
            like = Like(
                user_id=user_id,
                content_id=data.content_id,
                content_type=data.content_type
            )
            await like.insert()
            print(f"✅ Like ajouté avec succès: {like.id}")
            return {"success": True, "action": "liked", "message": "Like ajouté", "like_id": str(like.id)}
    except Exception as e:
        print(f"❌ Erreur dans toggle_like: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

async def get_like(like_id: str) -> Optional[Like]:
    """Récupérer un like par ID"""
    return await Like.get(like_id)

async def get_likes(content_id: str, content_type: str, skip: int = 0, limit: int = 100) -> List[dict]:
    """Récupérer les likes d'un contenu avec infos utilisateur"""
    likes = await Like.find(
        Like.content_id == content_id,
        Like.content_type == content_type
    ).sort(-Like.created_at).skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos utilisateur
    enriched_likes = []
    for like in likes:
        user = await User.get(like.user_id)
        like_dict = like.dict()
        like_dict['username'] = user.username if user else "Utilisateur inconnu"
        enriched_likes.append(like_dict)
    
    return enriched_likes

async def get_user_likes(user_id: str, content_type: Optional[str] = None) -> List[Like]:
    """Récupérer tous les likes d'un utilisateur"""
    if content_type:
        return await Like.find(
            Like.user_id == user_id,
            Like.content_type == content_type
        ).to_list()
    return await Like.find(Like.user_id == user_id).to_list()

async def check_user_liked(user_id: str, content_id: str, content_type: str) -> bool:
    """Vérifier si un utilisateur a liké un contenu"""
    like = await Like.find_one(
        Like.user_id == user_id,
        Like.content_id == content_id,
        Like.content_type == content_type
    )
    return like is not None

async def count_likes(content_id: str, content_type: str) -> int:
    """Compter les likes d'un contenu"""
    return await Like.find(
        Like.content_id == content_id,
        Like.content_type == content_type
    ).count()

async def remove_like(like_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Supprimer un like (auteur ou admin)"""
    like = await Like.get(like_id)
    if not like:
        return False
    
    if like.user_id != user_id and not is_admin:
        return False
    
    await like.delete()
    return True

async def get_all_likes(skip: int = 0, limit: int = 1000) -> List[dict]:
    """Récupérer tous les likes (pour admin)"""
    likes = await Like.find().skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos utilisateur
    enriched_likes = []
    for like in likes:
        user = await User.get(like.user_id)
        like_dict = like.dict()
        like_dict['username'] = user.username if user else "Utilisateur inconnu"
        enriched_likes.append(like_dict)
    
    return enriched_likes
