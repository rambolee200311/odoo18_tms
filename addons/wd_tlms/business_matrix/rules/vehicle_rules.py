"""RULE-VEHICLE-000~005 static handlers (used as fallback when no configured rules)."""


def check_vehicle_rules(ctx):
    """Execute vehicle requirement rules against the given context.
    Returns a list of violation dicts.

    Priority chain: Service Type Split > ADR Compliance > Capacity > Body Type
    """
    violations = []
    vehicle_mode = ctx.get('vehicle_requirement_mode', 'required')

    # RULE-VEHICLE-000: Service type split (enforced by vehicle_requirement_mode)
    if vehicle_mode == 'exempted':
        return violations  # skip all vehicle checks for exempted mode

    carrier = ctx.get('carrier_type')
    carrier_caps = ctx.get('carrier_capabilities') or set()
    vehicle_body = ctx.get('vehicle_body_type')
    vehicle_cap = ctx.get('vehicle_capacity_requirement')
    is_dg = ctx.get('is_dangerous_goods', 'normal')

    # RULE-VEHICLE-002: ADR compliance chain
    # 2a: ADR carrier capability
    if is_dg == 'adr_dangerous' and 'adr' not in carrier_caps:
        violations.append({
            'rule_id': 'RULE-VEHICLE-002',
            'message': 'ADR危险品运输需承运商持有ADR资质',
            'result': 'block',
        })

    # RULE-VEHICLE-005: DG / normal fleet mutual exclusion
    if is_dg == 'adr_dangerous' and carrier == 'courier':
        violations.append({
            'rule_id': 'RULE-VEHICLE-005',
            'message': '快递承运商禁止承运ADR危险品',
            'result': 'block',
        })

    # RULE-VEHICLE-003: Capacity constraint
    if vehicle_cap != 'no_limit' and vehicle_cap:
        # This rule is triggered when request specifies a minimum capacity.
        # The actual vehicle capacity matching is done at allocation time (Sprint50),
        # but we flag this as a constraint for the plan.
        violations.append({
            'rule_id': 'RULE-VEHICLE-003',
            'message': '车辆载重下限需求：%s' % dict(
                [('below_40t', '< 40t'), ('40t_44t', '40t-44t'), ('over_44t', '> 44t')]
            ).get(vehicle_cap, vehicle_cap),
            'result': 'warning',  # soft constraint — actual match at allocation
        })

    # RULE-VEHICLE-001: Body type constraint
    if vehicle_body and vehicle_body != 'no_requirement':
        violations.append({
            'rule_id': 'RULE-VEHICLE-001',
            'message': '车辆装卸类型需求：%s' % vehicle_body,
            'result': 'warning',  # soft constraint — actual match at allocation
        })

    return violations