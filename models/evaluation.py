from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Evaluation(models.Model):
    _name = 'gestion.evaluation'
    _description = 'Évaluation'
    _rec_name = 'name'
    
    name = fields.Char(string='Référence', readonly=True, default=lambda self: _('Nouvelle'))
    projet_id = fields.Many2one('gestion.projet', string='Projet', required=True)
    etudiant_id = fields.Many2one('gestion.etudiant', string='Étudiant', required=True)
    enseignant_id = fields.Many2one('gestion.enseignant', string='Évaluateur', required=True)
    
    date_evaluation = fields.Date(string='Date d\'Évaluation', default=fields.Date.today)
    critere = fields.Selection([
        ('qualite_travail', 'Qualité du Travail'),
        ('respect_delais', 'Respect des Délais'),
        ('presentation', 'Présentation'),
        ('innovation', 'Innovation'),
        ('analyse', 'Analyse et Synthèse'),
        ('rapport', 'Rapport Écrit'),
    ], string='Critère d\'Évaluation', required=True)
    
    note = fields.Float(string='Note', digits=(3,2), required=True)
    commentaire = fields.Text(string='Commentaire')
    
    # Séquence pour référence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle')) == _('Nouvelle'):
                seq = self.env['ir.sequence'].next_by_code('gestion.evaluation') or '/'
                vals['name'] = seq
        return super(Evaluation, self).create(vals_list)
    
    # Contraintes
    @api.constrains('note')
    def _check_note(self):
        for evaluation in self:
            if evaluation.note < 0 or evaluation.note > 20:
                raise ValidationError(_("La note doit être comprise entre 0 et 20"))