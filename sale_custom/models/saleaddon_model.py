from odoo import api,fields,models
import inflect,random

class sale_addon(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    payment_methods = fields.Selection([('bank','Bank'),
                                      ('cash','Cash'),
                                      ('mpesa','Mpesa')])

    currency_number = fields.Many2one(related="currency_id", string="Currency")

    total = fields.Monetary(related="amount_total", string="Amount total", currency_field="currency_number")

    @api.depends('amount_total')
    def _calc_amount_words(self):
        p = inflect.engine()
        number = self.amount_total
        result = p.number_to_words(number)
        self.amount_words = result.upper()

    amount_words = fields.Text(string="Amount in Words", compute=_calc_amount_words, store=True)



class product_addon(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    desc = fields.Text(size=100, string="Description")

class deliverynote_addon(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    payment_methods = fields.Selection([('bank', 'Bank'),
                                        ('cash', 'Cash'),
                                        ('mpesa', 'Mpesa')])

    @api.depends('amount_total')
    def _calc_amount_words(self):
        p = inflect.engine()
        number = self.amount_total
        result = p.number_to_words(number)
        self.amount_words = result.upper()

    amount_words = fields.Text(string="Amount in Words", compute=_calc_amount_words, store=True)

    @api.multi
    def print_receipt(self):
        self.ensure_one()
        invoice = self.env["account.invoice"].search([('number', '=', self.number)])
        return {'type': 'ir.actions.act_window', 'res_model': 'receipt.model', 'view_type': 'form',
                'view_mode': 'form', 'target': 'new','context':{'invoice_passed':invoice}}

    @api.multi
    def delivery_report(self):
        self.ensure_one()
        invoice = self.env["account.invoice"].search([('number', '=', self.number)])
        return {'type': 'ir.actions.act_window', 'res_model': 'delivery.model', 'view_type': 'form',
                'view_mode': 'form', 'target': 'new','context':{'invoice_passed':invoice}}

class receipt(models.Model):
    _name = 'receipt.model'

    invoice_id = fields.Many2one("account.invoice",string="Invoice ID")
    invoice_number = fields.Many2one("invoice_id.number", string="Invoice ID")
    partner = fields.Char(related='invoice_id.partner_id.name',string="Customer Name")
    partner_id=fields.Many2one(related='invoice_id.partner_id',string="Customer ID")
    products = fields.One2many(related="invoice_id.invoice_line_ids",string="Products")
    currency_id = fields.Many2one(related="invoice_id.currency_id",string="Currency")
    total = fields.Monetary(related="invoice_id.amount_total",string="Amount total",currency_field= "currency_id")
    payment = fields.Selection(related="invoice_id.payment_methods",string="Payment Method")
    num = fields.Integer(string="Get ID",related="id")
    date = fields.Datetime(string="Date")

    @api.depends('num')
    def _calc_number(self):
        self.number = str(self.num/10000).split('.')[1]

    number = fields.Char(string="Receipt ID",compute=_calc_number, store=True)

    @api.depends('total')
    def _calc_amount_words(self):
        p = inflect.engine()
        number = self.total
        result = p.number_to_words(number)
        self.amount_words = result.upper()

    amount_words = fields.Text(string="Amount in Words", compute=_calc_amount_words, store=True)

    @api.multi
    def view_receipt(self):
        self.ensure_one()
        return {'type': 'ir.actions.report', 'report_name': 'sale_custom.report_receipt_template',
                'report_type': "qweb-html"}

class delivery_note(models.Model):

    _name = 'delivery.model'

    invoice_id = fields.Many2one("account.invoice", string="Invoice ID")
    invoice_number = fields.Many2one("invoice_id.number", string="Invoice ID")
    partner = fields.Char(related='invoice_id.partner_id.name', string="Customer Name")
    partner_id = fields.Many2one(related='invoice_id.partner_id', string="Customer ID")
    products = fields.One2many(related="invoice_id.invoice_line_ids", string="Products")
    currency_id = fields.Many2one(related="invoice_id.currency_id", string="Currency")
    total = fields.Monetary(related="invoice_id.amount_total", string="Amount total", currency_field="currency_id")
    date = fields.Date(related='invoice_id.date',string="Date")
    user_id = fields.Many2one(related="invoice_id.user_id",string="Salesperson")
    num = fields.Integer(string="Get ID", related="id")

    @api.depends('num')
    def _calc_number(self):
        self.number = str(self.num/10000).split('.')[1]

    number= fields.Char(string="Delivery Note ID",compute=_calc_number, store=True)

    @api.depends('total')
    def _calc_amount_words(self):
        p = inflect.engine()
        number = self.total
        result = p.number_to_words(number)
        self.amount_words = result.upper()

    amount_words = fields.Text(string="Amount in Words", compute=_calc_amount_words, store=True)

    @api.multi
    def view_deliverynote(self):
        self.ensure_one()
        return {'type': 'ir.actions.report', 'report_name': 'sale_custom.report_deliverynote_template',
                'report_type': "qweb-html"}