with open('app/main.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('Control.etat == "En place"', 'Control.status == "implemented"')
c = c.replace('c.etat == "En place"', 'c.status == "implemented"')
c = c.replace('sc.nom', 'sc.name')
c = c.replace('t.nom', 't.name')
c = c.replace('"nom": sc.nom', '"nom": sc.name')
c = c.replace('"nom": t.nom', '"nom": t.name')

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(c)

with open('dashboard/streamlit_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'cols = ["id", "nom", "description", "theme", "applicable", "etat", "maturite", "justification", "preuve"]',
    'cols = ["id", "name", "description", "theme", "is_applicable", "status", "maturity", "justification", "evidence"]'
)

old_loop = '''                for _, row in theme_controls.iterrows():
                    desc = row['description'] if row.get('description') else 'Description non spécifiée.'
                    etat = row.get('etat', 'Non défini')
                    color = "#27ae60" if etat == "En place" else "#f39c12" if etat == "Partiel" else "#c0392b"
                    badge = f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">{etat}</span>'
                    mat = f"{row.get('maturite', 0)}/5"
                    justif = row.get('justification', '')
                    
                    html_content += f"""<tr>
<td style="font-weight: bold; color: #1c325c;">{row['id']}</td>
<td style="font-weight: bold; font-size: 12px;">{row['nom']}</td>'''

new_loop = '''                for _, row in theme_controls.iterrows():
                    desc = row['description'] if row.get('description') else 'Description non spécifiée.'
                    etat = row.get('status', 'Non défini')
                    color = "#27ae60" if etat == "implemented" else "#f39c12" if etat == "partial" else "#c0392b"
                    badge = f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">{etat}</span>'
                    mat = f"{row.get('maturity', 0)}/5"
                    justif = row.get('justification', '')
                    
                    html_content += f"""<tr>
<td style="font-weight: bold; color: #1c325c;">{row['id']}</td>
<td style="font-weight: bold; font-size: 12px;">{row['name']}</td>'''

c = c.replace(old_loop, new_loop)

# Also fix dataframe display in SoA overview
c = c.replace('df["progression (%)"] = (df["en_place"] / df["total"] * 100).round(1)', 'df["progression (%)"] = (df["en_place"] / df["total"] * 100).round(1)')
# Wait, "nom" is still hardcoded in get_kpi_heatmap and others:
c = c.replace('df[["id", "nom", "gravite"', 'df[["id", "nom", "gravite"') # Actually the API returns "nom": sc.name, so df has "nom"

with open('dashboard/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(c)
