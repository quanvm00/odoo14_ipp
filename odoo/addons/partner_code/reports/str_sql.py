
select_sql = """
    WITH currency_rate as (%s)
        SELECT 
            s.date_order as date_order,
            to_char(s.date_order, 'YYYY-MM-DD HH24:MI:SS') as str_date_order,                  
            l.id as line_id,
            l.discount as discount,
            l.product_id as product_id,
            t.uom_id as product_uom,
            l.price_unit as price_unit,
            sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
            sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
            sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
            sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
            
            
            s.name as name,
            s.is_from_app as is_from_app,
            s.date_order as date,
            s.confirmation_date as confirmation_date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.user_ss_id as user_ss_id,
            partner2.name as user_name,
            s.company_id as company_id, res_company.name as company_name, res_company.id as company_id, res_company.manager_id as manager_id, 
            extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
            t.categ_id as categ_id,
            p.product_tmpl_id as product_tmpl_id,
            
        """

from_sql = """
    FROM sale_order_line l
        JOIN sale_order s on (l.order_id=s.id)
        JOIN res_partner partner on s.partner_id = partner.id
        LEFT JOIN product_product p on (l.product_id=p.id)
            LEFT JOIN product_template t on (p.product_tmpl_id=t.id)
        LEFT JOIN product_uom u on (u.id=l.product_uom)
        LEFT JOIN res_users res_user on (res_user.id = s.user_id)
        LEFT JOIN res_partner partner2 on (partner2.id = res_user.partner_id)
        LEFT JOIN product_uom u2 on (u2.id=t.uom_id)
        LEFT JOIN res_company res_company on (res_company.id = s.company_id)
        LEFT JOIN currency_rate cr on (cr.currency_id = pp.currency_id and
            cr.company_id = s.company_id and
            cr.date_start <= coalesce(s.date_order, now()) and
            (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
"""

group_by_sql = """
    GROUP BY s.date_order, l.id, l.discount, t.uom_id, s.name, s.confirmation_date, s.state, s.partner_id, 
                s.user_id, s.user_ss_id, s.is_from_app,
				partner2.name, s.company_id, res_company.name, res_company.id, t.categ_id, p.product_tmpl_id
	ORDER BY 
        s.date_order, 
        res_company.id, 
        s.user_id, s.partner_id, t.categ_id, l.product_id
"""




sql = """
SELECT
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_delivered / u.factor * u2.factor) ELSE 0 END as qty_delivered,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END as qty_invoiced,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END as qty_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_invoiced,
            count(*) as nbr,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            s.source_id as source_id,
            extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as weight,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as volume,
            l.discount as discount,
            CASE WHEN l.product_id IS NOT NULL THEN sum((l.price_unit * l.product_uom_qty * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END))ELSE 0 END as discount_amount,
            s.id as order_id
FROM 
            sale_order_line l
              right outer join sale_order s on (s.id=l.order_id)
              join res_partner partner on s.partner_id = partner.id
                left join product_product p on (l.product_id=p.id)
                    left join product_template t on (p.product_tmpl_id=t.id)
            left join uom_uom u on (u.id=l.product_uom)
            left join uom_uom u2 on (u2.id=t.uom_id)
            left join product_pricelist pp on (s.pricelist_id = pp.id)
GROUP BY 
            l.product_id,
            l.order_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.user_id,
            s.state,
            s.company_id,
            s.source_id,
            s.team_id,
            p.product_tmpl_id,
            l.discount,
            s.id 

"""
where_sql = """WHERE 
                s.date_order >=%s  
                AND s.date_order <=%s 
                
                AND t.categ_id in %s 
                AND s.state not in  ('draft', 'cancel', 'sent')
                AND s.id in %s
                
                """

