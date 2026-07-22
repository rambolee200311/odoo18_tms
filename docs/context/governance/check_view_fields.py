#!/usr/bin/env python3
"""
View-Model 字段存在性交叉校验
防止 BUG-007 类型错误：视图引用了模型中不存在的字段
用法: python3 check_view_fields.py
返回码: 0=通过, 1=有错误
"""
import os, re, sys, glob
import xml.etree.ElementTree as ET

BASE = '/Users/lijianqiang/Documents/odoo18_tms/addons/wd_tlms'
MODELS_DIR = os.path.join(BASE, 'models')
VIEWS_DIR = os.path.join(BASE, 'views')

def extract_field_from_py(filepath):
    """从 Python 模型文件中提取字段定义 {field_name: line_number}"""
    fields = {}
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            m = re.match(r'^    (\w+)\s*=\s*fields\.(\w+)\(', line)
            if m:
                fields[m.group(1)] = i
    return fields

def extract_model_fields():
    """扫描所有模型文件, 构建 {model_name: {field_name: line}}"""
    models = {}
    current_model = None
    for f in sorted(glob.glob(os.path.join(MODELS_DIR, '*.py'))):
        with open(f) as fh:
            for line in fh:
                m = re.match(r'^\s*_name\s*=\s*'([^']+)'' , line)
                if m:
                    current_model = m.group(1)
                    models.setdefault(current_model, {})
                if current_model:
                    fm = re.match(r'^\s*(\w+)\s*=\s*fields\.(\w+)\(', line)
                    if fm:
                        models[current_model][fm.group(1)] = True
    return models

def extract_view_fields(filepath):
    """从视图 XML 中提取 {model_name: [(field_name, line)]}"""
    views = {}
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except:
        return views
    for record in root.findall(".//record"):
        model_elem = record.find("./field[@name='model']")
        if model_elem is None or not model_elem.text:
            continue
        model_name = model_elem.text.strip()
        if model_name.startswith('tlmp.') or model_name.startswith('transport.'):
            arch = record.find("./field[@name='arch']")
            if arch is not None:
                fields_found = set()
                for field_tag in arch.iter('field'):
                    fn = field_tag.get('name')
                    if fn and fn != 'arch' and not fn.startswith(('parent.', 'context_')):
                        fields_found.add(fn)
                for fn in fields_found:
                    views.setdefault(model_name, []).append(fn)
    return views

def main():
    models = extract_model_fields()
    errors = []
    for f in sorted(glob.glob(os.path.join(VIEWS_DIR, '*.xml'))):
        view_fields = extract_view_fields(f)
        for model_name, fnames in view_fields.items():
            model_fields = models.get(model_name, {})
            for fn in fnames:
                if fn not in model_fields:
                    # Check if it might be an inherited field
                    # by looking in other models with this prefix
                    errors.append((os.path.basename(f), model_name, fn))

    if errors:
        print("=== View-Model 字段存在性校验 ===")
        for fname, model, field in sorted(errors):
            print(f"  {fname}: field '{field}' NOT in model '{model}'")
        print(f"\n❌ {len(errors)} errors found")
        return 1
    else:
        print("  View-Model 字段校验: 全部通过 ✅")
        return 0

if __name__ == '__main__':
    sys.exit(main())
