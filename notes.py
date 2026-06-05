import re
import html as html_mod

# Python script to convert MIPS.md into a beautiful standalone HTML page
# Run: python build.py

md_file = "MIPS.md"
output_html = "MIPS_Notes.html"

with open(md_file, "r", encoding="utf-8") as f:
    md = f.read()

# --- Remove YAML front matter ---
md = re.sub(r'^---.*?---\s*', '', md, flags=re.DOTALL)

# --- Escape HTML ---
md = html_mod.escape(md)

# --- Code blocks (fenced) ---
def replace_code_blocks(text):
    pattern = r'```(\w*)\n(.*?)```'
    def repl(m):
        lang = m.group(1) or ''
        code = m.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    return re.sub(pattern, repl, text, flags=re.DOTALL)

md = replace_code_blocks(md)

# --- Inline code ---
md = re.sub(r'`([^`]+)`', r'<code>\1</code>', md)

# --- Bold / Italic ---
md = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', md)
md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md)

# --- Images ---
md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', md)

# --- Links ---
md = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', md)

# --- Headings ---
md = re.sub(r'^#### (.+)$', r'<h4 id="\1">\1</h4>', md, flags=re.MULTILINE)
md = re.sub(r'^### (.+)$', r'<h3 id="\1">\1</h3>', md, flags=re.MULTILINE)
md = re.sub(r'^## (.+)$', r'<h2 id="\1">\1</h2>', md, flags=re.MULTILINE)
md = re.sub(r'^# (.+)$', r'<h1 id="\1">\1</h1>', md, flags=re.MULTILINE)

# --- Horizontal rules ---
md = re.sub(r'^---$', '<hr>', md, flags=re.MULTILINE)

# --- Blockquotes ---
md = re.sub(r'^&gt; (.+)$', r'<blockquote><p>\1</p></blockquote>', md, flags=re.MULTILINE)

# --- Unordered lists ---
md = re.sub(r'^- (.+)$', r'<li>\1</li>', md, flags=re.MULTILINE)

# --- Paragraphs (double newlines) ---
paragraphs = md.split('\n\n')
for i, p in enumerate(paragraphs):
    if not re.match(r'<(h[1-6]|pre|table|ul|ol|li|blockquote|hr|img|details|summary|div)', p.strip()):
        paragraphs[i] = f'<p>{p.strip()}</p>'
md = '\n\n'.join(paragraphs)

# --- Wrap continuous <li> in <ul> ---
md = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\n\g<0></ul>\n', md)

# --- Tables (basic pipe table handling) ---
# Simple approach: detect table rows and convert
lines = md.split('\n')
processed = []
i = 0
while i < len(lines):
    line = lines[i]
    if '|' in line and not line.strip().startswith('<'):
        table_lines = []
        while i < len(lines) and '|' in lines[i] and not lines[i].strip().startswith('<'):
            table_lines.append(lines[i].strip())
            i += 1
        if len(table_lines) >= 2:
            # Header
            header_cells = [c.strip() for c in table_lines[0].split('|') if c.strip()]
            # Separator (skip)
            # Body rows
            body_rows = []
            for tl in table_lines[2:]:
                cells = [c.strip() for c in tl.split('|') if c.strip()]
                body_rows.append(cells)
            html_table = '<table>\n<thead>\n<tr>\n'
            for hc in header_cells:
                html_table += f'<th>{hc}</th>\n'
            html_table += '</tr>\n</thead>\n<tbody>\n'
            for row in body_rows:
                html_table += '<tr>\n'
                for cell in row:
                    html_table += f'<td>{cell}</td>\n'
                html_table += '</tr>\n'
            html_table += '</tbody>\n</table>'
            processed.append(html_table)
            continue
    processed.append(line)
    i += 1
md = '\n'.join(processed)

# --- Unescape inside code blocks ---
md = re.sub(r'<code class="language-([^"]*)">(.*?)</code>', lambda m: f'<pre><code class="language-{m.group(1)}">{html_mod.unescape(m.group(2))}</code></pre>', md, flags=re.DOTALL)
md = re.sub(r'<pre><code>(.*?)</code></pre>', lambda m: f'<pre><code>{html_mod.unescape(m.group(1))}</code></pre>', md, flags=re.DOTALL)
md = re.sub(r'<code>(.*?)</code>', lambda m: f'<code>{html_mod.unescape(m.group(1))}</code>', md)

# --- Details / Summary ---
md = md.replace('<details>', '<details>\n')
md = md.replace('</details>', '</details>\n')
md = md.replace('<summary>', '<summary>')
md = md.replace('</summary>', '</summary>')

