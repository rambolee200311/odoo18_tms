import os
import base64
import json

def read(fp):
    with open(fp, 'r') as f:
        return f.read()

def write(fp, c):
    with open(fp, 'w') as f:
        f.write(c)

def update_inventory(fp):
    c = read(fp)
    old_marker = "### 2.2 IFFM \u2192 TMS \u5f15\u7528\u6d41"
    if old_marker not in c:
        return False
    lines = c.split('\n')
    section_start = None
    for i, line in enumerate(lines):
        if line.startswith("### 2.2 IFFM"):
            section_start = i
            break
    if section_start is None:
        return False
    section_end = None
    for i in range(section_start + 1, len(lines)):
        if lines[i].startswith("## "):
            section_end = i
            break
    if section_end is None:
        section_end = len(lines)
    new_section = """### 2.2 \u53cc Transport Request \u4f53\u7cfb

TMS \u7cfb\u7edf\u5b58\u5728\u4e24\u7c7b\u5bf9\u7b49\u7684 transport.request\uff0c\u5206\u522b\u6765\u81ea\u4e24\u4e2a\u4e1a\u52a1\u90e8\u95e8\uff1a

\x60\x60\x60
     IFFM \u90e8\u95e8\uff08\u8fdb\u53e3\u8d27\u4ee3\uff09                 TMS \u90e8\u95e8\uff08\u8fd0\u8f93\u7269\u6d41\uff09
  import.pickup.requirement           tlmp.transport.request
  \uff08\u8fdb\u53e3\u5230\u6e2f\u89e6\u53d1\uff09                      \uff08\u5ba2\u6237\u59d4\u6258/\u8fd0\u8425\u624b\u52a8\u521b\u5efa\uff09
          \u2502                                      \u2502
          \u2502  pickup_scene:                       \u2502  request_type:
          \u2502    to_our_warehouse                  \u2502    plan_driven \u2192 \u6392\u671f\u8c03\u5ea6
          \u2502    to_customer_address               \u2502    commercial  \u2192 \u8be2\u4ef7\u62a5\u4ef7
          \u2502    customer_self_pickup              \u2502
          \u2502                                      \u2502  destination_type:
          \u2502  \u5bb9\u5668: container_lines               \u2502    warehouse
          \u2502  \uff08from waybill\uff09                     \u2502    warehouse_transfer
          \u2502                                      \u2502    customer
          \u2502  \u72b6\u6001: draft\u2192submitted\u2192planned\u2192      \u2502    self_pickup
          \u2502        completed / cancelled          \u2502
          \u2502                                      \u2502  \u8d27\u7269: cargo_type + \u660e\u7ec6
          \u2502                                      \u2502  \uff08\u624b\u52a8/request\u5f55\u5165\uff09
          \u2502                                      \u2502
          \u2502                                      \u2502  \u72b6\u6001: draft\u2192confirmed\u2192cancelled
          \u2502                                      \u2502
          \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2192  pickup.plan  \u2190\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534
                    \uff08\u7edf\u4e00\u6392\u671f\u8c03\u5ea6\u5b50\u5355\u636e\uff09
                        \u2502
                        \u2193
                  transport.order
\x60\x60\x60

\u4e24\u4e2a transport.request \u7684\u7ed3\u6784\u5bf9\u7b49\u5173\u7cfb\uff1a"""
    new_section += """

| \u7ef4\u5ea6 | import.pickup.requirement | tlmp.transport.request |
|------|--------------------------|------------------------|
| \u89e6\u53d1\u65b9\u5f0f | waybill\uff08\u8fdb\u53e3\u63d0\u5355\uff09\u89e6\u53d1 | \u5ba2\u6237\u59d4\u6258 / \u8fd0\u8425\u624b\u52a8\u521b\u5efa |
| \u573a\u666f\u5b57\u6bb5 | pickup_scene\uff083\u90091\uff09 | request_type + destination_type |
| \u4ed3\u5e93\u573a\u666f | warehouse_id + warehouse_contact_id | warehouse_id\uff08stock.warehouse\uff09 |
| \u5ba2\u6237\u5730\u5740 | delivery_city/street/contact/phone | partner_id\uff08res.partner \u5730\u5740\uff09 |
| \u81ea\u63d0 | self_pickup_contact_id/phone | \u65e0\uff08Sprint3\u8865\u5145\uff09 |
| \u96c6\u88c5\u7bb1 | container_lines\uff08pickup.container.line\uff09 | \u65e0\uff08Sprint3\u8865\u5145\u2192pickup.plan\uff09 |
| \u6258\u4ef6\u8d27\u7269 | \u65e0 | pallet_count/package_count/weight/volume |
| \u72b6\u6001\u673a | 5\u72b6\u6001 | 3\u72b6\u6001 |
| \u6a21\u5757\u5f52\u5c5e | wd_iffm | wd_tlms |
| \u4e0b\u6e38 | pickup.plan\uff08source_type=iff\uff09 | pickup.plan\uff08transport_request_id\uff09 |

### 2.3 IFFM \u2194 TMS \u5f15\u7528\u6d41

\x60\x60\x60
import.pickup.requirement  \u2500\u2500\u53ea\u8bfb\u5f15\u7528\u2500\u2500\u2192  pickup.plan
\uff08wd_iffm\uff09                 Reference\u5b57\u6bb5       \uff08wd_tlms\uff09
     \u2502                                              \u2502
     \u2502 pickup_scene \u2192 destination_type               \u2502 transport_request_id
     \u2502 container_lines \u2192 container_line_ids          \u2502 \uff08Sprint3 \u5f3a\u5316\uff09
     \u2502 terminal/warehouse/address\u2192\u76ee\u6807\u5b57\u6bb5            \u2502
     \u2502 source_type=iff, \u6240\u6709\u660e\u7ec6 readonly            \u2502
     \u2502                                                \u2502
     \u7981\u6b62\u53cd\u5411\u4fee\u6539 IFFM                                  \u2502
\x60\x60\x60

**\u8de8\u6a21\u5757\u5f15\u7528\u7ea6\u675f**:
- \x60pickup.plan.iff_requirement_ref\x60 = Reference \u5b57\u6bb5\u6307\u5411 \x60import.pickup.requirement\x60\uff08\u65e0\u786c depends\uff09
- \x60pickup.plan.transport_request_id\x60 = Many2one \u6307\u5411 \x60tlmp.transport.request\x60\uff08\u540c\u6a21\u5757\uff09
- IFFM \u6765\u6e90\u7684 pickup.plan \u6240\u6709\u660e\u7ec6\u5b57\u6bb5 readonly
- TMS \u7edd\u4e0d\u53cd\u5411\u4fee\u6539 IFFM \u4efb\u4f55\u6570\u636e

"""
    new_lines = new_section.split('\n')
    new_content = '\n'.join(lines[:section_start]) + '\n' + new_section.strip() + '\n'
    new_content += '\n'.join(lines[section_end:])
    write(fp, new_content)
    return True

