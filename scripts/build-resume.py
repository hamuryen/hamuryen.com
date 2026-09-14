#!/usr/bin/env python3
"""Generate a single-column HTML and plain-text resume from index.html."""
from pathlib import Path
from html import unescape, escape
import re
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'index.html').read_text()
def clean(value):
    return ' '.join(unescape(re.sub('<[^>]+>', ' ', value)).split())
def section(name):
    return re.search(r'<section id="'+name+r'"[\s\S]*?</section>',s).group()
def entries(name):
    return re.findall(r'<div class="exp-date">(.*?)</div>\s*<div class="exp-info">\s*<h3 class="exp-role">(.*?)</h3>\s*<div class="exp-desc">(.*?)</div>(.*?)(?=<div class="exp-card|</section>)',section(name),re.S)
summary='Senior Software Engineer based in Berlin with 14+ years of experience building distributed systems, microservices, and real-time video streaming and processing platforms. Work spans multi-cluster Kubernetes architectures and services in Go, Kotlin, Scala, Python, and Java across cloud, on-premise, and edge environments, alongside sensor and industrial device integration.'
parts=['<h1>Burak Hamuryen</h1><p class="title">Senior Software Engineer</p><p>Berlin, Germany<br>Email: <a href="mailto:burak@hamuryen.com">burak@hamuryen.com</a><br>Website: <a href="https://hamuryen.com/">hamuryen.com</a><br>GitHub: <a href="https://github.com/hamuryen">github.com/hamuryen</a><br>LinkedIn: <a href="https://www.linkedin.com/in/hamuryen">linkedin.com/in/hamuryen</a></p>','<h2>Professional Summary</h2><p>'+summary+'</p>','<h2>Professional Experience</h2>']
for date,role,description,tail in entries('experience'):
    role=clean(role).replace('R&D Engineer', 'Research and Development Engineer').replace('Freelance ·', 'Freelance Software Engineer ·')
    bullets=re.split(r'(?<=[.!?])\s+(?=[A-Z])',clean(description))
    tags=', '.join(clean(t) for t in re.findall(r'<span class="tag">(.*?)</span>',tail))
    tags=tags.replace('GCloud', 'Google Cloud (GCP)').replace('K8s', 'Kubernetes (K8s)')
    parts.append('<article><h3>'+escape(clean(role))+'</h3><p class="date">'+escape(clean(date).replace('Now','Present'))+'</p><ul>'+''.join('<li>'+escape(b)+'</li>' for b in bullets)+'</ul><p><strong>Technologies:</strong> '+escape(tags)+'</p></article>')
parts.append('<h2>Technical Skills</h2>')
for title,body in re.findall(r'<h3>(.*?)</h3>(.*?)(?=</div>\s*</div>)',section('skills'),re.S):
    tags=', '.join(clean(t) for t in re.findall(r'<span class="tag">(.*?)</span>',body))
    parts.append('<p><strong>'+escape(clean(title))+':</strong> '+escape(tags)+'</p>')
parts.append('<h2>Education and Credentials</h2>')
for date,role,description,tail in entries('education'):
    parts.append('<article><h3>'+escape(clean(role))+'</h3><p>'+escape(clean(description))+' | '+escape(clean(date))+'</p></article>')
body='\n'.join(parts)
head='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Burak Hamuryen — Résumé | Senior Software Engineer</title><meta name="description" content="Professional résumé of Burak Hamuryen: senior software engineering experience, distributed systems, cloud infrastructure, technical skills, and education."><link rel="canonical" href="https://hamuryen.com/resume.html"><link rel="icon" href="favicon.ico"><link rel="stylesheet" href="assets/resume.css"></head><body><nav aria-label="Résumé navigation"><a href="index.html">Back to portfolio</a><a href="burak-hamuryen-resume.pdf" download>Download PDF</a><a href="burak-hamuryen-resume.txt" download>Plain text</a></nav><main>'''
(ROOT/'resume.html').write_text(head+body+'</main></body></html>')
text=re.sub(r'</(?:h[123]|p|li|article)>','\n\n',body)
text=re.sub('<li>','- ',text)
text=re.sub('<br>','\n',text)
text=unescape(re.sub('<[^>]+>','',text))
text=re.sub(r'\n{3,}', '\n\n', text)
(ROOT/'burak-hamuryen-resume.txt').write_text(text.strip()+'\n')
print('Generated resume.html and burak-hamuryen-resume.txt')
