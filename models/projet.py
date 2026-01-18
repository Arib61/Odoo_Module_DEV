from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta

class Projet(models.Model):
    _name = 'gestion.projet'
    _description = 'Projet Pédagogique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'
    
    # Identification
    name = fields.Char(string='Titre du Projet', required=True, tracking=True)
    code = fields.Char(string='Code Projet', size=20, required=True, index=True, default='Nouveau')
    description = fields.Html(string='Description')
    
    # Dates
    date_debut = fields.Date(string='Date de Début', required=True, default=fields.Date.today, tracking=True)
    date_fin = fields.Date(string='Date de Fin', required=True, tracking=True)
    date_soutenance = fields.Date(string='Date de Soutenance Prévue')
    duree = fields.Integer(string='Durée (jours)', compute='_compute_duree', store=True)
    
    # Participants
    etudiant_id = fields.Many2one('gestion.etudiant', string='Étudiant Principal', required=True, tracking=True)
    etudiant_ids = fields.Many2many('gestion.etudiant', 'projet_etudiant_rel', 
                                   string='Étudiants (groupe)')
    enseignant_id = fields.Many2one('gestion.enseignant', string='Encadrant', required=True, tracking=True)
    jury_ids = fields.Many2many('gestion.enseignant', 'projet_jury_rel', string='Membres du Jury')
    
    # Caractéristiques
    type_projet = fields.Selection([
        ('pfe', 'Projet de Fin d\'Études'),
        ('memoire', 'Mémoire'),
        ('stage', 'Rapport de Stage'),
        ('recherche', 'Projet de Recherche'),
        ('technique', 'Projet Technique'),
    ], string='Type de Projet', required=True, default='pfe', tracking=True)
    
    domaine = fields.Selection([
        ('informatique', 'Informatique'),
        ('genie_civil', 'Génie Civil'),
        ('genie_mecanique', 'Génie Mécanique'),
        ('genie_electrique', 'Génie Électrique'),
        ('commerce', 'Commerce'),
        ('gestion', 'Gestion'),
        ('autres', 'Autres'),
    ], string='Domaine', required=True, default='informatique')
    
    mots_cles = fields.Char(string='Mots-clés')
    
    # État et évaluation
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('en_cours', 'En Cours'),
        ('soutenu', 'Soutenu'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('archive', 'Archivé'),
    ], string='État', default='brouillon', tracking=True)
    
    note = fields.Float(string='Note Finale', digits=(4,2), tracking=True)
    mention = fields.Selection([
        ('excellent', 'Excellent'),
        ('tres_bien', 'Très Bien'),
        ('bien', 'Bien'),
        ('assez_bien', 'Assez Bien'),
        ('passable', 'Passable'),
        ('ajourne', 'Ajourné'),
    ], string='Mention', tracking=True)
    
    avancement = fields.Float(string='Avancement (%)', compute='_compute_avancement', store=True)
    
    # Documents
    document_principal = fields.Binary(string='Document Principal')
    document_name = fields.Char(string='Nom du Document')
    
    # Relations
    tache_ids = fields.One2many('gestion.tache', 'projet_id', string='Tâches')
    tache_count = fields.Integer(string='Nombre de Tâches', compute='_compute_tache_count')
    soutenance_ids = fields.One2many('gestion.soutenance', 'projet_id', string='Soutenances')
    
    # Calculs
    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for projet in self:
            if projet.date_debut and projet.date_fin:
                delta = projet.date_fin - projet.date_debut
                projet.duree = delta.days + 1
            else:
                projet.duree = 0
    
    @api.depends('tache_ids', 'tache_ids.avancement')
    def _compute_avancement(self):
        for projet in self:
            if projet.tache_ids:
                total_avancement = sum(tache.avancement for tache in projet.tache_ids)
                projet.avancement = total_avancement / len(projet.tache_ids)
            else:
                projet.avancement = 0
    
    def _compute_tache_count(self):
        for projet in self:
            projet.tache_count = len(projet.tache_ids)
    
    # Séquence pour code projet
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'Nouveau') == 'Nouveau':
                seq = self.env['ir.sequence'].next_by_code('gestion.projet') or '/'
                vals['code'] = seq
        return super(Projet, self).create(vals_list)
    
    # Contraintes
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for projet in self:
            if projet.date_debut and projet.date_fin:
                if projet.date_fin < projet.date_debut:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début"))
    
    @api.constrains('note')
    def _check_note(self):
        for projet in self:
            if projet.note and (projet.note < 0 or projet.note > 20):
                raise ValidationError(_("La note doit être comprise entre 0 et 20"))
    
    # Actions
    def action_demarrer_projet(self):
        self.ensure_one()
        if self.state != 'brouillon':
            raise UserError(_("Seuls les projets en brouillon peuvent être démarrés"))
        self.write({'state': 'en_cours'})
        
        # Créer une activité de suivi
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=date.today() + timedelta(days=7),
            summary=_('Suivi hebdomadaire du projet'),
            note=_('Veuillez fournir un point d\'avancement sur le projet.')
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Projet démarré'),
                'message': _('Le projet a été démarré avec succès.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_soutenir(self):
        self.ensure_one()
        if self.state != 'en_cours':
            raise UserError(_("Seuls les projets en cours peuvent être marqués comme soutenus"))
        self.write({'state': 'soutenu'})
    
    def action_valider(self):
        self.ensure_one()
        if self.state != 'soutenu':
            raise UserError(_("Seuls les projets soutenus peuvent être validés"))
        if not self.note:
            raise UserError(_("Veuillez saisir la note avant de valider le projet"))
        self.write({'state': 'valide'})
    
    def action_refuser(self):
        self.ensure_one()
        if self.state != 'soutenu':
            raise UserError(_("Seuls les projets soutenus peuvent être refusés"))
        self.write({'state': 'refuse'})
    
    def action_archiver(self):
        self.write({'state': 'archive'})
    
    def action_view_taches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tâches du projet {self.name}',
            'res_model': 'gestion.tache',
            'view_mode': 'tree,form',
            'domain': [('projet_id', '=', self.id)],
            'context': {'default_projet_id': self.id, 'default_etudiant_id': self.etudiant_id.id},
        }
    
    def action_view_soutenance(self):
        self.ensure_one()
        if self.soutenance_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gestion.soutenance',
                'res_id': self.soutenance_ids[0].id,
                'view_mode': 'form',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Créer une soutenance'),
                'res_model': 'gestion.soutenance',
                'view_mode': 'form',
                'context': {'default_projet_id': self.id},
            }