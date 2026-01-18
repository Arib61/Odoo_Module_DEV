from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Etudiant(models.Model):
    _name = 'gestion.etudiant'
    _description = 'Étudiant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    
    # Informations personnelles
    name = fields.Char(string='Nom', required=True, tracking=True)
    prenom = fields.Char(string='Prénom', required=True, tracking=True)
    display_name = fields.Char(string='Nom Complet', compute='_compute_display_name', store=True)
    image_1920 = fields.Image(string='Photo', max_width=1920, max_height=1920)
    cin = fields.Char(string='CIN', size=10, tracking=True)
    cne = fields.Char(string='CNE', required=True, tracking=True, index=True)
    date_naissance = fields.Date(string='Date de Naissance', tracking=True)
    lieu_naissance = fields.Char(string='Lieu de Naissance')
    
    # Informations académiques
    filiere = fields.Selection([
        ('informatique', 'Informatique'),
        ('genie_civil', 'Génie Civil'),
        ('genie_mecanique', 'Génie Mécanique'),
        ('genie_electrique', 'Génie Électrique'),
        ('commerce', 'Commerce'),
        ('gestion', 'Gestion'),
    ], string='Filière', required=True, tracking=True)
    
    niveau = fields.Selection([
        ('licence1', 'Licence 1'),
        ('licence2', 'Licence 2'),
        ('licence3', 'Licence 3'),
        ('master1', 'Master 1'),
        ('master2', 'Master 2'),
        ('doctorat', 'Doctorat'),
    ], string='Niveau', required=True, tracking=True)
    
    annee_academique = fields.Char(string='Année Académique', default='2024-2025')
    moyenne_generale = fields.Float(string='Moyenne Générale', digits=(5,2))
    credit_acquis = fields.Integer(string='Crédits Acquis')
    
    # Coordonnées
    email = fields.Char(string='Email', required=True, tracking=True)
    telephone = fields.Char(string='Téléphone')
    adresse = fields.Text(string='Adresse')
    
    # Relations
    projet_ids = fields.One2many('gestion.projet', 'etudiant_id', string='Projets')
    projet_count = fields.Integer(string='Nombre de Projets', compute='_compute_projet_count')
    tache_ids = fields.One2many('gestion.tache', 'etudiant_id', string='Tâches')
    tache_count = fields.Integer(string='Nombre de Tâches', compute='_compute_tache_count')
    
    # État
    state = fields.Selection([
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('diplome', 'Diplômé'),
        ('abandon', 'Abandon'),
    ], string='État', default='actif', tracking=True)
    
    # Calculs
    @api.depends('name', 'prenom')
    def _compute_display_name(self):
        for etudiant in self:
            etudiant.display_name = f"{etudiant.prenom} {etudiant.name}"
    
    def _compute_projet_count(self):
        for etudiant in self:
            etudiant.projet_count = len(etudiant.projet_ids)
    
    def _compute_tache_count(self):
        for etudiant in self:
            etudiant.tache_count = len(etudiant.tache_ids)
    
    # Contraintes
    @api.constrains('email')
    def _check_email(self):
        for etudiant in self:
            if etudiant.email and '@' not in etudiant.email:
                raise ValidationError(_("L'email doit être valide"))
    
    @api.constrains('cne')
    def _check_cne(self):
        for etudiant in self:
            if etudiant.cne and len(etudiant.cne) != 10:
                raise ValidationError(_("Le CNE doit contenir 10 caractères"))
    
    # Actions
    def action_view_projets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projets de {self.display_name}',
            'res_model': 'gestion.projet',
            'view_mode': 'tree,form',
            'domain': [('etudiant_id', '=', self.id)],
            'context': {'default_etudiant_id': self.id},
        }
    
    def action_view_taches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tâches de {self.display_name}',
            'res_model': 'gestion.tache',
            'view_mode': 'tree,form',
            'domain': [('etudiant_id', '=', self.id)],
            'context': {'default_etudiant_id': self.id},
        }