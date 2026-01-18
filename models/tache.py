from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta

class Tache(models.Model):
    _name = 'gestion.tache'
    _description = 'Tâche du Projet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut, priorite desc'
    
    name = fields.Char(string='Titre', required=True, tracking=True)
    description = fields.Text(string='Description')
    
    projet_id = fields.Many2one('gestion.projet', string='Projet', required=True, tracking=True)
    etudiant_id = fields.Many2one('gestion.etudiant', string='Étudiant Responsable', required=True)
    
    date_debut = fields.Date(string='Date de Début', required=True, default=fields.Date.today)
    date_fin = fields.Date(string='Date de Fin', required=True)
    date_limite = fields.Date(string='Date Limite')
    
    priorite = fields.Selection([
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ], string='Priorité', default='moyenne')
    
    state = fields.Selection([
        ('a_faire', 'À Faire'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('retard', 'En Retard'),
        ('annule', 'Annulé'),
    ], string='État', default='a_faire', tracking=True)
    
    avancement = fields.Integer(string='Avancement (%)', default=0)
    difficulte = fields.Selection([
        ('facile', 'Facile'),
        ('moyen', 'Moyen'),
        ('difficile', 'Difficile'),
    ], string='Difficulté', default='moyen')
    
    # Calculs
    @api.onchange('date_debut', 'date_fin')
    def _onchange_dates(self):
        if self.date_debut and self.date_fin:
            if self.date_fin < self.date_debut:
                return {
                    'warning': {
                        'title': _('Dates incorrectes'),
                        'message': _('La date de fin doit être postérieure à la date de début.')
                    }
                }
    
    # Contraintes
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for tache in self:
            if tache.date_debut and tache.date_fin:
                if tache.date_fin < tache.date_debut:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début"))
    
    @api.constrains('avancement')
    def _check_avancement(self):
        for tache in self:
            if tache.avancement < 0 or tache.avancement > 100:
                raise ValidationError(_("L'avancement doit être compris entre 0 et 100"))
    
    # Actions
    def action_demarrer(self):
        for tache in self:
            tache.write({'state': 'en_cours'})
    
    def action_terminer(self):
        for tache in self:
            tache.write({'state': 'termine', 'avancement': 100})
    
    def action_retard(self):
        for tache in self:
            tache.write({'state': 'retard'})
    
    def action_annuler(self):
        for tache in self:
            tache.write({'state': 'annule'})
    
    # Méthode cron pour vérifier les tâches en retard
    def _cron_verifier_taches_retard(self):
        aujourdhui = fields.Date.today()
        taches_retard = self.search([
            ('state', 'in', ['a_faire', 'en_cours']),
            ('date_fin', '<', aujourdhui)
        ])
        for tache in taches_retard:
            tache.write({'state': 'retard'})
            tache.message_post(
                body=_('⚠️ Cette tâche est en retard ! Date de fin dépassée.'),
                subject=_('Tâche en retard')
            )