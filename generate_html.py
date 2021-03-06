import bibtexparser
from bibtexparser.bwriter import BibTexWriter

def entry_sort_key(entry):
    l = entry['link']
    if l.find('arxiv') != -1:
        return int(l.rsplit('/',1)[1][:4]) #arxiv year-month
    else:
        return int(entry['year'][2:])*100
        
def normalise_name(n):
    p1, p2 = n.split(', ')
    return p2.strip() + " " + p1.strip()

HTML = r"""<a target="_blank" href="{url}">{title}</a>, {authors}, <i>{journal}</i> ({year}). <br><p class="abstract"><b>Abstract:</b> {abstract}</p>"""


def entry_to_html(entry):
    e = bibtexparser.customization.author(entry)
    bibtexparser.customization.convert_to_unicode(entry)
    authors = ""
    if len(e['author'])==1:
        authors = normalise_name(e['author'][0])
    else:
        for a in e['author'][:-2]:
            p1, p2 = a.split(',')
            authors += normalise_name(a) + ", "
        authors += normalise_name(e['author'][-2]) + " and "
        authors += normalise_name(e['author'][-1])
    if 'journal' in entry:
        journal = entry['journal']
    elif 'booktitle' in entry:
        journal = entry['booktitle']
    else:
        journal = entry['note']

    journal = journal.replace('\n', ' ')
    return HTML.format(url = entry['link'], title=entry['title'],
                       authors = authors, journal = journal,
                       year = entry['year'], abstract=entry['abstract'])

def library_to_html(lib):
    entries = [entry_to_html(b) for b in sorted(lib.entries,key=entry_sort_key,reverse=True)]
    output = ""
    for e in entries:
        output += "<li>" + e + "</li>" +"\n"

    return output

def to_clipboard(s):
    try:
        from Tkinter import Tk
    except ImportError:
        from tkinter import Tk
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(s)
    r.update() # now it stays on the clipboard after the window is closed
    r.destroy()

if __name__ == '__main__':
    with open('zx-papers.bib',encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
        bib_data = library_to_html(bib_database)
    with open('html/base_html.html') as f:
        html_base = f.read()
    with open('html/expand.js') as f:
        js_base = f.read()
    output = html_base.format(content=bib_data,javascript=js_base)
    f = open("publications.html",'wb')
    f.write(output.encode('utf-8'))
    f.close()
