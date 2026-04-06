from app.models.reel import Reel
from app.schemas.reel import ReelCreate, ReelUpdate
from typing import List, Optional
from datetime import datetime, timedelta
import math


async def create_reel(data: ReelCreate) -> Reel:
    reel = Reel(**data.dict())
    await reel.insert()
    return reel


# ─── ALGORITHME DE RECOMMANDATION ─────────────────────────────────────────────

def calculate_reel_score(reel: dict, viewer_seen_ids: set = None) -> float:
    """
    Algorithme de recommandation inspiré TikTok/Instagram Reels.

    5 signaux combinés :
    1. Retention Score   — taux de completion (signal #1 chez TikTok)
    2. Engagement Score  — likes, comments, shares, saves pondérés
    3. Trending Boost    — vitesse d'engagement sur les 48 dernières heures
    4. Time Decay        — pénalité progressive pour les contenus anciens
    5. Diversity Penalty — pénalise les reels déjà vus pour diversifier le feed
    """
    likes        = reel.get('likes', 0)
    comments     = reel.get('comments', 0)
    shares       = reel.get('shares', 0)
    saves        = reel.get('saves', 0)
    views        = max(reel.get('views', 1), 1)
    completions  = reel.get('watch_completions', 0)
    watch_time   = reel.get('watch_time_total', 0.0)
    duration     = reel.get('duration') or 30.0  # durée par défaut 30s
    recent_likes = reel.get('recent_likes', 0)
    recent_views = max(reel.get('recent_views', 1), 1)
    recent_shares= reel.get('recent_shares', 0)
    created_at   = reel.get('created_at')

    # ── 1. RETENTION SCORE (0-500 pts) ───────────────────���─────────────────
    # Signal le plus important : est-ce que les gens regardent jusqu'au bout ?
    completion_rate = completions / views  # % de gens qui finissent
    avg_watch_time  = watch_time / views if views > 0 else 0
    watch_ratio     = min(avg_watch_time / duration, 1.0)  # 0 à 1

    # Pondération : completion_rate prime sur watch_ratio
    retention_score = (completion_rate * 0.7 + watch_ratio * 0.3) * 500

    # ── 2. ENGAGEMENT SCORE (0-400 pts) ────────────────────────────────────
    # Saves > Shares > Comments > Likes (ordre d'importance de l'intention)
    engagement_raw = (
        saves    * 15 +   # sauvegarde = très fort signal d'intérêt
        shares   * 10 +   # partage = signal viral
        comments * 5  +   # commentaire = engagement actif
        likes    * 1      # like = engagement passif
    )
    engagement_rate  = engagement_raw / views
    engagement_score = math.log1p(engagement_rate * 100) * 80  # log pour lisser

    # ── 3. TRENDING BOOST (multiplicateur 1x–4x) ───────────────────────────
    # Vitesse d'engagement récente (dernières 48h) — détecte les contenus qui décollent
    recent_engagement = recent_likes * 1 + recent_shares * 10
    trending_velocity = recent_engagement / recent_views  # engagement récent / vues récentes

    if trending_velocity > 0.5:    # très viral maintenant
        trending_mult = 4.0
    elif trending_velocity > 0.2:  # viral
        trending_mult = 3.0
    elif trending_velocity > 0.05: # bonne dynamique
        trending_mult = 2.0
    elif trending_velocity > 0.01: # légère dynamique
        trending_mult = 1.5
    else:
        trending_mult = 1.0

    # ── 4. TIME DECAY (0.05–1.0) ───────────────────────────────────────────
    # Contenus récents favorisés, mais pas à 100% — les bons anciens restent visibles
    now = datetime.utcnow()
    if created_at:
        age_hours = max((now - created_at).total_seconds() / 3600, 0.1)
    else:
        age_hours = 24.0

    # Demi-vie de 36h — plus douce que avant (24h) pour garder les bons contenus
    # Plancher à 0.05 : un vieux reel très populaire garde 5% de son score
    time_decay = max(math.exp(-age_hours / (36 * 1.44)), 0.05)

    # Boost pour les contenus très frais (< 2h) — fenêtre de découverte
    if age_hours < 2:
        time_decay = min(time_decay * 1.5, 1.0)

    # ── 5. DIVERSITY PENALTY ───────────────────────────────────────────────
    # Pénalise les reels déjà vus pour diversifier le feed
    reel_id = str(reel.get('id', ''))
    diversity_mult = 0.1 if (viewer_seen_ids and reel_id in viewer_seen_ids) else 1.0

    # ── SCORE FINAL ────────────────────────────────────────────────────────
    base_score = retention_score + engagement_score
    final_score = base_score * trending_mult * time_decay * diversity_mult

    return final_score


async def list_reels(
    skip: int = 0,
    limit: int = 20,
    seen_ids: Optional[List[str]] = None
) -> dict:
    """
    Retourne les reels triés par score de recommandation.
    seen_ids : IDs des reels déjà vus par l'utilisateur (pour la diversification).
    """
    try:
        total = await Reel.find_all().count()
        seen_set = set(seen_ids) if seen_ids else set()

        # On récupère plus de reels que demandé pour avoir du choix après scoring
        fetch_limit = max(limit * 5, 200)
        reels = await Reel.find_all().sort(-Reel.created_at).limit(fetch_limit).to_list()

        scored_reels = []
        for reel in reels:
            reel_dict = reel.dict()
            reel_dict['id'] = str(reel.id)
            if reel.video_url:
                reel_dict['video_url'] = str(reel.video_url)
                reel_dict['videoUrl'] = str(reel.video_url)

            score = calculate_reel_score(reel_dict, seen_set)
            scored_reels.append((score, reel_dict))

        # Trier par score décroissant
        scored_reels.sort(key=lambda x: x[0], reverse=True)

        # Pagination sur les résultats triés
        paginated = scored_reels[skip:skip + limit]
        result = [r for _, r in paginated]

        return {"items": result, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        print(f"❌ Erreur list_reels: {str(e)}")
        return {"items": [], "total": 0, "skip": skip, "limit": limit}


async def update_reel(reel_id: str, data: ReelUpdate) -> Optional[Reel]:
    reel = await Reel.get(reel_id)
    if not reel:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reel, field, value)
    reel.updated_at = datetime.utcnow()
    await reel.save()
    return reel


