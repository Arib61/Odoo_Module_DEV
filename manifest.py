{
    "name": "Gestion des Projets Pédagogiques",
    "version": "17.0.1.0.0",
    "category": "Education",
    "summary": "Système complet de gestion des projets étudiants",
    "description": """
        Module complet de gestion des projets pédagogiques pour établissements d'enseignement supérieur.
        Gestion des étudiants, enseignants, projets, tâches, soutenances et évaluations.
    """,
    "author": "ARIB Aymane",
    "website": "",
    "depends": ["base", "mail", "calendar", "contacts"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "data/data_demo.xml",
        "views/etudiant_views.xml",
        "views/enseignant_views.xml",
        "views/projet_views.xml",
        "views/tache_views.xml",
        "views/soutenance_views.xml",
        "views/evaluation_views.xml",
        "views/menu_views.xml",
        "views/action_views.xml",
        "reports/project_report.xml",
    ],
    "demo": ["data/data_demo.xml"],
    "assets": {
        "web.assets_backend": [
            "gestion_projets_pedagogiques/static/src/css/custom.css",
            "gestion_projets_pedagogiques/static/src/js/custom.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}