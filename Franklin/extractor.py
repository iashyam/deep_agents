import pymupdf4llm
import json

pymupdf4llm.use_layout = False
loader = pymupdf4llm.to_json('docs/ohm.pdf', page_chunks=True, write_images=True)
print(json.loads(loader).keys())
exit()
for i, loader in enumerate(loader):
    print(loader['image'])
