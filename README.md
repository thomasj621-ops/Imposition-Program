# Imposition-Program

Basic imposition software designed for a 1-Up Standard Saddle-Stitch Signature layout. Inputs a PDF, outputs a PDF, and includes an optional preview.

## HOW TO USE

Run with the command:

```bash
python impose.py [PDF file]
```

Your PDF file should have a `.pdf` suffix.

- If your document is at least **32 pages** long, the program will prompt you for a signature size (recommended: **16, 20, 24, or 32**).
- If it is fewer than **32 pages**, the program will prompt for permission to impose the entire document as a single signature.
- If the number of pages is not a multiple of your signature size, the program will insert blank pages as padding and ask how you would like to distribute them:
  - Beginning
  - End
  - Split (recommended)
- After these steps, the program prints a summary and asks for confirmation. Entering `N` or `n` terminates the program.
- If you continue, the program generates an imposed copy of your document in your current working directory.
- After the output file is created, the program offers to render a preview.
- If you answer `Y` or `y`, it renders the preview, printing:

```
Rendering Page (page number) of (total pages in original document)...
```

for each rendered page.

When rendering is complete, a separate preview window opens showing:

- **Print Order:** The front and back of every sheet (4 document pages per sheet, 2 per side).
- **Folded View:** A visualization of the finished folded pamphlet.

The terminal becomes usable again after the preview window is closed.

## Example

```text
$ python3 impose.py test.pdf

Reading: test.pdf

Signature setup:
Recommended signature sizes: 16, 20, 24, 28, 32
Pages per signature [28]: 16

You need 2 blank pages.
How would you like to distribute them?
1) End only
2) Beginning only
3) Split between front and back (recommended)

Choice [3]: 3

==================================================

Input file:         test.pdf
Total pages:        34
Final pages:        36
Blank pages:        2
Signature size:     16
Signatures:         3

Breakdown:
Signature 1: 1-16
Signature 2: 17-32
Signature 3: 33-48

==================================================

Continue? [Y/n]: y
Generating imposed PDF...
Processing signature 1...
Processing signature 2...
Processing signature 3...

Done!

Output written to: test-imposed.pdf

============================================================
PRINTING INSTRUCTIONS
============================================================
PRINTER SETTINGS:
- Double-sided printing: ON
- Flip: SHORT EDGE (IMPORTANT)
- Scale: 100% (DO NOT 'Fit to page')
- Collation: OFF

BINDING INSTRUCTIONS:
- Fold each of the signatures carefully
- Keep signatures in order: 1 (outer) → last (inner)
- Stack in correct sequence before sewing or binding

WARNING:
- If pages appear reversed, check SHORT EDGE setting
- If pages are upside down, printer orientation is wrong
- Do NOT scale or auto-fit pages

===========================================================

Would you like to render a preview of your pamphlet? [Y/n]: y
Opening layout preview window... (Close window to return to terminal)
Preparing visual preview window...
Rendering Page 1 of 34...
Rendering Page 2 of 34...
Rendering Page 3 of 34...
Rendering Page 4 of 34...
Rendering Page 5 of 34...
Rendering Page 6 of 34...
Rendering Page 7 of 34...
Rendering Page 8 of 34...
Rendering Page 9 of 34...
Rendering Page 10 of 34...
Rendering Page 11 of 34...
Rendering Page 12 of 34...
Rendering Page 13 of 34...
Rendering Page 14 of 34...
Rendering Page 15 of 34...
Rendering Page 16 of 34...
Rendering Page 17 of 34...
Rendering Page 18 of 34...
Rendering Page 19 of 34...
Rendering Page 20 of 34...
Rendering Page 21 of 34...
Rendering Page 22 of 34...
Rendering Page 23 of 34...
Rendering Page 24 of 34...
Rendering Page 25 of 34...
Rendering Page 26 of 34...
Rendering Page 27 of 34...
Rendering Page 28 of 34...
Rendering Page 29 of 34...
Rendering Page 30 of 34...
Rendering Page 31 of 34...
Rendering Page 32 of 34...
Rendering Page 33 of 34...
Rendering Page 34 of 34...
Rendering complete! Opening Window...
```

# Comments

This was a fun project. It took me a couple of days with the help of ChatGPT and Google Gemini.

I decided to write this program because I recently got into bookbinding. My first project was a simple saddle-stitched booklet so I could have a printed copy of *Paganini's 24 Caprices* without buying a bound edition. After that project, I wanted to bind my 109-page digital journal from last year.

At first, I tried printing it using my printer's built-in "2 pages per sheet" option with double-sided printing (flip on the long edge). As you might expect, the page order was completely wrong. Fortunately, I caught the mistake immediately and worked out the correct imposition order for a small 12-page document. After bringing that problem to ChatGPT, I discovered the world of **imposition**.

Initially, I assumed I could simply enter a custom page sequence into my Chromebook's print dialog. I also didn't want to manually write out the page order for a 109-page document, so I figured I'd write a quick script to generate it. Before starting, I tested whether the print dialog even accepted page sequences. It didn't.

By that point I was already excited to build the tool anyway, so I continued. Working with both ChatGPT and Google Gemini, I gradually developed the program into something much closer to what I had originally envisioned.

I'm really happy with how it turned out. In the future, I may expand it to support additional imposition layouts beyond standard saddle stitching for other bookbinding projects.
