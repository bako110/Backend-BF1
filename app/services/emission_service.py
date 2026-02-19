"""
Service pour la gestion des émissions
Contient la logique métier pour les opérations sur les émissions
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId

from app.models.emission import Emission
from app.schemas.emission import (
    EmissionCreate, 
    EmissionUpdate, 
    EmissionResponse,
    SearchRequest,
    LikeRequest,
    ViewIncrementRequest
)


class EmissionService:
    """Service pour la gestion des émissions"""

    async def _find_emission_by_id(self, emission_id: str) -> Optional[Emission]:
        """
        Méthode utilitaire pour trouver une émission par ID de manière robuste
        """
        print(f"🔍 Recherche d'émission avec ID: {emission_id}")
        
        # MÉTHODE 1: Utiliser get() - méthode recommandée par Beanie
        try:
            emission = await Emission.get(emission_id)
            if emission:
                print(f"✅ Émission trouvée via Emission.get(): {emission.id}")
                return emission
        except Exception as e:
            print(f"⚠️ Erreur avec Emission.get(): {e}")
        
        # MÉTHODE 2: Utiliser find_one avec le champ 'id' (alias de _id)
        try:
            emission = await Emission.find_one({"id": emission_id})
            if emission:
                print(f"✅ Émission trouvée via find_one avec id: {emission.id}")
                return emission
        except Exception as e:
            print(f"⚠️ Erreur avec find_one id: {e}")
        
        # MÉTHODE 3: Essayer avec ObjectId
        if ObjectId.is_valid(emission_id):
            try:
                obj_id = ObjectId(emission_id)
                emission = await Emission.find_one({"_id": obj_id})
                if emission:
                    print(f"✅ Émission trouvée via _id avec ObjectId: {emission.id}")
                    return emission
            except Exception as e:
                print(f"⚠️ Erreur avec ObjectId: {e}")
        
        # MÉTHODE 4: Recherche textuelle dans tous les IDs
        try:
            all_emissions = await Emission.find({}).to_list()
            for emission in all_emissions:
                if str(emission.id) == emission_id:
                    print(f"✅ Émission trouvée via recherche textuelle: {emission.id}")
                    return emission
        except Exception as e:
            print(f"⚠️ Erreur avec recherche textuelle: {e}")
        
        print(f"❌ Aucune émission trouvée avec l'ID: {emission_id}")
        return None

    async def get_all_emissions(
        self,
        category: Optional[str] = None,
        featured: Optional[bool] = None,
        is_new: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Récupère toutes les émissions avec filtres et pagination
        """
        try:
            print(f"📋 Récupération des émissions - page: {page}, per_page: {per_page}")
            
            # Vérifier si la collection est initialisée
            try:
                # Test simple pour voir si la collection fonctionne
                test_count = await Emission.find({}).count()
                print(f"📊 Test collection: {test_count} émissions trouvées")
            except Exception as collection_error:
                print(f"❌ Erreur de collection: {collection_error}")
                # La collection n'est pas initialisée, retourner vide
                return {
                    "emissions": [],
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

            # Récupérer les émissions
            emissions = []
            try:
                # Trier par created_at
                emissions = await Emission.find(filter_dict).sort("-created_at").skip((page - 1) * per_page).limit(per_page).to_list()
                print(f"✅ Émissions récupérées avec tri: {len(emissions)}")
            except Exception as sort_error:
                print(f"⚠️ Erreur de tri: {sort_error}")
                try:
                    # Essayer sans tri
                    emissions = await Emission.find(filter_dict).skip((page - 1) * per_page).limit(per_page).to_list()
                    print(f"✅ Émissions récupérées sans tri: {len(emissions)}")
                except Exception as fetch_error:
                    print(f"❌ Erreur de récupération: {fetch_error}")
                    emissions = []
            
            # Debug : afficher la structure des émissions
            if emissions:
                print(f"📋 Structure d'une émission: {list(emissions[0].dict().keys())}")
                print(f"🆔 ID de la première émission: {emissions[0].dict().get('id')}")
                print(f"🆔 ID Beanie de la première émission: {emissions[0].id}")
                print(f"🆔 ID Beanie (type): {type(emissions[0].id)}")
            else:
                print("📭 Aucune émission trouvée dans la base de données")
            
            # Compter le total
            total = 0
            try:
                total = await Emission.find(filter_dict).count()
                print(f"📊 Total d'émissions: {total}")
            except Exception as count_error:
                print(f"❌ Erreur de comptage: {count_error}")
                total = len(emissions)  # Utiliser la longueur de la liste récupérée

            result = {
                "emissions": [
                    EmissionResponse.from_orm(emission) 
                    for emission in emissions
                ],
            }
            
            # Debug : vérifier le premier résultat
            if result["emissions"]:
                first_emission = result["emissions"][0]
                print(f"🔍 Première émission dans le résultat:")
                print(f"  id: {first_emission.id}")
                print(f"  titre: {first_emission.title}")
                print(f"  type id: {type(first_emission.id)}")
            
            result.update({
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
            })
            
            print(f"📤 Résultat retourné: {len(result['emissions'])} émissions, total: {result['total']}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur globale dans get_all_emissions: {e}")
            import traceback
            traceback.print_exc()
            # Retourner un résultat vide en cas d'erreur
            return {
                "emissions": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }

    async def get_emission_by_id(self, emission_id: str) -> Dict[str, Any]:
        """
        Récupère une émission spécifique par son ID
        """
        emission = await self._find_emission_by_id(emission_id)

        if not emission or not emission.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Émission non trouvée"
            )

        return EmissionResponse.from_orm(emission)

    async def create_emission(self, emission_data: EmissionCreate) -> Dict[str, Any]:
        """
        Crée une nouvelle émission
        """
        emission = Emission(**emission_data.dict())
        emission.updated_at = datetime.utcnow()
        await emission.insert()  # Utiliser insert() au lieu de save() pour les nouveaux documents

        return EmissionResponse.from_orm(emission)

    async def update_emission(self, emission_id: str, emission_data: EmissionUpdate) -> Dict[str, Any]:
        """
        Met à jour une émission existante
        """
        print(f"🔍 Recherche de l'émission pour mise à jour avec ID: {emission_id}")
        
        emission = await self._find_emission_by_id(emission_id)
        
        if not emission:
            print(f"❌ Émission non trouvée pour mise à jour avec ID: {emission_id}")
            
            # Lister toutes les émissions disponibles pour le debug
            all_emissions = await Emission.find({}).to_list()
            if all_emissions:
                print("📋 Émissions disponibles:")
                for i, e in enumerate(all_emissions[:5]):  # Limiter à 5 pour éviter le spam
                    print(f"  {i+1}. id: {e.id}, titre: {e.title}")
                    print(f"      🆔 ID Beanie: {e.id}, type: {type(e.id)}")
            else:
                print("📭 Aucune émission dans la base de données")
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Émission non trouvée avec l'ID: {emission_id}"
            )

        # Mettre à jour uniquement les champs fournis
        update_data = emission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(emission, field, value)
        
        emission.updated_at = datetime.utcnow()
        await emission.save()

        print(f"✅ Émission mise à jour avec succès: {emission.id}")
        return EmissionResponse.from_orm(emission)

    async def delete_emission(self, emission_id: str) -> bool:
        """
        Supprime (désactive) une émission
        """
        print(f"🔍 Recherche de l'émission avec ID: {emission_id}")
        
        emission = await self._find_emission_by_id(emission_id)
        
        if not emission:
            print(f"❌ Émission non trouvée avec ID: {emission_id}")
            # Lister toutes les émissions disponibles pour le debug
            all_emissions = await Emission.find({}).to_list()
            if all_emissions:
                print("📋 Émissions disponibles:")
                for i, e in enumerate(all_emissions[:5]):
                    print(f"  {i+1}. id: {e.id}, titre: {e.title}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Émission non trouvée avec l'ID: {emission_id}"
            )

        print(f"✅ Émission trouvée, suppression en cours...")
        # Soft delete : désactiver au lieu de supprimer
        emission.is_active = False
        emission.updated_at = datetime.utcnow()
        await emission.save()

        return True

    async def search_emissions(self, search_request: SearchRequest) -> List[Dict[str, Any]]:
        """
        Recherche des émissions par terme de recherche
        """
        # Construire le filtre de base
        filter_dict = {"is_active": True}
        
        # Ajouter la recherche texte
        search_term = search_request.query.lower()
        
        # Filtrer par catégorie si spécifié
        if search_request.category and search_request.category != "toutes":
            filter_dict["category"] = search_request.category

        # Rechercher dans plusieurs champs (MongoDB text search)
        emissions = await Emission.find(filter_dict).to_list()
        
        # Filtrer manuellement les résultats pour la recherche texte
        filtered_emissions = []
        for emission in emissions:
            if (search_term in emission.title.lower() or 
                (emission.description and search_term in emission.description.lower()) or
                (emission.presenter and search_term in emission.presenter.lower()) or
                any(search_term in tag.lower() for tag in emission.tags)):
                filtered_emissions.append(emission)

        # Trier et paginer
        filtered_emissions.sort(key=lambda x: (x.featured, x.date or datetime.min), reverse=True)
        
        start_idx = search_request.offset
        end_idx = start_idx + search_request.limit
        paginated_emissions = filtered_emissions[start_idx:end_idx]

        return [EmissionResponse.from_orm(emission) for emission in paginated_emissions]

    async def get_featured_emissions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les émissions en vedette
        """
        emissions = await Emission.find(
            {"featured": True, "is_active": True}
        ).sort("-date").limit(limit).to_list()

        return [EmissionResponse.from_orm(emission) for emission in emissions]

    async def get_new_emissions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les nouvelles émissions
        """
        emissions = await Emission.find(
            {"is_new": True, "is_active": True}
        ).sort("-created_at").limit(limit).to_list()

        return [EmissionResponse.from_orm(emission) for emission in emissions]

    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Récupère les catégories avec le nombre d'émissions
        """
        # Utiliser l'agrégation MongoDB pour compter par catégorie
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        category_counts = await Emission.aggregate(pipeline).to_list()

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

    async def increment_views(self, emission_id: str, request: Optional[ViewIncrementRequest] = None) -> bool:
        """
        Incrémente le nombre de vues d'une émission
        """
        emission = await self._find_emission_by_id(emission_id)

        if not emission or not emission.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Émission non trouvée"
            )

        emission.views += 1
        emission.updated_at = datetime.utcnow()
        await emission.save()

        return True

    async def toggle_like(self, emission_id: str, request: LikeRequest) -> Dict[str, Any]:
        """
        Ajoute ou retire un like d'une émission
        """
        emission = await self._find_emission_by_id(emission_id)

        if not emission or not emission.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Émission non trouvée"
            )

        # TODO: Gérer les likes par utilisateur dans une collection séparée
        # Pour l'instant, on incrémente/décrémente simplement le compteur
        
        if request.action == "add":
            emission.likes += 1
        elif request.action == "remove" and emission.likes > 0:
            emission.likes -= 1

        emission.updated_at = datetime.utcnow()
        await emission.save()

        return {
            "id": str(emission.id),
            "likes": emission.likes,
            "action": request.action
        }

    async def get_emission_stats(self, emission_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une émission
        """
        emission = await self._find_emission_by_id(emission_id)

        if not emission or not emission.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Émission non trouvée"
            )

        return {
            "id": str(emission.id),
            "views": emission.views,
            "likes": emission.likes,
            "created_at": emission.created_at,
            "updated_at": emission.updated_at
        }