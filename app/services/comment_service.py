from app.models.comment import Comment
from app.models.user import User
from app.models.movie import Movie
from app.models.show import Show
from app.schemas.comment import CommentCreate, CommentUpdate
from typing import List, Optional
from datetime import datetime

async def add_comment(user_id: str, data: CommentCreate) -> Optional[Comment]:
    """Ajouter un commentaire avec validation du contenu"""
    # Vérifier que le contenu existe
    if data.content_type == "movie":
        content = await Movie.get(data.content_id)
    else:
        content = await Show.get(data.content_id)
    
    if not content:
        return None
    
    comment = Comment(
        user_id=user_id,
        content_id=data.content_id,
        content_type=data.content_type,
        text=data.text
    )
    await comment.insert()
    return comment

async def get_comment(comment_id: str) -> Optional[Comment]:
    """Récupérer un commentaire par ID"""
    return await Comment.get(comment_id)

async def get_comments(content_id: str, content_type: str, skip: int = 0, limit: int = 50) -> List[dict]:
    """Récupérer les commentaires d'un contenu avec infos utilisateur"""
    comments = await Comment.find(
        Comment.content_id == content_id,
        Comment.content_type == content_type
    ).sort(-Comment.created_at).skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos utilisateur
    enriched_comments = []
    for comment in comments:
        user = await User.get(comment.user_id)
        comment_dict = comment.dict()
        comment_dict['username'] = user.username if user else "Utilisateur inconnu"
        enriched_comments.append(comment_dict)
    
    return enriched_comments

async def get_user_comments(user_id: str, skip: int = 0, limit: int = 50) -> List[Comment]:
    """Récupérer tous les commentaires d'un utilisateur"""
    return await Comment.find(
        Comment.user_id == user_id
    ).sort(-Comment.created_at).skip(skip).limit(limit).to_list()

async def update_comment(comment_id: str, user_id: str, data: CommentUpdate) -> Optional[Comment]:
    """Mettre à jour un commentaire (seulement par l'auteur)"""
    comment = await Comment.get(comment_id)
    if not comment or comment.user_id != user_id:
        return None
    
    comment.text = data.text
    comment.updated_at = datetime.utcnow()
    await comment.save()
    return comment

async def delete_comment(comment_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Supprimer un commentaire (auteur ou admin)"""
    comment = await Comment.get(comment_id)
    if not comment:
        return False
    
    if comment.user_id != user_id and not is_admin:
        return False
    
    await comment.delete()
    return True

async def count_comments(content_id: str, content_type: str) -> int:
    """Compter les commentaires d'un contenu"""
    return await Comment.find(
        Comment.content_id == content_id,
        Comment.content_type == content_type
    ).count()

async def get_all_comments(skip: int = 0, limit: int = 1000) -> List[dict]:
    """Récupérer tous les commentaires (pour admin)"""
    comments = await Comment.find().skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos utilisateur
    enriched_comments = []
    for comment in comments:
        user = await User.get(comment.user_id)
        comment_dict = comment.dict()
        comment_dict['username'] = user.username if user else "Utilisateur inconnu"
        enriched_comments.append(comment_dict)
    
    return enriched_comments
