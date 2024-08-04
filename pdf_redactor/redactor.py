import pymupdf

class Redactor:
    def __init__(self, input_file, redact_list):
        self.input_file = input_file
        self.redact_list = redact_list

    def redact(self) -> str:
        pymupdf.TOOLS.set_small_glyph_heights(True)

        src_doc = pymupdf.open(self.input_file)
        cleaned_file = self.clean(src_doc)
        cleaned_doc = pymupdf.open(cleaned_file)

        try:
            for page in cleaned_doc:
                for text in self.redact_list:
                    areas = page.search_for(text)
                    for hit in areas:
                        page.add_redact_annot(hit, fill=(0, 0, 0))
                page.apply_redactions()

        except Exception as e:
            print(f"Error: {e}")
            return

        output_file = f"{self.input_file.rsplit('.', 1)[0]}_redacted.pdf"
        cleaned_doc.save(output_file, garbage=4, deflate=True)
        cleaned_doc.close()

        return output_file
    
    def clean(self, src_doc) -> str:
        output_file = f"{self.input_file.rsplit('.', 1)[0]}_cleaned.pdf"
        src_doc.save(output_file, garbage=4, deflate=True)
        
        return output_file
