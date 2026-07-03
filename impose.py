#!/usr/bin/env python3

import sys
import math
from copy import deepcopy
from pypdf import PdfReader, PdfWriter
import tkinter as tk
from tkinter import ttk

#Chunk 2:


def pad_page_count(total_pages: int):
    """
    Pads total pages to next multiple of 4.
    Returns (new_total, blank_count)
    """
    remainder = total_pages % 4
    if remainder == 0:
        return total_pages, 0

    blank_needed = 4 - remainder
    return total_pages + blank_needed, blank_needed


def build_signature_order(signature_size: int):
    order = []
    low = 1
    high = signature_size

    # Loop exactly for the number of sheets needed (4 pages per sheet layout)
    for _ in range(signature_size // 4):
        # FRONT spread (outer pages)
        order.append(high)
        order.append(low)

        # BACK spread (inner pages)
        order.append(low + 1)
        order.append(high - 1)

        # Shift bounds cleanly inward
        low += 2
        high -= 2

    return order


def split_into_signatures(total_pages, signature_size):
    # Ensure signature size is a multiple of 4
    if signature_size % 4 != 0:
        signature_size = ((signature_size // 4) + 1) * 4

    # Pad total pages to a multiple of the signature size
    padded_total = ((total_pages + signature_size - 1) // signature_size) * signature_size
    
    # Generate the pristine master print flat order sequence
    flat_order = build_signature_order(signature_size)
    
    signatures = []
    # Step through every full signature group required
    for sig_offset in range(0, padded_total, signature_size):
        sig_pages = []
        for p in flat_order:
            actual_page = sig_offset + p
            # If the page is out of the real PDF boundary, map it as 0 (Blank Pad)
            if actual_page > total_pages:
                sig_pages.append(0)
            else:
                sig_pages.append(actual_page)
        signatures.append(sig_pages)
        
    return signatures


def add_blank_pages(signatures, total_pages, padded_total):
    """
    Replaces page numbers beyond real content with 0 (blank pages).
    We'll interpret 0 later when building PDF.
    """

    result = []

    for sig in signatures:
        new_sig = []
        for p in sig:
            if p > total_pages:
                new_sig.append(0)  # blank page marker
            else:
                new_sig.append(p)
        result.append(new_sig)

    return result


# Chunk 3:

def prompt_int(prompt, default=None):
    """
    Safely prompt for integer input with optional default.
    """
    while True:
        raw = input(f"{prompt}" + (f" [{default}]: " if default else ": ")).strip()

        if raw == "" and default is not None:
            return default

        if raw.isdigit():
            return int(raw)

        print("Please enter a valid number.")


def prompt_yes_no(prompt, default=True):
    """
    Returns True for yes, False for no.
    """
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        raw = input(prompt + suffix).strip().lower()

        if raw == "" and default is not None:
            return default

        if raw in ["y", "yes"]:
            return True
        if raw in ["n", "no"]:
            return False

        print("Please enter y or n.")


def choose_signature_size(total_pages):
    """
    Determines signature size interactively.
    """

    print("\nSignature setup:\n")

    max_size = 32

    if total_pages <= max_size:
        use_single = prompt_yes_no(
            f"\nUse a single signature of {total_pages} pages?", True
        )
        if use_single:
            return total_pages

    print("\nRecommended signature sizes: 16, 20, 24, 28, 32\n")

    size = prompt_int("Pages per signature", default=28)

    if size % 4 != 0:
        print("Warning: signature size should be divisible by 4. Adjusting.")
        size = (size // 4) * 4

    return size


def choose_blank_distribution(blank_count):
    """
    Your requested behavior:
    - front only
    - back only
    - split front/back (default recommended)
    """

    if blank_count == 0:
        return "none"

    print(f"\nYou need {blank_count} blank pages.\n")
    print("How would you like to distribute them?")
    print("1) End only")
    print("2) Beginning only")
    print("3) Split between front and back (recommended)\n")

    choice = input("Choice [3]: ").strip() or "3"

    return {
        "1": "end",
        "2": "start",
        "3": "split"
    }.get(choice, "split")


def print_summary(input_file, total_pages, padded_total,
                  blank_count, signature_size, signatures):

    print("\n" + "=" * 50)
    print(f"Input file:        {input_file}")
    print(f"Total pages:       {total_pages}")
    print(f"Final pages:       {padded_total}")
    print(f"Blank pages:       {blank_count}")
    print(f"Signature size:    {signature_size}")
    print(f"Signatures:        {len(signatures)}")
    print("\nBreakdown:\n")

    for i, sig in enumerate(signatures, 1):
        start = (i - 1) * signature_size + 1
        end = i * signature_size
        print(f"Signature {i}: {start}-{end}")

    print("=" * 50 + "\n")


def confirm_continue():
    return prompt_yes_no("\nContinue?", True)


def build_config(input_file, total_pages):
    """
    Central config builder used by main().
    """

    signature_size = choose_signature_size(total_pages)

    padded_total, blank_count = pad_page_count(total_pages)

    blank_mode = choose_blank_distribution(blank_count)

    signatures = split_into_signatures(padded_total, signature_size)
    signatures = add_blank_pages(signatures, total_pages, padded_total)

    print_summary(
        input_file,
        total_pages,
        padded_total,
        blank_count,
        signature_size,
        signatures
    )

    if not confirm_continue():
        print("Aborted.")
        sys.exit(0)

    return {
        "signature_size": signature_size,
        "padded_total": padded_total,
        "blank_count": blank_count,
        "blank_mode": blank_mode,
        "signatures": signatures
    }

# Chunk 4:


def get_blank_page(writer, width, height):
    """
    Creates a reusable blank page.
    """
    return writer.add_blank_page(width=width, height=height)


def build_imposed_pdf(input_file, config, output_file):
    """
    Converts signature page plan into a real imposed PDF.
    """

    reader = PdfReader(input_file)
    writer = PdfWriter()

    signatures = config["signatures"]

    # Use first page size as reference
    sample_page = reader.pages[0]
    width = float(sample_page.mediabox.width)
    height = float(sample_page.mediabox.height)

    # Pre-create blank page template
    blank_page = None

    print("\nGenerating imposed PDF...\n")

    for s_idx, signature in enumerate(signatures, 1):
        print(f"Processing signature {s_idx}...")

        for p in signature:
            if p == 0:
                # blank page
                if blank_page is None:
                    blank_page = writer.add_blank_page(width=width, height=height)
                    # we don't actually reuse this page directly;
                    # we just use its dimensions

                writer.add_blank_page(width=width, height=height)

            else:
                # convert 1-based → 0-based
                writer.add_page(reader.pages[p - 1])

    with open(output_file, "wb") as f:
        writer.write(f)

def printinstructions():
    print("\n" + "=" * 60)
    print("PRINTING INSTRUCTIONS")
    print("=" * 60)

    print("\nPRINTER SETTINGS:")
    print("- Double-sided printing: ON")
    print("- Flip: SHORT EDGE (IMPORTANT)")
    print("- Scale: 100% (DO NOT 'Fit to page')")
    print("- Collation: OFF\n")

    print("BINDING INSTRUCTIONS:")
    print(f"- Fold each of the signatures carefully")
    print("- Keep signatures in order: 1 (outer) → last (inner)")
    print("- Stack in correct sequence before sewing or binding\n")

    print("WARNING:")
    print("- If pages appear reversed, check SHORT EDGE setting")
    print("- If pages are upside down, printer orientation is wrong")
    print("- Do NOT scale or auto-fit pages\n")

    print("=" * 60 + "\n")

# GUI

from PIL import Image, ImageTk
from pdf2image import convert_from_path

class BookletPreviewer:
    def __init__(self, root, input_file, config):
        self.root = root
        self.input_file = input_file
        self.config = config
        self.signatures = config["signatures"]
        self.signature_size = config["signature_size"]
        
        # UI State
        self.current_view = "print_order"  # "print_order" or "folded"
        self.current_sheet_idx = 0        # For Print Order view

        # --- PDF to Image Conversion ---
        print("Preparing visual preview window...")
        self.pdf_images = []
        try:
            # First, check total pages using our reader instance
            total_pdf_pages = len(PdfReader(input_file).pages)
            
            # Render page by page to show live progress in the terminal
            for page_idx in range(1, total_pdf_pages + 1):
                print(f"Rendering Page {page_idx} of {total_pdf_pages}...")
                self.root.update_idletasks() # Keeps UI stable if needed later
                
                # Convert exactly one page at a time
                single_page_list = convert_from_path(
                    input_file, 
                    first_page=page_idx, 
                    last_page=page_idx
                )
                if single_page_list:
                    self.pdf_images.append(single_page_list[0])
            print("Rendering complete! Opening Window...")
            
        except Exception as e:
            print(f"\n[Visual render engine failed: {e}. Falling back to blank blocks.]")
            self.pdf_images = []

# --- Pre-calculate Reading Order Pairs for Folded View ---
        self.folded_pages = []
        
        real_page_count = len(self.pdf_images)
        
        # FIX: Calculate total booklet pages using the actual padded signature array length
        total_booklet_pages = len(self.signatures) * len(self.signatures[0])
        
        # 1. Front Cover Spread: Outside air (0) paired with Page 1
        self.folded_pages.append((0, 1))
        
        # 2. Inner Spreads & Blank Padding Leaves:
        # Loop sequentially through the internal pairs up to the second-to-last page
        for p in range(2, total_booklet_pages, 2):
            self.folded_pages.append((p, p + 1))
            
        # 3. True Back Cover Realignment:
        # Explicitly append the structural back cover leaf wrap using the true padded endpoint
        self.folded_pages.append((total_booklet_pages, 0))
                
        self.current_fold_idx = 0          # For Folded View tracking

        #--- Group Signatures into 4-Page Printable Sheets ---
        self.sheets = []
        for sig in self.signatures:
            for i in range(0, len(sig), 4):
                # Ensure a full 4-page sheet exists to prevent out-of-index errors
                if i + 3 < len(sig):
                    self.sheets.append({
                        "front_left": sig[i],
                        "front_right": sig[i+1],
                        "back_left": sig[i+2],
                        "back_right": sig[i+3]
                    })

        self.root.title(f"Booklet Preview – {input_file}")
        self.root.geometry("950x700")
        self.root.configure(bg="#f5f5f7")
        
        # Keyboard Event Bindings
        self.root.bind("<Left>", lambda event: self.prev_item())
        self.root.bind("<Right>", lambda event: self.next_item())
        
        self.build_ui()

        self.canvas.bind("<Configure>", lambda event: self.draw_current_view())
        
        self.draw_current_view()

    def build_ui(self):
        # Top Navigation View Bar
        top_bar = tk.Frame(self.root, bg="#ffffff", height=50, bd=1, relief="groove")
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        
        self.btn_print_order = tk.Button(
            top_bar, text="Print Order", font=("Arial", 11, "bold"),
            bd=0, bg="#007aff", fg="#ffffff", padx=15, pady=5,
            command=lambda: self.switch_view("print_order")
        )
        self.btn_print_order.pack(side="left", padx=10, pady=8)
        
        self.btn_folded_view = tk.Button(
            top_bar, text="Folded View", font=("Arial", 11),
            bd=0, bg="#e5e5ea", fg="#000000", padx=15, pady=5,
            command=lambda: self.switch_view("folded")
        )
        self.btn_folded_view.pack(side="left", padx=5, pady=8)

        self.info_lbl = tk.Label(top_bar, font=("Arial", 10), bg="#ffffff", fg="#555555")
        self.info_lbl.pack(side="right", padx=15)

        # Main Layout Container holding Sidebar Left Nav, Canvas, Sidebar Right Nav
        main_layout_frame = tk.Frame(self.root, bg="#f5f5f7")
        main_layout_frame.pack(fill="both", expand=True, side="top")

        # Side Navigation Left Target Button
        self.side_prev_btn = tk.Button(
            main_layout_frame, text="◀", font=("Arial", 22, "bold"),
            bd=0, bg="#f5f5f7", fg="#aaaaaa", activebackground="#e5e5ea",
            command=self.prev_item, width=3
        )
        self.side_prev_btn.pack(side="left", fill="y")

        # Side Navigation Right Target Button
        self.side_next_btn = tk.Button(
            main_layout_frame, text="▶", font=("Arial", 22, "bold"),
            bd=0, bg="#f5f5f7", fg="#aaaaaa", activebackground="#e5e5ea",
            command=self.next_item, width=3
        )
        self.side_next_btn.pack(side="right", fill="y")

        # Visual Drawing Canvas
        self.canvas = tk.Canvas(main_layout_frame, bg="#f5f5f7", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="left")

        # Bottom Bar Status
        self.bottom_bar = tk.Frame(self.root, bg="#ffffff", height=40, bd=1, relief="groove")
        self.bottom_bar.pack(fill="x", side="bottom")
        self.bottom_bar.pack_propagate(False)
        
        self.page_indicator = tk.Label(self.bottom_bar, text="", font=("Arial", 10), bg="#ffffff", fg="#333333")
        self.page_indicator.pack(side="top", pady=8)

    def switch_view(self, view_mode):
        self.current_view = view_mode
        if view_mode == "print_order":
            self.btn_print_order.configure(bg="#007aff", fg="#ffffff", font=("Arial", 11, "bold"))
            self.btn_folded_view.configure(bg="#e5e5ea", fg="#000000", font=("Arial", 11))
        else:
            self.btn_print_order.configure(bg="#e5e5ea", fg="#000000", font=("Arial", 11))
            self.btn_folded_view.configure(bg="#007aff", fg="#ffffff", font=("Arial", 11, "bold"))
        self.draw_current_view()

    def prev_item(self):
        if self.current_view == "print_order":
            if self.current_sheet_idx > 0:
                self.current_sheet_idx -= 1
                self.draw_current_view()
        else:
            if self.current_fold_idx > 0:
                self.current_fold_idx -= 1
                self.draw_current_view()

    def next_item(self):
        if self.current_view == "print_order":
            if self.current_sheet_idx < len(self.sheets) - 1:
                self.current_sheet_idx += 1
                self.draw_current_view()
        else:
            if self.current_fold_idx < len(self.folded_pages) - 1:
                self.current_fold_idx += 1
                self.draw_current_view()

    def get_page_thumbnail(self, page_num, width, height):
        """Extracts and resizes the actual PDF page image if available."""
        # Force width and height to be integers so Pillow doesn't crash
        w_int = int(width)
        h_int = int(height)

        if page_num == 0 or not self.pdf_images or page_num > len(self.pdf_images):
            img = Image.new("RGB", (w_int, h_int), "#ffffff")
            return ImageTk.PhotoImage(img)
        
        orig_img = self.pdf_images[page_num - 1]
        resized = orig_img.resize((w_int, h_int), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized)

    def draw_page_box(self, x, y, width, height, label_top, page_num):
        w_int = int(width)
        h_int = int(height)
        
        # Treat page_num as blank if it's 0 OR if it exceeds our actual rendered PDF images
        if page_num == 0 or page_num > len(self.pdf_images):
            # Draw the blank page precisely like a normal page: clean white background, dark border
            self.canvas.create_rectangle(x, y, x + w_int, y + h_int, fill="#ffffff", outline="#333333", width=2)
            # Add a subtle, clean gray placeholder label in the dead center
            self.canvas.create_text(x + w_int / 2, y + h_int / 2, text="[ Blank ]", font=("Arial", 12, "italic"), fill="#aaaaaa")
            lbl = f"{label_top} [Blank]"
        else:
            # Keeps your pristine live PDF thumbnail page preview code intact!
            tk_img = self.get_page_thumbnail(page_num, w_int, h_int)
            if not hasattr(self, "_cache"):
                self._cache = []
            self._cache.append(tk_img)
            
            self.canvas.create_image(x, y, image=tk_img, anchor="nw")
            self.canvas.create_rectangle(x, y, x + w_int, y + h_int, outline="#333333", width=2)
            lbl = f"{label_top} (p. {page_num})"
        
        # Upper Label tracking top-of-page layout
        self.canvas.create_text(x + w_int / 2, y - 12, text=lbl, font=("Arial", 10, "bold"), fill="#1c1c1e")
        
    def draw_current_view(self):
        self.canvas.delete("all")
        self._cache = [] # Clean image memory buffers
        
        # Measure actual layout area dynamically
        canv_w = self.canvas.winfo_width()
        canv_h = self.canvas.winfo_height()
        
        # Guard clause for initial window drawing lifecycle calculations
        if canv_w < 100 or canv_h < 100:
            return

        if self.current_view == "print_order":
            self.side_prev_btn.configure(fg="#007aff" if self.current_sheet_idx > 0 else "#dddddd")
            self.side_next_btn.configure(fg="#007aff" if self.current_sheet_idx < len(self.sheets) - 1 else "#dddddd")
            
            sheet = self.sheets[self.current_sheet_idx]
            self.info_lbl.configure(text=f"Total Imposed Sheet Plan Layout Profiles")
            self.page_indicator.configure(text=f"Sheet Setup Configuration {self.current_sheet_idx + 1} of {len(self.sheets)}")
            
            # --- Dynamic Split Sizing Layout ---
            half_w = canv_w / 2
            avail_h = canv_h - 130 
            
            # Target width for a dual-page spread on one side
            target_spread_w = half_w - 60
            
            # Maintain a beautiful 1:1.5 standard portrait aspect ratio for booklet leaves
            box_w = min(target_spread_w / 2, avail_h / 1.5)
            box_h = box_w * 1.5
            
            start_y = 55
            
            # Front Layout (Left Half)
            front_center_x = half_w / 2
            fx_left = front_center_x - box_w
            fx_right = front_center_x
            
            self.canvas.create_text(front_center_x, 25, text="FRONT (Outer side Spread)", font=("Arial", 12, "bold"), fill="#222222")
            self.draw_page_box(fx_left, start_y, box_w, box_h, "Left", sheet["front_left"])
            self.draw_page_box(fx_right, start_y, box_w, box_h, "Right", sheet["front_right"])
            self.canvas.create_line(fx_right, start_y, fx_right, start_y + box_h, dash=(4, 4), fill="#007aff", width=1.5)

            # Back Layout (Right Half)
            back_center_x = half_w + (half_w / 2)
            bx_left = back_center_x - box_w
            bx_right = back_center_x
            
            self.canvas.create_text(back_center_x, 25, text="BACK (Inner side Spread)", font=("Arial", 12, "bold"), fill="#222222")
            self.draw_page_box(bx_left, start_y, box_w, box_h, "Left", sheet["back_left"])
            self.draw_page_box(bx_right, start_y, box_w, box_h, "Right", sheet["back_right"])
            self.canvas.create_line(bx_right, start_y, bx_right, start_y + box_h, dash=(4, 4), fill="#007aff", width=1.5)

            # Informational Context Layer Box (Positioned dynamically at the bottom)
            info_y = start_y + box_h + 25
            self.canvas.create_rectangle(40, info_y, canv_w - 40, info_y + 45, fill="#e8f4ff", outline="#b3d7ff", width=1)
            instructions = "🖨️ Printer Target Mode: Double-sided ON  •  Flip on SHORT EDGE  •  Scale 100% (Actual Size Output)"
            self.canvas.create_text(canv_w / 2, info_y + 22, text=instructions, font=("Arial", 10, "bold"), fill="#0056b3")

        elif self.current_view == "folded":
            self.side_prev_btn.configure(fg="#007aff" if self.current_fold_idx > 0 else "#dddddd")
            self.side_next_btn.configure(fg="#007aff" if self.current_fold_idx < len(self.folded_pages) - 1 else "#dddddd")
            
            left_p, right_p = self.folded_pages[self.current_fold_idx]
            self.info_lbl.configure(text="Pamphlet 2D Folded Finished View")
            self.page_indicator.configure(text=f"Fold Spread {self.current_fold_idx + 1} of {len(self.folded_pages)} (Reader Layout)")

            # --- DYNAMIC TITLE LOGIC ---
            total_folds = len(self.folded_pages)
            if self.current_fold_idx == 0:
                title_text = "2D Simulation: Front Cover Layout"
                left_label = ""
                right_label = "Front Cover"
            elif self.current_fold_idx == total_folds - 1:
                title_text = "2D Simulation: Back Cover Layout"
                left_label = "Back Cover"
                right_label = ""
            else:
                title_text = f"2D Simulation: Inner Folded Spread Layout (Spread {self.current_fold_idx} of {total_folds - 2})"
                left_label = "Left Leaf"
                right_label = "Right Leaf"

            # Draw the text using the dynamic variables
            self.canvas.create_text(canv_w / 2, 25, text=title_text, font=("Arial", 13, "bold"), fill="#222222")
            self.canvas.create_text(canv_w / 2, 45, text="Use Left/Right keyboard arrow keys or sidebar arrow elements to flip pages.", font=("Arial", 9), fill="#777777")

            # Calculate dynamic sizes for the folded layout leaf views
            avail_w = canv_w - 100
            avail_h = canv_h - 130

            if left_p == 0 or right_p == 0:
                box_w = min(avail_w, avail_h / 1.5)
            else:
                box_w = min(avail_w / 2, avail_h / 1.5)
                
            box_h = box_w * 1.5
            start_y = 80
            center_x = canv_w / 2

            if "Front Cover" in right_label or "Front Cover" in title_text:
                # FRONT COVER: Always on the right side of the spine
                self.draw_page_box(center_x, start_y, box_w, box_h, right_label, right_p)
                # Spine accents down the middle
                self.canvas.create_line(center_x, start_y, center_x, start_y + box_h, fill="#666666", width=2)
                self.canvas.create_rectangle(center_x, start_y, center_x + 4, start_y + box_h, fill="#444444", stipple="gray25", outline="")

            elif "Back Cover" in left_label or "Back Cover" in title_text:
                # BACK COVER: Always on the left side of the spine
                lx = center_x - box_w
                # Check which variable safely holds the page or blank data
                final_label = left_label if left_label else right_label
                final_p = left_p if left_p != 0 else right_p
                
                self.draw_page_box(lx, start_y, box_w, box_h, final_label, final_p)
                self.canvas.create_line(center_x, start_y, center_x, start_y + box_h, fill="#666666", width=2)
                self.canvas.create_rectangle(center_x - 4, start_y, center_x, start_y + box_h, fill="#444444", stipple="gray25", outline="")

            else:
                # CHRONOLOGICAL OPEN SPREAD
                lx = center_x - box_w
                rx = center_x
                self.draw_page_box(lx, start_y, box_w, box_h, left_label, left_p)
                self.draw_page_box(rx, start_y, box_w, box_h, right_label, right_p)

                self.canvas.create_line(center_x, start_y, center_x, start_y + box_h, fill="#666666", width=2)
                self.canvas.create_rectangle(center_x - 3, start_y, center_x + 3, start_y + box_h, fill="#444444", stipple="gray25", outline="")


import multiprocessing

def launch_gui_process(input_file, config):
    try:
        root = tk.Tk()
        app = BookletPreviewer(root, input_file, config)
        root.mainloop()
    except Exception as e:
        print(f"\n[GUI Error] Could not start window: {e}")

def main_with_preview(input_file, config):
    print("\nOpening layout preview window... (Close window to return to terminal)")
    root = tk.Tk()
    app = BookletPreviewer(root, input_file, config)
    root.mainloop()


#=========================================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 impose.py input.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".pdf", "-imposed.pdf")

    print(f"\nReading: {input_file}\n")

    reader = PdfReader(input_file)
    total_pages = len(reader.pages)

    config = build_config(input_file, total_pages)

    build_imposed_pdf(input_file, config, output_file)

    print(f"\nDone!\nOutput written to: {output_file}\n")

    printinstructions()

    choice = input("Would you like to render a preview of your pamphlet? [Y/n]: ").strip().lower()    
    if choice == '' or choice.startswith('y'):
        main_with_preview(input_file, config)
    elif choice.startswith('n'):
        print("Exiting.")
        sys.exit()
    else:
        print("Invalid input. Exiting.")
        sys.exit()

if __name__ == "__main__":
    main()