# ========= WRITE HTML =========
html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIPS 学习笔记</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <style>
        :root {{
            --bg: #faf8f5; --card-bg: #ffffff; --text: #2c2c2c; --text-light: #555555;
            --text-muted: #888888; --accent: #b8542b; --accent-light: #f1d9c8;
            --accent-blue: #4b6e8c; --border: #e8e3d6; --border-light: #f0ebe0;
            --code-bg: #f5f2eb; --code-text: #38323a;
            --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.04);
            --radius: 12px;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg); font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
            color: var(--text); line-height: 1.7; -webkit-font-smoothing: antialiased; padding: 2rem 1rem;
        }}
        .container {{
            max-width: 960px; margin: 0 auto; background: var(--card-bg); border-radius: var(--radius);
            box-shadow: var(--shadow); border: 1px solid var(--border); padding: 3rem 3.5rem;
        }}
        @media (max-width: 768px) {{ .container {{ padding: 2rem 1.5rem; }} }}

        .note-header {{ margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 2px dashed var(--border); }}
        .note-header .eyebrow {{
            display: inline-flex; align-items: center; gap: 0.5rem; font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent);
            background: var(--accent-light); padding: 0.3rem 0.8rem; border-radius: 999px; margin-bottom: 0.8rem;
        }}
        .note-header h1 {{
            font-size: 2.8rem; font-weight: 700;
            background: linear-gradient(135deg, var(--text) 0%, var(--accent) 80%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            margin: 0.5rem 0 0.2rem; line-height: 1.2;
        }}
        .note-header .subtitle {{ color: var(--text-light); font-size: 1rem; max-width: 600px; }}

        h1, h2, h3, h4, h5, h6 {{ scroll-margin-top: 80px; }}
        h1 {{ font-size: 2em; border-bottom: 2px solid var(--border); padding-bottom: 0.3em; margin-top: 2em; margin-bottom: 0.6em; }}
        h2 {{ font-size: 1.6em; border-left: 4px solid var(--accent); padding-left: 0.8em; margin-top: 2em; margin-bottom: 0.6em; }}
        h3 {{ font-size: 1.3em; color: var(--accent); margin-top: 1.8em; margin-bottom: 0.5em; }}
        h3::before {{ content: "§ "; color: var(--text-muted); font-weight: 400; }}
        h4 {{ font-size: 1.1em; margin-top: 1.5em; margin-bottom: 0.5em; }}

        p {{ margin-bottom: 1em; }}
        strong {{ color: var(--text); background: linear-gradient(180deg, transparent 65%, var(--accent-light) 65%); padding: 0 2px; }}
        a {{ color: var(--accent-blue); text-decoration: none; border-bottom: 1px dashed var(--accent-blue); }}
        a:hover {{ color: var(--accent); border-bottom-color: var(--accent); }}

        code {{
            font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.88em;
            background: var(--code-bg); color: var(--accent); border: 1px solid var(--border);
            border-radius: 4px; padding: 0.15em 0.4em;
        }}
        pre {{
            background: var(--code-bg); border: 1px solid var(--border); border-radius: 10px;
            padding: 1.2em 1.4em; overflow-x: auto; margin: 1.2em 0;
            font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; line-height: 1.6;
        }}
        pre code {{ background: transparent; border: none; padding: 0; color: var(--code-text); font-size: inherit; }}

        table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 1.5em 0;
                border: 1px solid var(--border); border-radius: 8px; overflow: hidden; font-size: 0.95rem; }}
        th {{ background: var(--accent-light); font-weight: 600; padding: 0.7em 1em; border-bottom: 2px solid var(--accent); text-align: left; }}
        td {{ padding: 0.6em 1em; border-bottom: 1px solid var(--border-light); }}
        tr:last-child td {{ border-bottom: none; }}
        tr:nth-child(even) td {{ background: #fcfaf7; }}

        blockquote {{
            background: var(--accent-light); border-left: 4px solid var(--accent);
            border-radius: 0 8px 8px 0; padding: 1em 1.2em; margin: 1.5em 0;
        }}

        ul, ol {{ padding-left: 1.8em; margin: 0.8em 0; }}
        li {{ margin: 0.3em 0; }}
        ul li::marker {{ color: var(--accent); }}

        details {{ margin: 0.8em 0; border: 1px solid var(--border-light); border-radius: 8px; padding: 0.5em 1em; background: #fdfcf9; }}
        summary {{ font-weight: 600; cursor: pointer; padding: 0.3em 0; color: var(--accent); }}

        hr {{ border: none; border-top: 1px dashed var(--border); margin: 2.5em 0; position: relative; }}
        hr::after {{
            content: "✦"; position: absolute; left: 50%; top: -0.8em; transform: translateX(-50%);
            background: var(--card-bg); padding: 0 0.8em; color: var(--accent); font-size: 0.9rem;
        }}

        img {{ max-width: 100%; border-radius: 8px; border: 1px solid var(--border); margin: 1em 0; background: #fafafa; }}

        .toc-sidebar {{
            position: fixed; right: 20px; top: 50%; transform: translateY(-50%); width: 240px;
            max-height: 70vh; overflow-y: auto; background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 12px; box-shadow: var(--shadow); padding: 1rem 1.2rem; font-size: 0.8rem; z-index: 100;
        }}
        .toc-sidebar h4 {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);
            margin: 0 0 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);
        }}
        .toc-sidebar ul {{ list-style: none; padding: 0; margin: 0; }}
        .toc-sidebar li {{ margin: 0; }}
        .toc-sidebar a {{
            display: block; padding: 0.35em 0.6em; color: var(--text-light);
            border-left: 2px solid transparent; border-bottom: none; border-radius: 0 6px 6px 0;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-decoration: none;
        }}
        .toc-sidebar a:hover {{ color: var(--accent); background: #faf6f2; }}
        .toc-sidebar a.active {{ color: var(--accent); border-left-color: var(--accent); background: var(--accent-light); font-weight: 600; }}
        .toc-sidebar .toc-h3 {{ padding-left: 1.2em; font-size: 0.78rem; }}

        @media (max-width: 1200px) {{ .toc-sidebar {{ display: none; }} }}

        .back-to-top {{
            position: fixed; right: 24px; bottom: 24px; width: 44px; height: 44px; border-radius: 50%;
            background: var(--card-bg); border: 1px solid var(--border); box-shadow: var(--shadow);
            display: flex; align-items: center; justify-content: center; cursor: pointer;
            opacity: 0; pointer-events: none; transition: opacity 0.3s; z-index: 99;
            font-size: 1.2rem; color: var(--text-light);
        }}
        .back-to-top.visible {{ opacity: 1; pointer-events: auto; }}
        .back-to-top:hover {{ color: var(--accent); transform: translateY(-3px); }}
    </style>
</head>
<body>
<nav class="toc-sidebar" id="toc"></nav>
<div class="back-to-top" id="backToTop">↑</div>

<div class="container" id="content">
    <div class="note-header">
        <div class="eyebrow"><span>● Notebook</span><span>计算机组成 · 汇编语言</span></div>
        <h1>MIPS 学习笔记</h1>
        <p class="subtitle">从指令集到流水线，一份关于 MIPS 体系结构、寻址方式与汇编翻译的整理与速查手册。</p>
    </div>

{md}

</div>

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>
    document.querySelectorAll('.katex').forEach(el => {{
        const tex = el.textContent;
        try {{ katex.render(tex, el, {{ throwOnError: false }}); }} catch(e) {{ el.textContent = tex; }}
    }});
    hljs.highlightAll();

    (function buildTOC() {{
        const toc = document.getElementById('toc');
        const content = document.getElementById('content');
        const headings = content.querySelectorAll('h2[id], h3[id]');
        if (headings.length === 0) return;
        let html = '<h4>Contents</h4><ul>';
        headings.forEach(h => {{
            const tag = h.tagName.toLowerCase();
            const cls = tag === 'h3' ? 'toc-h3' : '';
            html += `<li><a class="${{cls}}" href="#${{h.id}}" data-target="${{h.id}}">${{h.textContent.trim().substring(0, 28)}}</a></li>`;
        }});
        html += '</ul>';
        toc.innerHTML = html;
        toc.querySelectorAll('a').forEach(a => {{
            a.addEventListener('click', e => {{
                e.preventDefault();
                document.getElementById(a.dataset.target).scrollIntoView({{ behavior: 'smooth' }});
            }});
        }});
        const links = [...toc.querySelectorAll('a')];
        new IntersectionObserver(entries => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    links.forEach(l => l.classList.remove('active'));
                    links.find(l => l.dataset.target === entry.target.id)?.classList.add('active');
                }}
            }});
        }}, {{ rootMargin: '-30% 0px -65% 0px' }}).observe(document.querySelectorAll('h2[id], h3[id]'));
    }})();

    const btn = document.getElementById('backToTop');
    window.addEventListener('scroll', () => btn.classList.toggle('visible', window.scrollY > 600));
    btn.addEventListener('click', () => window.scrollTo({{ top: 0, behavior: 'smooth' }}));
</script>
</body>
</html>
'''

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Done! Open {output_html} in your browser.")