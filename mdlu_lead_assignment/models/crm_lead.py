# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def next_assigned_user(self):
        user_id = self.env.user
        team = self.team_id
        assign_method = team.lead_assignment
        if 'user' == assign_method:
            return user_id
        elif 'crm_team_next' == assign_method:
            user_id = team.sudo().find_next_team_member()
        elif 'lowest_leads' == assign_method:
            user_id = team.sudo().lowest_leads_member()
        elif 'random_assignment' == assign_method:
            user_id = team.sudo().next_random_team_member(team.member_ids)
        return user_id


    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        override_user = res.team_id.override_user
        res.user_id = self.env.user
        if res.user_id.id == 1:
            if not override_user:
                res.user_id = res.sudo().next_assigned_user()
            elif override_user:
                res.user_id = res.sudo().next_assigned_user()
        return res
