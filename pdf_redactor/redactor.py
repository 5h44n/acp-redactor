import pymupdf
import uuid
from tqdm import tqdm

class Redactor:
    def __init__(self, input_file, redact_list):
        self.input_file = input_file
        self.redact_list = redact_list

    def clean_pdf(self):
        doc = pymupdf.open(self.input_file)
        cleaned_file = f"{self.input_file.rsplit('.', 1)[0]}_cleaned.pdf"
        doc.save(cleaned_file, clean=True)
        doc.close()
        return cleaned_file

    def redact(self):
        cleaned_file = self.clean_pdf()
        doc = pymupdf.open(cleaned_file)
        total_pages = len(doc)

        with tqdm(total=total_pages, desc="Redacting PDF") as pbar:
            for page_num in range(total_pages):
                page = doc[page_num]
                for text in self.redact_list:
                    instances = page.search_for(text)
                    for inst in instances:
                        # Draw a black rectangle over the text
                        page.draw_rect(inst, color=(0, 0, 0), fill=(0, 0, 0))
                        # Optionally, add some padding to the rectangle:
                        # padded_inst = pymupdf.Rect(inst.x0-2, inst.y0-2, inst.x1+2, inst.y1+2)
                        # page.draw_rect(padded_inst, color=(0, 0, 0), fill=(0, 0, 0))
                pbar.update(1)

        output_file = f"{self.input_file.rsplit('.', 1)[0]}_redacted_{uuid.uuid4()}.pdf"
        doc.save(output_file)
        doc.close()
        return output_file