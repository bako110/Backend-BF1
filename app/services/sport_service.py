"""
Service pour la gestion des sports
Contient la logique métier pour les opérations sur les sports
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId

from app.models.sport import Sport
from app.schemas.sport import (
    SportCreate, 
    SportUpdate, 
    SportResponse,
    SearchRequest,
    LikeRequest,
    ViewIncrementRequest
)


class SportService:
    """Service pour la gestion des sports"""

    async def _find_sport_by_id(self, sport_id: str) -> Optional[Sport]:
        """
        Méthode utilitaire pour trouver un sport par ID de manière robuste
        """
        print(f"🔍 Recherche de sport avec ID: {sport_id}")
        
        # MÉTHODE 1: Utiliser get() - méthode recommandée par Beanie
        try:
            sport = await Sport.get(sport_id)
            if sport:
                print(f"✅ Sport trouvé via Sport.get(): {sport.id}")
                return sport
        except Exception as e:
            print(f"⚠️ Erreur avec Sport.get(): {e}")
        
        # MÉTHODE 2: Utiliser find_one avec le champ 'id' (alias de _id)
        try:
            sport = await Sport.find_one({"id": sport_id})
            if sport:
                print(f"✅ Sport trouvé via find_one avec id: {sport.id}")
                return sport
        except Exception as e:
            print(f"⚠️ Erreur avec find_one id: {e}")
        
        # MÉTHODE 3: Essayer avec ObjectId
        if ObjectId.is_valid(sport_id):
            try:
                obj_id = ObjectId(sport_id)
                sport = await Sport.find_one({"_id": obj_id})
                if sport:
                    print(f"✅ Sport trouvé via _id avec ObjectId: {sport.id}")
                    return sport
            except Exception as e:
                print(f"⚠️ Erreur avec ObjectId: {e}")
        
        # MÉTHODE 4: Recherche textuelle dans tous les IDs
        try:
            all_sports = await Sport.find({}).to_list()
            for sport in all_sports:
                if str(sport.id) == sport_id:
                    print(f"✅ Sport trouvé via recherche textuelle: {sport.id}")
                    return sport
        except Exception as e:
            print(f"⚠️ Erreur avec recherche textuelle: {e}")
        
        print(f"❌ Aucun sport trouvé avec l'ID: {sport_id}")
        return None

    async def get_all_sports(
        self,
        category: Optional[str] = None,
        featured: Optional[bool] = None,
        is_new: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Récupère tous les sports avec filtres et pagination
        """
        try:
            print(f"📋 Récupération des sports - page: {page}, per_page: {per_page}")
            
            # Vérifier si la collection est initialisée
            try:
                # Test simple pour voir si la collection fonctionne
                test_count = await Sport.find({}).count()
                print(f"📊 Test collection: {test_count} sports trouvés")
            except Exception as collection_error:
                print(f"❌ Erreur de collection: {collection_error}")
                # La collection n'est pas initialisée, retourner vide
                return {
                    "sports": [],
                    "total": 0,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": 0
                }
            
            # Construire le filtre
            filter_dict = {"is_active": True}
            
            if category and category != "toutes":
                filter_dict["category"] = category
            
            if featured is not None:
                filter_dict["featured"] = featured
            
            if is_new is not None:
                filter_dict["is_new"] = is_new

            print(f"🔍 Filtre appliqué: {filter_dict}")

            # Récupérer les sports
            sports = []
            try:
                # Trier par created_at
                sports = await Sport.find(filter_dict).sort("-created_at").skip((page - 1) * per_page).limit(per_page).to_list()
                print(f"✅ Sports récupérés avec tri: {len(sports)}")
            except Exception as sort_error:
                print(f"⚠️ Erreur de tri: {sort_error}")
                try:
                    # Essayer sans tri
                    sports = await Sport.find(filter_dict).skip((page - 1) * per_page).limit(per_page).to_list()
                    print(f"✅ Sports récupérés sans tri: {len(sports)}")
                except Exception as fetch_error:
                    print(f"❌ Erreur de récupération: {fetch_error}")
                    sports = []
            
            # Debug : afficher la structure des sports
            if sports:
                print(f"📋 Structure d'un sport: {list(sports[0].dict().keys())}")
                print(f"🆔 ID du premier sport: {sports[0].dict().get('id')}")
                print(f"🆔 ID Beanie du premier sport: {sports[0].id}")
                print(f"🆔 ID Beanie (type): {type(sports[0].id)}")
            else:
                print("📭 Aucun sport trouvé dans la base de données")
            
            # Compter le total
            total = 0
            try:
                total = await Sport.find(filter_dict).count()
                print(f"📊 Total de sports: {total}")
            except Exception as count_error:
                print(f"❌ Erreur de comptage: {count_error}")
                total = len(sports)  # Utiliser la longueur de la liste récupérée

            result = {
                "sports": [
                    SportResponse.from_orm(sport) 
                    for sport in sports
                ],
            }
            
            # Debug : vérifier le premier résultat
            if result["sports"]:
                first_sport = result["sports"][0]
                print(f"🔍 Premier sport dans le résultat:")
                print(f"  id: {first_sport.id}")
                print(f"  titre: {first_sport.title}")
                print(f"  type id: {type(first_sport.id)}")
            
            result.update({
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
            })
            
            print(f"📤 Résultat retourné: {len(result['sports'])} sports, total: {result['total']}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur globale dans get_all_sports: {e}")
            import traceback
            traceback.print_exc()
            # Retourner un résultat vide en cas d'erreur
            return {
                "sports": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }

    async def get_sport_by_id(self, sport_id: str) -> Dict[str, Any]:
        """
        Récupère un sport spécifique par son ID
        """
        sport = await self._find_sport_by_id(sport_id)

        if not sport or not sport.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sport non trouvé"
            )

        return SportResponse.from_orm(sport)

    async def create_sport(self, sport_data: SportCreate) -> Dict[str, Any]:
        """
        Crée un nouveau sport
        """
        sport = Sport(**sport_data.dict())
        sport.updated_at = datetime.utcnow()
        await sport.insert()  # Utiliser insert() au lieu de save() pour les nouveaux documents

        return SportResponse.from_orm(sport)

    async def update_sport(self, sport_id: str, sport_data: SportUpdate) -> Dict[str, Any]:
        """
        Met à jour un sport existant
        """
        print(f"🔍 Recherche du sport pour mise à jour avec ID: {sport_id}")
        
        sport = await self._find_sport_by_id(sport_id)
        
        if not sport:
            print(f"❌ Sport non trouvé pour mise à jour avec ID: {sport_id}")
            
            # Lister tous les sports disponibles pour le debug
            all_sports = await Sport.find({}).to_list()
            if all_sports:
                print("📋 Sports disponibles:")
                for i, s in enumerate(all_sports[:5]):  # Limiter à 5 pour éviter le spam
                    print(f"  {i+1}. id: {s.id}, titre: {s.title}")
                    print(f"      🆔 ID Beanie: {s.id}, type: {type(s.id)}")
            else:
                print("📭 Aucun sport dans la base de données")
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport non trouvé avec l'ID: {sport_id}"
            )

        # Mettre à jour uniquement les champs fournis
        update_data = sport_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sport, field, value)
        
        sport.updated_at = datetime.utcnow()
        await sport.save()

        print(f"✅ Sport mis à jour avec succès: {sport.id}")
        return SportResponse.from_orm(sport)

    async def delete_sport(self, sport_id: str) -> bool:
        """
        Supprime (désactive) un sport
        """
        print(f"🔍 Recherche du sport avec ID: {sport_id}")
        
        sport = await self._find_sport_by_id(sport_id)
        
        if not sport:
            print(f"❌ Sport non trouvé avec ID: {sport_id}")
            # Lister tous les sports disponibles pour le debug
            all_sports = await Sport.find({}).to_list()
            if all_sports:
                print("📋 Sports disponibles:")
                for i, s in enumerate(all_sports[:5]):
                    print(f"  {i+1}. id: {s.id}, titre: {s.title}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport non trouvé avec l'ID: {sport_id}"
            )

        print(f"✅ Sport trouvé, suppression en cours...")
        # Soft delete : désactiver au lieu de supprimer
        sport.is_active = False
        sport.updated_at = datetime.utcnow()
        await sport.save()

        return True

    async def search_sports(self, search_request: SearchRequest) -> List[Dict[str, Any]]:
        """
        Recherche des sports par terme de recherche
        """
        # Construire le filtre de base
        filter_dict = {"is_active": True}
        
        # Ajouter la recherche texte
        search_term = search_request.query.lower()
        
        # Filtrer par catégorie si spécifié
        if search_request.category and search_request.category != "toutes":
            filter_dict["category"] = search_request.category

        # Rechercher dans plusieurs champs (MongoDB text search)
        sports = await Sport.find(filter_dict).to_list()
        
        # Filtrer manuellement les résultats pour la recherche texte
        filtered_sports = []
        for sport in sports:
            if (search_term in sport.title.lower() or 
                (sport.description and search_term in sport.description.lower()) or
                (sport.presenter and search_term in sport.presenter.lower()) or
                any(search_term in tag.lower() for tag in sport.tags)):
                filtered_sports.append(sport)

        # Trier et paginer
        filtered_sports.sort(key=lambda x: (x.featured, x.date or datetime.min), reverse=True)
        
        start_idx = search_request.offset
        end_idx = start_idx + search_request.limit
        paginated_sports = filtered_sports[start_idx:end_idx]

        return [SportResponse.from_orm(sport) for sport in paginated_sports]

    async def get_featured_sports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les sports en vedette
        """
        sports = await Sport.find(
            {"featured": True, "is_active": True}
        ).sort("-date").limit(limit).to_list()

        return [SportResponse.from_orm(sport) for sport in sports]

    async def get_new_sports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les nouveaux sports
        """
        sports = await Sport.find(
            {"is_new": True, "is_active": True}
        ).sort("-created_at").limit(limit).to_list()

        return [SportResponse.from_orm(sport) for sport in sports]

    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Récupère les catégories avec le nombre de sports
        """
        # Utiliser l'agrégation MongoDB pour compter par catégorie
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        category_counts = await Sport.aggregate(pipeline).to_list()

        # Mapping des noms et icônes (cohérence avec le frontend)
        category_info = {
            'jt': {'name': 'JT', 'icon': 'newspaper'},
            'magazines': {'name': 'Magazines', 'icon': 'book'},
            'documentaires': {'name': 'Docs', 'icon': 'videocam'},
            'divertissement': {'name': 'Show', 'icon': 'happy'},
            'sport': {'name': 'Sport', 'icon': 'football'}
        }

        categories = []
        for item in category_counts:
            category = item['_id']
            count = item['count']
            info = category_info.get(category, {'name': category, 'icon': 'grid'})
            categories.append({
                'id': category,
                'name': info['name'],
                'icon': info['icon'],
                'count': count
            })

        # Ajouter "Toutes" avec le total
        total_count = sum(item['count'] for item in category_counts)
        categories.insert(0, {
            'id': 'toutes',
            'name': 'Toutes',
            'icon': 'grid',
            'count': total_count
        })

        return categories

    async def increment_views(self, sport_id: str, request: Optional[ViewIncrementRequest] = None) -> bool:
        """
        Incrémente le nombre de vues d'un sport
        """
        sport = await self._find_sport_by_id(sport_id)

        if not sport or not sport.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sport non trouvé"
            )

        sport.views += 1
        sport.updated_at = datetime.utcnow()
        await sport.save()

        return True

    async def toggle_like(self, sport_id: str, request: LikeRequest) -> Dict[str, Any]:
        """
        Ajoute ou retire un like d'un sport
        """
        sport = await self._find_sport_by_id(sport_id)

        if not sport or not sport.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sport non trouvé"
            )

        # TODO: Gérer les likes par utilisateur dans une collection séparée
        # Pour l'instant, on incrémente/décrémente simplement le compteur
        
        if request.action == "add":
            sport.likes += 1
        elif request.action == "remove" and sport.likes > 0:
            sport.likes -= 1

        sport.updated_at = datetime.utcnow()
        await sport.save()

        return {
            "id": str(sport.id),
            "likes": sport.likes,
            "action": request.action
        }

    async def get_sport_stats(self, sport_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un sport
        """
        sport = await self._find_sport_by_id(sport_id)

        if not sport or not sport.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sport non trouvé"
            )

        return {
            "id": str(sport.id),
            "views": sport.views,
            "likes": sport.likes,
            "created_at": sport.created_at,
            "updated_at": sport.updated_at
        }