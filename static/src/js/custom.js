odoo.define('gestion_projets_pedagogiques.custom', function (require) {
    "use strict";

    var core = require('web.core');
    var utils = require('web.utils');
    var ListRenderer = require('web.ListRenderer');

    // Extension du rendu de liste pour ajouter des classes CSS basées sur l'état
    ListRenderer.include({
        _renderRow: function (record) {
            var $tr = this._super.apply(this, arguments);
            var state = record.data.state;
            
            if (state) {
                $tr.addClass('state-' + state.replace(/_/g, '-'));
            }
            
            // Ajouter une classe pour les projets en retard
            if (record.model === 'gestion.projet') {
                var date_fin = record.data.date_fin;
                if (date_fin) {
                    var today = new Date();
                    var fin = new Date(date_fin);
                    if (fin < today && record.data.state === 'en_cours') {
                        $tr.addClass('project-late');
                    }
                }
            }
            
            return $tr;
        }
    });

    // Widget pour le dashboard
    var DashboardWidget = core.Class.extend({
        init: function (parent) {
            this.parent = parent;
        },
        
        start: function () {
            var self = this;
            this._updateStats();
            
            // Mettre à jour les stats toutes les 30 secondes
            setInterval(function() {
                self._updateStats();
            }, 30000);
        },
        
        _updateStats: function () {
            var self = this;
            
            // Récupérer les statistiques via RPC
            this._rpc({
                model: 'gestion.etudiant',
                method: 'search_count',
                args: [[]],
            }).then(function (count) {
                $('.etudiant-count').text(count || 0);
            });
            
            this._rpc({
                model: 'gestion.projet',
                method: 'search_count',
                args: [[]],
            }).then(function (count) {
                $('.projet-count').text(count || 0);
            });
            
            this._rpc({
                model: 'gestion.enseignant',
                method: 'search_count',
                args: [[]],
            }).then(function (count) {
                $('.enseignant-count').text(count || 0);
            });
            
            this._rpc({
                model: 'gestion.soutenance',
                method: 'search_count',
                args: [[['state', '=', 'planifiee']]],
            }).then(function (count) {
                $('.soutenance-count').text(count || 0);
            });
        },
        
        _rpc: function (params) {
            return this.parent.call('ajax', 'jsonrpc', params);
        }
    });

    return {
        DashboardWidget: DashboardWidget
    };
});