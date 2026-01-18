from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class Soutenance(models.Model):
    _name = 'gestion.soutenance'
    _description = 'Soutenance de Projet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Référence', required=True, default=lambda self: _('Nouvelle Soutenance'))
    projet_id = fields.Many2one('gestion.projet', string='Projet', required=True)
    
    date_soutenance = fields.Datetime(string='Date et Heure', required=True, default=fields.Datetime.now)
    duree = fields.Integer(string='Durée (minutes)', default=30)
    salle = fields.Char(string='Salle', required=True)
    
    jury_ids = fields.Many2many('gestion.enseignant', 'soutenance_jury_rel', 
                               'soutenance_id', 'enseignant_id', string='Membres du Jury')
    president_jury = fields.Many2one('gestion.enseignant', string='Président du Jury')
    
    # Notes
    note_rapport = fields.Float(string='Note Rapport', digits=(4,2))
    note_presentation = fields.Float(string='Note Présentation', digits=(4,2))
    note_technique = fields.Float(string='Note Technique', digits=(4,2))
    note_finale = fields.Float(string='Note Finale', digits=(4,2), compute='_compute_note_finale', store=True)
    
    observations = fields.Text(string='Observations du Jury')
    decision = fields.Selection([
        ('admis', 'Admis'),
        ('admis_avec_mention', 'Admis avec Mention'),
        ('redouble', 'Redouble'),
        ('ajourne', 'Ajourné'),
    ], string='Décision')
    
    state = fields.Selection([
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En Cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ], string='État', default='planifiee', tracking=True)
    
    rapport_soutenance = fields.Binary(string='Rapport de Soutenance')
    rapport_nom = fields.Char(string='Nom du Rapport')
    
    # Calculs
    @api.depends('note_rapport', 'note_presentation', 'note_technique')
    def _compute_note_finale(self):
        for soutenance in self:
            coefficients = {'note_rapport': 0.4, 'note_presentation': 0.3, 'note_technique': 0.3}
            notes_valides = []
            total_coeff = 0
            
            if soutenance.note_rapport:
                notes_valides.append(soutenance.note_rapport * coefficients['note_rapport'])
                total_coeff += coefficients['note_rapport']
            if soutenance.note_presentation:
                notes_valides.append(soutenance.note_presentation * coefficients['note_presentation'])
                total_coeff += coefficients['note_presentation']
            if soutenance.note_technique:
                notes_valides.append(soutenance.note_technique * coefficients['note_technique'])
                total_coeff += coefficients['note_technique']
            
            if notes_valides and total_coeff > 0:
                soutenance.note_finale = sum(notes_valides) / total_coeff
            else:
                soutenance.note_finale = 0
    
    # Séquence pour référence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle Soutenance')) == _('Nouvelle Soutenance'):
                seq = self.env['ir.sequence'].next_by_code('gestion.soutenance') or '/'
                vals['name'] = seq
        return super(Soutenance, self).create(vals_list)
    
    # Contraintes
    @api.constrains('date_soutenance')
    def _check_date_soutenance(self):
        for soutenance in self:
            if soutenance.date_soutenance:
                if soutenance.date_soutenance < fields.Datetime.now():
                    raise ValidationError(_("La date de soutenance doit être future"))
    
    @api.constrains('duree')
    def _check_duree(self):
        for soutenance in self:
            if soutenance.duree <= 0:
                raise ValidationError(_("La durée doit être positive"))
    
    # Actions
    def action_demarrer(self):
        for soutenance in self:
            if soutenance.state != 'planifiee':
                raise ValidationError(_("Seules les soutenances planifiées peuvent être démarrées"))
            soutenance.write({'state': 'en_cours'})
    
    def action_terminer(self):
        for soutenance in self:
            if soutenance.state != 'en_cours':
                raise ValidationError(_("Seules les soutenances en cours peuvent être terminées"))
            soutenance.write({'state': 'terminee'})
            
            # Mettre à jour le projet
            if soutenance.projet_id and soutenance.decision == 'admis':
                soutenance.projet_id.write({
                    'state': 'valide',
                    'note': soutenance.note_finale,
                    'date_soutenance': soutenance.date_soutenance.date()
                })
    
    def action_annuler(self):
        for soutenance in self:
            if soutenance.state in ['terminee', 'annulee']:
                raise ValidationError(_("Cette soutenance ne peut plus être annulée"))
            soutenance.write({'state': 'annulee'})