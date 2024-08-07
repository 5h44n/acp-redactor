import fitz  # PyMuPDF

class Redactor:
    def __init__(self, input_file, attorney, client):
        self.input_file = input_file
        self.attorney = attorney
        self.client = client

    def redact(self) -> str:
        fitz.TOOLS.set_small_glyph_heights(True)

        src_doc = fitz.open(self.input_file)
        cleaned_file = self.clean(src_doc)
        cleaned_doc = fitz.open(cleaned_file)

        try:
            for page in cleaned_doc:
                page: fitz.Page = page  # typecast for great justice

                # Parse each email in page and apply redaction annotations
                self._process_emails(page)

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

    def _process_emails(self, page):
        email_info_keywords = ["Subject:", "From:", "To:", "Cc:", "Attachments:", "Date Sent:", "Date Received:", "Date:"]
        text = page.get_text("text")
        lines = text.split('\n')

        email_info_lines = []
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in email_info_keywords):
                bbox = self._find_line_bbox(page, line)
                if bbox:
                    email_info_lines.append((i, line, bbox))

        # Group email info lines by line numbers
        email_info_groups = []
        current_group = []

        for i, line, bbox in email_info_lines:
            if not current_group:
                current_group.append((i, line, bbox))
            else:
                if i - current_group[-1][0] <= 1:  # If the lines are consecutive, they belong to the same group
                    current_group.append((i, line, bbox))
                else:
                    email_info_groups.append(current_group)
                    current_group = [(i, line, bbox)]

        if current_group:
            email_info_groups.append(current_group)

        # Process each email info group
        for j, group in enumerate(email_info_groups):
            email_info_texts = [line for _, line, _ in group]
            from_line = next((line for line in email_info_texts if "From:" in line), None)
            to_line = next((line for line in email_info_texts if "To:" in line), None)
            cc_line = next((line for line in email_info_texts if "Cc:" in line), None)

            if from_line and to_line and self._is_valid_email_exchange(from_line, to_line, cc_line):
                redact_start = max(bbox.y1 for _, _, bbox in group)
                if j < len(email_info_groups) - 1:
                    next_group_start = email_info_groups[j + 1][0][2].y0
                    redact_end = next_group_start
                else:
                    redact_end = page.rect.height
                self._redact_area(page, redact_start, redact_end)

    def _find_line_bbox(self, page, line):
        """Find the bounding box of a line in the page."""
        areas = page.search_for(line)
        if areas:
            return areas[0]
        return None

    def _is_valid_email_exchange(self, from_line, to_line, cc_line):
        emails = [self.attorney, self.client]
        # Extract emails from lines
        from_emails = [email.strip().split('<')[-1].replace('>', '') for email in from_line.split(':', 1)[1].split(',')]
        to_emails = [email.strip().split('<')[-1].replace('>', '') for email in to_line.split(':', 1)[1].split(',')]
        cc_emails = [email.strip().split('<')[-1].replace('>', '') for email in cc_line.split(':', 1)[1].split(',')] if cc_line else []

        all_emails = set(from_emails + to_emails + cc_emails)

        result = all(email in emails for email in all_emails) and (self.attorney in all_emails and self.client in all_emails)

        print(f"Emails: {all_emails} - {result}")

        return result

    def _redact_area(self, page, redact_start, redact_end):
        """Redact a rectangular area from y0 to y1 on the page."""
        rect = fitz.Rect(0, redact_start, page.rect.width, redact_end)
        print(f"Redacting area: {rect}")
        page.add_redact_annot(rect, fill=(0, 0, 0))
