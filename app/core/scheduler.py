"""
Gestionnaire de tâches planifiées (CRON).
Désactive automatiquement les abonnements expirés en fonction de leur durée.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio


scheduler = AsyncIOScheduler()


async def deactivate_expired_subscriptions_job():
    """
    Tâche planifiée : désactive tous les abonnements expirés.
    Vérifie chaque abonnement et compare end_date avec la date actuelle.
    La end_date est calculée automatiquement lors de la création de l'abonnement
    en fonction du plan choisi (1 mois, 3 mois, 1 an, etc.).
    """
    try:
        from app.services.subscription_service import deactivate_expired_subscriptions
        
        print(f"\n⏰ [CRON {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Vérification des abonnements expirés...")
        
        count = await deactivate_expired_subscriptions()
        
        if count > 0:
            print(f"✅ {count} abonnement(s) expiré(s) désactivé(s)")
        else:
            print(f"✅ Aucun abonnement expiré trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de la désactivation des abonnements expirés: {e}")


async def sync_user_categories_job():
    """
    Tâche planifiée : synchronise les catégories d'abonnement des utilisateurs.
    Met à jour subscription_category et is_premium pour tous les utilisateurs
    ayant des abonnements actifs mais des données incohérentes.
    """
    try:
        from app.models.user import User
        from app.services.subscription_service import sync_user_premium_status
        
        print(f"\n🔄 [CRON {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Synchronisation des catégories d'abonnement...")
        
        # Récupérer tous les utilisateurs
        users = await User.find().to_list()
        updated_count = 0
        
        for user in users:
            try:
                # Synchroniser chaque utilisateur
                old_category = user.subscription_category
                old_premium = user.is_premium
                
                await sync_user_premium_status(str(user.id))
                
                # Recharger l'utilisateur pour voir les changements
                updated_user = await User.get(user.id)
                
                if (updated_user.subscription_category != old_category or 
                    updated_user.is_premium != old_premium):
                    print(f"✅ Utilisateur {user.email}: {old_category} -> {updated_user.subscription_category}, premium: {old_premium} -> {updated_user.is_premium}")
                    updated_count += 1
                    
            except Exception as user_error:
                print(f"❌ Erreur sync utilisateur {user.email}: {user_error}")
        
        if updated_count > 0:
            print(f"✅ {updated_count} utilisateur(s) synchronisé(s)")
        else:
            print(f"✅ Aucune synchronisation nécessaire")
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des catégories: {e}")


async def send_program_reminders_job():
    """
    Tache planifiee : envoie les rappels de programmes dus dans la prochaine minute.
    Utilise une mise a jour atomique pour eviter les doublons entre workers gunicorn.
    """
    # Eviter l'execution sur plusieurs workers : seul le worker principal (pid le plus bas) execute
    import os
    worker_pid = os.getpid()

    try:
        from app.models.program import ProgramReminder
        from app.models.user import User
        from app.services.push_notification_service import push_notification_service
        import firebase_admin
        from firebase_admin import messaging as fcm_messaging
        from datetime import timedelta
        from beanie.operators import Set as BSet

        now = datetime.utcnow()
        window_end = now + timedelta(minutes=1)

        # Recuperer les IDs eligibles
        candidates = await ProgramReminder.find({
            "status": "scheduled",
            "scheduled_for": {"$gte": now, "$lte": window_end}
        }).to_list()

        if not candidates:
            return

        # Marquer atomiquement chaque rappel via findOneAndUpdate
        # Seul le worker qui reussit le update (status: scheduled -> sending) traite le rappel
        from motor.motor_asyncio import AsyncIOMotorClient
        collection = ProgramReminder.get_motor_collection()

        reminders = []
        for candidate in candidates:
            result = await collection.find_one_and_update(
                {"_id": candidate.id, "status": "scheduled"},
                {"$set": {"status": "sending"}},
                return_document=True
            )
            if result:
                reminders.append(await ProgramReminder.get(candidate.id))

        if not reminders:
            return  # Un autre worker a deja tout pris

            print(f"[CRON][pid:{worker_pid}] Envoi rappel pour '{updated.program_title}'")

            try:
                user = await User.get(updated.user_id)
                title = f"Rappel : {updated.program_title or 'Programme'}"
                body  = f"Commence dans {updated.minutes_before} min sur {updated.channel_name or 'BF1 TV'}"

                fcm_sent = False

                # Envoi FCM si l'utilisateur a des tokens
                if user and getattr(user, 'fcm_tokens', None) and firebase_admin._apps:
                    tokens = [t for t in user.fcm_tokens if t]
                    if tokens:
                        msg = fcm_messaging.MulticastMessage(
                            notification=fcm_messaging.Notification(title=title, body=body),
                            data={
                                "type":       "program_reminder",
                                "program_id": str(updated.program_id),
                                "title":      updated.program_title or '',
                            },
                            tokens=tokens,
                            webpush=fcm_messaging.WebpushConfig(
                                notification=fcm_messaging.WebpushNotification(icon='/logo.png')
                            ),
                        )
                        response = fcm_messaging.send_each_for_multicast(msg)
                        fcm_sent = response.success_count > 0
                        print(f"[CRON] FCM: {response.success_count}/{len(tokens)} tokens OK")
                else:
                    print(f"[CRON] Pas de token FCM pour user {updated.user_id} — WebSocket seulement")

                # Envoi WebSocket (onglet ouvert)
                await push_notification_service._broadcast_notification({
                    "title": title,
                    "body":  body,
                    "data":  {
                        "type":       "program_reminder",
                        "program_id": str(updated.program_id),
                        "title":      updated.program_title or '',
                    }
                })

                updated.status = "sent"
                updated.sent_at = now
                await updated.save()
                print(f"[OK] Rappel envoye (FCM:{fcm_sent}) pour '{updated.program_title}'")

            except Exception as e:
                updated.status = "failed"
                await updated.save()
                print(f"[ERREUR] Rappel {updated.id}: {e}")

    except Exception as e:
        print(f"[ERREUR] Job rappels programmes: {e}")


def start_scheduler():
    """
    Démarre le scheduler avec toutes les tâches planifiées.
    
    Tâches configurées:
    - Désactivation des abonnements expirés : toutes les heures
    - Synchronisation des catégories : toutes les 6 heures
    
    Pour tester en dev : changer la fréquence à 'interval' avec minutes=1
    """
    # PRODUCTION : Toutes les heures
    scheduler.add_job(
        deactivate_expired_subscriptions_job,
        CronTrigger(hour='*', minute=0),  # Toutes les heures à la minute 0
        id='deactivate_expired_subscriptions',
        name='Désactiver les abonnements expirés',
        replace_existing=True
    )
    
    # Synchronisation des catégories : toutes les 6 heures
    scheduler.add_job(
        sync_user_categories_job,
        CronTrigger(hour='*/6', minute=30),  # Toutes les 6 heures à la minute 30
        id='sync_user_categories',
        name='Synchroniser les catégories d\'abonnement',
        replace_existing=True
    )
    
    # DÉVELOPPEMENT : Décommenter pour tester toutes les minutes
    # scheduler.add_job(
    #     deactivate_expired_subscriptions_job,
    #     'interval',
    #     minutes=1,  # Exécute toutes les 1 minute pour tester
    #     id='deactivate_expired_subscriptions_dev',
    #     name='Désactiver les abonnements expirés (DEV)',
    #     replace_existing=True
    # )
    
    # Optionnel : Exécuter immédiatement au démarrage
    scheduler.add_job(
        deactivate_expired_subscriptions_job,
        'date',
        run_date=datetime.now(),
        id='deactivate_expired_subscriptions_startup',
        name='Désactivation des abonnements expirés (démarrage)'
    )
    
    # Synchronisation immédiate au démarrage
    scheduler.add_job(
        sync_user_categories_job,
        'date',
        run_date=datetime.now(),
        id='sync_user_categories_startup',
        name='Synchronisation des catégories (démarrage)'
    )
    
    # Rappels de programmes : toutes les minutes
    scheduler.add_job(
        send_program_reminders_job,
        'interval',
        minutes=1,
        id='send_program_reminders',
        name='Envoyer les rappels de programmes',
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler démarré - Tâches planifiées:")
    print("   📅 Désactivation abonnements expirés: Toutes les heures")
    print("   🔄 Synchronisation catégories: Toutes les 6 heures")
    print("   🔔 Rappels de programmes: Toutes les minutes")
    print("   🚀 Première exécution: Immédiatement au démarrage")


def stop_scheduler():
    """Arrête le scheduler proprement."""
    if scheduler.running:
        scheduler.shutdown()
        print("✅ Scheduler arrêté")