def update_stock(fp):
    c = read(fp)
    old_marker = "## 5. \u5ba2\u6237/\u5408\u4f5c\u4f19\u4f34\u94c1\u5f8b"
    if old_marker not in c:
        old_marker = "## 6. \u5ba2\u6237/\u5408\u4f5c\u4f19\u4f34\u94c1\u5f8b"
        if old_marker not in c:
            return False
    new_section = """## 5. \u8fd0\u8f93\u8bf7\u6c42\u53cc\u6765\u6e90\u4f53\u7cfb

### 5.1 \u4e24\u7c7b\u5bf9\u7b49 Transport Request

TMS \u7cfb\u7edf\u5b58\u5728\u4e24\u4e2a\u5bf9\u7b49\u7684 transport.request \u6a21\u578b\uff1a

| \u6a21\u578b | \u6a21\u5757 | \u89e6\u53d1\u65b9\u5f0f | \u9002\u7528\u573a\u666f |
|------|------|---------|---------|
| \x60import.pickup.requirement\x60 | wd_iffm | \u8fdb\u53e3\u63d0\u5355\u5230\u6e2f\u89e6\u53d1 | \u8fdb\u53e3\u8d27\u4ee3\u90e8\u95e8\u7684\u8fd0\u8f93\u9700\u6c42 |
| \x60tlmp.transport.request\x60 | wd_tlms | \u5ba2\u6237\u59d4\u6258/\u8fd0\u8425\u624b\u52a8\u521b\u5efa | \u8fd0\u8f93\u90e8\u95e8\u7684\u8fd0\u8f93\u9700\u6c42 |

### 5.2 \u7edf\u4e00\u8c03\u5ea6\u5165\u53e3

\u65e0\u8bba\u54ea\u79cd transport.request \u6765\u6e90\uff0c\u6392\u671f\u4e0e\u6267\u884c\u9636\u6bb5\u4f7f\u7528\u7edf\u4e00\u6a21\u578b\uff1a
\u4efb\u4f55 transport.request \u2192 pickup.plan\uff08\u6392\u671f\u8c03\u5ea6\u5b50\u5355\u636e\uff09\u2192 transport.order\uff08\u8fd0\u8f93\u6267\u884c\uff09

### 5.3 \u5b57\u6bb5\u5bf9\u7b49\u6620\u5c04

| import.pickup.requirement | tlmp.transport.request | \u8bf4\u660e |
|--------------------------|------------------------|------|
| pickup_scene | destination_type | \u76ee\u7684\u5730\u573a\u666f |
| warehouse_id | warehouse_id | \u76ee\u6807\u4ed3\u5e93 |
| terminal_a | terminal_id | \u8d77\u70b9\u7801\u5934/\u8d27\u7ad9 |
| container_lines | container_line_ids\uff08Sprint3\uff09 | \u96c6\u88c5\u7bb1\u660e\u7ec6 |
| delivery_city/street/zip/contact/phone | partner_id \u5730\u5740 | \u5ba2\u6237\u4ea4\u4ed8\u4fe1\u606f |
| self_pickup_contact_id/phone | \u65e0\uff08Sprint3\u8865\u5145\uff09 | \u81ea\u63d0\u4fe1\u606f |

### 5.4 \u8de8\u6a21\u5757\u53ea\u8bfb\u5f15\u7528

- import.pickup.requirement \u662f wd_iffm \u6a21\u5757\u7684\u6a21\u578b\uff0cTMS \u901a\u8fc7 Reference \u5b57\u6bb5\u53ea\u8bfb\u5f15\u7528
- \u5f53 pickup.plan.source_type='iff' \u65f6\uff0c\u6240\u6709\u540c\u6b65\u5b57\u6bb5\u8bbe\u4e3a readonly
- TMS \u7edd\u4e0d\u53cd\u5411\u4fee\u6539 wd_iffm \u7684\u6570\u636e

### 5.5 \u72b6\u6001\u673a\u5dee\u5f02

| import.pickup.requirement | tlmp.transport.request | \u8bf4\u660e |
|--------------------------|------------------------|------|
| draft \u2192 submitted | draft \u2192 ... | \u8349\u6848\u9636\u6bb5 |
| submitted \u2192 planned | draft \u2192 confirmed | \u786e\u8ba4/\u8ba1\u5212\u9636\u6bb5 |
| planned \u2192 completed | confirmed \u2192 (order) | \u6267\u884c\u5b8c\u6210 |
| draft/submitted \u2192 cancelled | draft/confirmed \u2192 cancelled | \u53d6\u6d88 |

"""
    c = c.replace(old_marker, new_section + old_marker)
    write(fp, c)
    return True

# Execute
errors = []

r1 = update_inventory('/Users/lijianqiang/Documents/odoo18_tms/docs/context/business/inventory_flow.md')
if r1:
    print("  OK: inventory_flow.md")
else:
    print("  FAIL: inventory_flow.md")
    errors.append("inventory_flow.md")

r2 = update_stock('/Users/lijianqiang/Documents/odoo18_tms/docs/context/business/stock_rule.md')
if r2:
    print("  OK: stock_rule.md")
else:
    print("  FAIL: stock_rule.md")
    errors.append("stock_rule.md")

if errors:
    print(f"Errors: {errors}")
    exit(1)
else:
    print("All business docs updated successfully.")
    exit(0)
