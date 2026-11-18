"""Assemble the inspected slide renderings into the canonical projection PDF."""
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
images=sorted((ROOT/'data/work/presentation').glob('slide-??.png'))
if len(images)!=29:
    raise ValueError('Expected 25 main slides and four backups')
doc=fitz.open()
for image in images:
    page=doc.new_page(width=960,height=540)
    page.insert_image(page.rect,filename=str(image))
doc.set_metadata({'title':'Climate change and nutritional security - Earth 616','author':'Mahtele, Patel, Puri, Lohare','subject':'20 minute professor presentation: metrics, overall trends and focused results; four backup slides'})
doc.save(ROOT/'docs/final_slides.pdf',garbage=4,deflate=True)
print('Slide PDF: 29 pages, 16:9; charts/text remain editable in the PowerPoint.')
