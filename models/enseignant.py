from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Enseignant(models.Model):
    _name = 'gestion.enseignant'
    _description = 'Enseignant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    
    # Informations personnelles
    name = fields.Char(string='Nom', required=True, tracking=True)
    prenom = fields.Char(string='Prénom', required=True, tracking=True)
    display_name = fields.Char(string='Nom Complet', compute='_compute_display_name', store=True)
    image_1920 = fields.Image(string='Photo', max_width=1920, max_height=1920)
    cin = fields.Char(string='CIN', size=10, tracking=True)
    date_naissance = fields.Date(string='Date de Naissance')
    lieu_naissance = fields.Char(string='Lieu de Naissance')
    
    # Informations professionnelles
    grade = fields.Selection([
        ('professeur', 'Professeur'),
        ('maitre_conference', 'Maître de Conférences'),
        ('charge_cours', 'Chargé de Cours'),
        ('vacataire', 'Enseignant Vacataire'),
        ('assistant', 'Assistant'),
    ], string='Grade', required=True, tracking=True)
    
    specialite = fields.Char(string='Spécialité', required=True)
    departement = fields.Char(string='Département')
    bureau = fields.Char(string='Bureau')
    date_embauche = fields.Date(string="Date d'Embauche")
    salaire = fields.Float(string='Salaire', digits=(10,2))
    
    # Coordonnées
    email = fields.Char(string='Email', required=True, tracking=True)
    telephone = fields.Char(string='Téléphone')
    adresse = fields.Text(string='Adresse')
    
    # Relations
    projet_ids = fields.One2many('gestion.projet', 'enseignant_id', string='Projets Supervisés')
    projet_count = fields.Integer(string='Nombre de Projets', compute='_compute_projet_count', store=True)
    soutenance_ids = fields.Many2many('gestion.soutenance', 'soutenance_jury_rel', 
                                      'enseignant_id', 'soutenance_id', string='Soutenances')
    
    # État
    state = fields.Selection([
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('retraite', 'Retraité'),
    ], string='État', default='actif', tracking=True)
    
    # Calculs
    @api.depends('name', 'prenom')
    def _compute_display_name(self):
        for enseignant in self:
            enseignant.display_name = f"{enseignant.prenom} {enseignant.name}"
    
    @api.depends('projet_ids')
    def _compute_projet_count(self):
        for enseignant in self:
            enseignant.projet_count = len(enseignant.projet_ids)
    
    # Contraintes
    @api.constrains('email')
    def _check_email(self):
        for enseignant in self:
            if enseignant.email and '@' not in enseignant.email:
                raise ValidationError(_("L'email doit être valide"))
    
    @api.constrains('cin')
    def _check_cin(self):
        for enseignant in self:
            if enseignant.cin and len(enseignant.cin) != 10:
                raise ValidationError(_("Le CIN doit contenir 10 caractères"))
    
    # Actions
    def action_view_projets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projets de {self.display_name}',
            'res_model': 'gestion.projet',
            'view_mode': 'tree,form',
            'domain': [('enseignant_id', '=', self.id)],
            'context': {'default_enseignant_id': self.id},
        }