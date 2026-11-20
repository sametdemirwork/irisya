"""One-off: carries the previous site's stylesheet over to the İrisya palette and type.
Reads  vors-dental-clinic/assets/css/style.css   Writes  irisya-clinic/assets/css/style.css
The İrisya-only components are appended from irisya-tools/irisya.css (before the responsive block)."""
import io, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.normpath(os.path.join(HERE, '..', 'vors-dental-clinic', 'assets', 'css', 'style.css'))
dst = os.path.normpath(os.path.join(HERE, '..', 'irisya-clinic', 'assets', 'css', 'style.css'))
add = os.path.join(HERE, 'irisya.css')
s = io.open(src, encoding='utf-8').read()

HEX = {
 '#C6A5FF':'#A8C7E3','#B593FA':'#8FB5D8','#EEE8FB':'#E6EEF6','#EBE3FE':'#E7EFF7','#E5D9FF':'#DCE8F4','#D9CDFB':'#CFDDEA',
 '#D9C9FF':'#CCDDEE','#CDBBFF':'#C3D8EC','#C9B0FB':'#B7D0E8','#C4EE87':'#CFE7F8','#5318EB':'#2D6BA6','#3B1878':'#13365F',
 '#280F62':'#021E44','#0C021C':'#04132B','#F4EFFF':'#EFF5FA','#ECE5FD':'#E5EDF6','#E6DDFB':'#DFE9F4','#E2D6FF':'#D8E6F3',
 '#E2D5FF':'#D8E6F3','#DDF4BA':'#E0EFFA','#D8CCFF':'#D2E2F0','#C2A8FF':'#A9C7E3','#BFA0FF':'#A2C2E0','#B6E46F':'#B7D9F1',
 '#9F7AEA':'#6E9CC8','#9C78F7':'#5E93C6','#8D6CEA':'#5F8FC0','#6B3DF0':'#3576B5','#6A3AEE':'#2C6AAA','#6440C8':'#2F64A0',
 '#3C2590':'#123F72','#3A1D82':'#10386A','#2A0E6B':'#0A2A55','#1B0A45':'#051E40','#1A0846':'#041D40','#120A2B':'#061A36',
 '#07040F':'#020B19','#3a1d82':'#10386A','#1b0a45':'#051E40','#3c2590':'#123F72',
}
RGB = {
 '40,15,98':'2,30,68','83,24,235':'45,107,166','198,165,255':'168,199,227','7,4,15':'2,11,25','12,2,28':'4,19,43',
 '9,4,22':'2,12,28','107,83,255':'70,140,210','216,204,255':'210,226,240','238,231,255':'231,239,247','235,227,254':'231,239,247',
 '196,238,135':'207,231,248','246,242,255':'243,247,251','244,239,255':'241,246,251','226,212,255':'220,233,245',
 '214,196,255':'205,224,241','158,118,255':'110,160,215','112,64,226':'50,110,180','60,50,140':'20,60,110','60,20,140':'15,50,100',
 '27,10,69':'4,24,52','200,170,255':'170,200,230','20,0,60':'2,16,40','176,140,255':'140,185,230','170,130,255':'130,180,230',
 '120,80,240':'60,120,200','110,70,220':'50,110,190','106,58,238':'45,105,180','10,6,22':'2,12,28',
}
for k, v in HEX.items():
    s = re.sub(re.escape(k), v, s, flags=re.I)
def rgb(m):
    key = re.sub(r'\s', '', m.group(2))
    return m.group(1) + (', '.join(RGB[key].split(',')) if key in RGB else m.group(2))
s = re.sub(r'(rgba?\()(\s*\d+\s*,\s*\d+\s*,\s*\d+)', rgb, s)

# header + tokens
s = s.replace("""   Vors Dental Clinic — One-page site
   Palette: ink #0C021C · purple #5318EB · deep #280F62 · lilac #C6A5FF
            pale #EBE3FE · lime #C4EE87""".replace('#0C021C','#04132B'), "x")  # no-op guard
s = re.sub(r'/\* =+\n   Vors Dental Clinic.*?=+ \*/', """/* ==========================================================================
   İrisya Clinic — One-page site (eye colour change, Istanbul)
   Palette (from the logo): navy #021E44 · ink #04132B · iris blue #2D6BA6
            sky #A8C7E3 · mist #E7EFF7 · ice #CFE7F8 · steel #4A6C88
   Variable names keep the original roles: --deep = brand navy, --purple = iris
   blue (action colour), --lilac = sky, --pale = mist, --lime = ice (highlight).
   Type: Pitch system — Figtree 800/700 with tight tracking (display, body),
   Space Mono uppercase eyebrows.
   ========================================================================== */""", s, count=1, flags=re.S)
s = s.replace("""  --f-head: 'Figtree', 'Helvetica Neue', Arial, sans-serif;
  --f-body: 'Figtree', 'Helvetica Neue', Arial, sans-serif;
  --f-mono: 'Space Mono', ui-monospace, Menlo, monospace;""", """  --steel: #4A6C88;
  --f-head: 'Figtree', 'Helvetica Neue', Arial, sans-serif;
  --f-ui: 'Figtree', 'Helvetica Neue', Arial, sans-serif;
  --f-body: 'Figtree', 'Helvetica Neue', Arial, sans-serif;
  --f-mono: 'Space Mono', ui-monospace, Menlo, monospace;""")
# small headings move to the UI face; display classes get the serif back in irisya.css
s = s.replace('font-family: var(--f-head)', 'font-family: var(--f-ui)')
# uppercase labels: tracked out instead of the mono's tight setting
def track(m):
    block = m.group(0)
    if 'var(--f-mono)' in block:
        block = re.sub(r'letter-spacing:\s*-\.02em', 'letter-spacing: .12em', block)
        block = re.sub(r'letter-spacing:\s*\.08em', 'letter-spacing: .14em', block)
    return block

extra = io.open(add, encoding='utf-8').read()
marker = '/* ==========================================================================\n   RESPONSIVE'
assert marker in s
s = s.replace(marker, extra + '\n' + marker, 1)
io.open(dst, 'w', encoding='utf-8', newline='\n').write(s)
left = re.findall(r'#(?:5318EB|280F62|C6A5FF|C4EE87|EBE3FE)|rgba\(83, 24, 235', s, flags=re.I)
print('written', len(s), 'leftover old colours:', len(left))
