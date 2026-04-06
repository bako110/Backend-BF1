from app.models.like import Like
from app.models.user import User
from app.models.movie import Movie
from app.models.breakingNews import BreakingNews
from app.models.divertissement import Divertissement
from app.models.reel import Reel
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.sport import Sport
from app.models.emission_category import EmissionCategory
from app.models.series import Series
from app.models.archive import Archive
from app.models.tele_realite import TeleRealite
from app.utils.engagement import increment_like
from app.schemas.like import LikeCreate
from typing import List, Optional, Dict, Any

async def toggle_like(user_id: str, data: LikeCreate) -> Dict[str, any]:
    """Toggle like (ajouter ou retirer) - évite les doublons"""
    try:
        print(f"🔍 Toggle like - User: {user_id}, Content: {data.content_id}, Type: {data.content_type}")
        
        # Pour le livestream, pas besoin de vérifier l'existence du contenu
        if data.content_type != "livestream":
            # Vérifier que le contenu existe
            content = await _get_content(data.content_type, data.content_id)
            if content:
                print(f"✅ Contenu trouvé: {getattr(content, 'title', None) or getattr(content, 'name', None)}")
            
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
            await existing_like.delete()
            if data.content_type != "livestream":
                await increment_like(data.content_type, data.content_id, -1)
            new_count = await count_likes(data.content_id, data.content_type)
            return {"success": True, "action": "unliked", "likes": new_count}
        else:
            like = Like(
                user_id=user_id,
                content_id=data.content_id,
                content_type=data.content_type
            )
            await like.insert()
            if data.content_type != "livestream":
                await increment_like(data.content_type, data.content_id, 1)
            new_count = await count_likes(data.content_id, data.content_type)
            return {"success": True, "action": "liked", "likes": new_count, "like_id": str(like.id)}
    except Exception as e:
        print(f"❌ Erreur dans toggle_like: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


CONTENT_MODELS = {
    "movie": Movie,
   
    "breaking_news": BreakingNews,
    "divertissement": Divertissement,
    "reel": Reel,
    "reportage": Reportage,
    "jtandmag": JTandMag,
    "sport": Sport,
    "emission_category": EmissionCategory,
    "series": Series,
    "archive": Archive,
    "tele_realite": TeleRealite,
    "event": TeleRealite,
}


async def _get_content(content_type: str, content_id: str):
    model = CONTENT_MODELS.get(content_type)
    if not model:
        return None
    return await model.get(content_id)

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
    try:
        likes = await Like.find(
            Like.content_id == content_id,
            Like.content_type == content_type
        ).to_list()
        return len(likes)
    except Exception as e:
        print(f"❌ Erreur count_likes: {str(e)}")
        return 0

async def remove_like(like_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Supprimer un like (auteur ou admin)"""
    like = await Like.get(like_id)
    if not like:
        return False
    
    if like.user_id != user_id and not is_admin:
        return False
    content_id = like.content_id
    content_type = like.content_type
    await like.delete()
    await increment_like(content_type, content_id, -1)
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
