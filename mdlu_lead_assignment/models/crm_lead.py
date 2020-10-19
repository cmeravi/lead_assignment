# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def next_assigned_user(self, user_id):
        team = self.team_id
        user_id = user_id if (user_id and user_id in team.get_available_team_members()) else team.get_available_team_members()[0]
        assign_method = team.lead_assignment
        if 'crm_team_next' == assign_method:
            user_id = team.find_next_team_member()
        elif 'lowest_leads' == assign_method:
            user_id = team.lowest_leads_member()
        elif 'random_assignment' == assign_method:
            user_id = team.next_random_team_member(team.get_available_team_members())
        return user_id

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        context = dict(self._context or {})
        file_import = 'import_file' in context and context['import_file']
        user = self.env['res.users'].search([('id','=',context['uid'])]) if 'uid' in context else False
        if 'team_id' in vals and res.team_id.id != vals['team_id']:
            res.team_id = self.env['crm.team'].search([('id','=',vals['team_id'])])
        elif 'team_id' not in vals and not file_import:
            res.team_id = user.sale_team_id
        available_team_members = res.team_id.get_available_team_members()
        team_user = user and available_team_members and user in available_team_members
        if not team_user or file_import:
            res.user_id = res.next_assigned_user(user)
        return res
