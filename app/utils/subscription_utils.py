"""
Utilitaires pour la gestion des catégories d'abonnement
"""
from typing import Optional

# Hiérarchie des catégories (du plus bas au plus haut)
SUBSCRIPTION_HIERARCHY = {
    None: 0,         # Gratuit
    'basic': 1,      # Basic
    'standard': 2,   # Standard
    'premium': 3     # Premium
}

def can_access_content(user_category: Optional[str], required_category: Optional[str]) -> bool:
    """
    Vérifie si un utilisateur avec une certaine catégorie d'abonnement
    peut accéder à un contenu qui requiert une catégorie spécifique.
    
    Hiérarchie:
    - Premium peut accéder à tout (basic, standard, premium, gratuit)
    - Standard peut accéder à basic, standard, et gratuit
    - Basic peut accéder à basic et gratuit
    - Gratuit (None) ne peut accéder qu'au contenu gratuit (None)
    
    Args:
        user_category: Catégorie d'abonnement de l'utilisateur (None, 'basic', 'standard', 'premium')
        required_category: Catégorie requise pour le contenu (None, 'basic', 'standard', 'premium')
    
    Returns:
        True si l'utilisateur peut accéder au contenu, False sinon
    """
    # Si le contenu est gratuit (None), tout le monde peut y accéder
    if required_category is None:
        return True
    
    # Si l'utilisateur n'a pas d'abonnement, il ne peut accéder qu'au contenu gratuit
    if user_category is None:
        return False
    
    # Comparer les niveaux de hiérarchie
    user_level = SUBSCRIPTION_HIERARCHY.get(user_category, 0)
    required_level = SUBSCRIPTION_HIERARCHY.get(required_category, 0)
    
    # L'utilisateur peut accéder au contenu si son niveau est >= au niveau requis
    return user_level >= required_level


def get_highest_active_category(categories: list[Optional[str]]) -> Optional[str]:
    """
    Retourne la catégorie la plus élevée parmi une liste de catégories.
    Utile quand un utilisateur a plusieurs abonnements actifs.
    
    Args:
        categories: Liste de catégories d'abonnement
    
    Returns:
        La catégorie la plus élevée (premium > standard > basic > None)
    """
    if not categories:
        return None
    
    # Filtrer les valeurs None et trier par niveau de hiérarchie
    valid_categories = [cat for cat in categories if cat is not None]
    
    if not valid_categories:
        return None
    
    # Retourner la catégorie avec le niveau le plus élevé
    return max(valid_categories, key=lambda cat: SUBSCRIPTION_HIERARCHY.get(cat, 0))


def get_category_display_name(category: Optional[str]) -> str:
    """
    Retourne le nom d'affichage pour une catégorie.
    
    Args:
        category: Catégorie d'abonnement
    
    Returns:
        Nom d'affichage de la catégorie
    """
    names = {
        None: 'Gratuit',
        'basic': 'Basic',
        'standard': 'Standard',
        'premium': 'Premium'
    }
    return names.get(category, 'Inconnu')


def is_upgrade(from_category: Optional[str], to_category: Optional[str]) -> bool:
    """
    Vérifie si le passage d'une catégorie à une autre est une amélioration.
    
    Args:
        from_category: Catégorie actuelle
        to_category: Nouvelle catégorie
    
    Returns:
        True si c'est une amélioration, False sinon
    """
    from_level = SUBSCRIPTION_HIERARCHY.get(from_category, 0)
    to_level = SUBSCRIPTION_HIERARCHY.get(to_category, 0)
    return to_level > from_level