async def delete_reel(reel_id: str) -> bool:
    reel = await Reel.get(reel_id)
    if not reel:
        return False
    await reel.delete()
    return True


async def get_reel(reel_id: str) -> Optional[Reel]:
    return await Reel.get(reel_id)


# ─── MÉTRIQUES DE VISIONNAGE ──────────────────────────────────────────────────

async def track_reel_watch(
    reel_id: str,
    watch_seconds: float,
    completed: bool,
    user_id: Optional[str] = None,
    client_ip: Optional[str] = None
) -> bool:
    """
    Enregistre une session de visionnage :
    - watch_seconds : combien de secondes l'utilisateur a regardé
    - completed     : a-t-il regardé jusqu'au bout ?
    - Anti-doublon 24h sur les vues (par user_id ou IP)
    """
    try:
        reel = await Reel.get(reel_id)
        if not reel:
            return False

        col = Reel.get_motor_collection()
        now = datetime.utcnow()

        # Anti-doublon 24h sur les vues
        from app.models.view_log import ViewLog
        identifier = user_id or client_ip or "anonymous"
        cutoff = now - timedelta(hours=24)
        already_viewed = await ViewLog.find_one(
            ViewLog.content_id == reel_id,
            ViewLog.content_type == "reel",
            ViewLog.identifier == identifier,
            ViewLog.created_at >= cutoff
        )

        updates = {
            "$inc": {
                "watch_time_total": watch_seconds,
                "recent_views": 1,
            }
        }

        if not already_viewed:
            updates["$inc"]["views"] = 1
            # Enregistrer la vue pour l'anti-doublon
            log = ViewLog(
                content_id=reel_id,
                content_type="reel",
                identifier=identifier,
                created_at=now
            )
            await log.insert()

        if completed:
            updates["$inc"]["watch_completions"] = 1

        from bson import ObjectId
        await col.update_one({"_id": ObjectId(reel_id)}, updates)

        # Recalculer le trending_score
        await _refresh_trending_score(reel_id)

        return True
    except Exception as e:
        print(f"❌ Erreur track_reel_watch: {e}")
        return False


async def increment_reel_view(reel_id: str) -> bool:
    """Compatibilité avec l'ancien endpoint /view (sans données de watch time)"""
    return await track_reel_watch(reel_id, watch_seconds=0, completed=False)


async def increment_reel_save(reel_id: str) -> bool:
    """Incrémenter le compteur de sauvegardes"""
    try:
        from bson import ObjectId
        col = Reel.get_motor_collection()
        result = await col.update_one(
            {"_id": ObjectId(reel_id)},
            {"$inc": {"saves": 1}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Erreur increment_reel_save: {e}")
        return False


async def increment_reel_recent_like(reel_id: str) -> bool:
    """Incrémenter le compteur de likes récents (appelé par like_service)"""
    try:
        from bson import ObjectId
        col = Reel.get_motor_collection()
        await col.update_one(
            {"_id": ObjectId(reel_id)},
            {"$inc": {"recent_likes": 1}}
        )
        await _refresh_trending_score(reel_id)
        return True
    except Exception as e:
        print(f"❌ Erreur increment_reel_recent_like: {e}")
        return False


async def increment_reel_recent_share(reel_id: str) -> bool:
    """Incrémenter le compteur de partages récents (appelé par share_service)"""
    try:
        from bson import ObjectId
        col = Reel.get_motor_collection()
        await col.update_one(
            {"_id": ObjectId(reel_id)},
            {"$inc": {"recent_shares": 1}}
        )
        await _refresh_trending_score(reel_id)
        return True
    except Exception as e:
        print(f"❌ Erreur increment_reel_recent_share: {e}")
        return False


async def _refresh_trending_score(reel_id: str):
    """Recalcule et persiste le trending_score en base"""
    try:
        reel = await Reel.get(reel_id)
        if not reel:
            return
        reel_dict = reel.dict()
        reel_dict['id'] = str(reel.id)
        score = calculate_reel_score(reel_dict)
        from bson import ObjectId
        col = Reel.get_motor_collection()
        await col.update_one(
            {"_id": ObjectId(reel_id)},
            {"$set": {"trending_score": score, "trending_updated_at": datetime.utcnow()}}
        )
    except Exception as e:
        print(f"❌ Erreur _refresh_trending_score: {e}")


async def reset_recent_metrics():
    """
    Remet à zéro les métriques récentes (recent_likes, recent_views, recent_shares).
    À appeler toutes les 48h depuis le scheduler.
    """
    try:
        col = Reel.get_motor_collection()
        result = await col.update_many(
            {},
            {"$set": {"recent_likes": 0, "recent_views": 0, "recent_shares": 0}}
        )
        print(f"✅ [Reels] Métriques récentes remises à zéro ({result.modified_count} reels)")
    except Exception as e:
        print(f"❌ [Reels] Erreur reset_recent_metrics: {e}")
