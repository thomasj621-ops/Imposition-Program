# Imposition-Program
Basic imposition software designed for a 1-Up Standard Saddle-Stitch Signature layout. Inputs a PDF, outputs a PDF, and includes an optional preview.

# HOW TO USE
Run with the command:
python impose.py [PDF file]
Your PDF file should have a .pdf suffix.
If your document is at least 32 pages long, the program will prompt you for a signature size (recommended 16, 20, 24, 32).
If it is less than 32 pages, the program will prompt for permission to impose with a single signature for your whole document.
If your the number of pages in your document is not a multiple of your signature size, the program will insert blank pages as padding and prompt you for how to distribute them (Beginning, End, or Split).
After these steps, the program will print out a summary and ask for confirmation. The program will terminate if you enter N/n.
When you continue, the program will output an imposed copy of your document into your current working directory.
After outputting a file, the program will offer to render a preview.
If you answer Y/y, it will render the preview, printing "rendering page (page number) out of (total pages in original document)" for each rendering page.
When it is finished, it will render a visual in a separate window that shows:
- Print Order: The front and back of each sheet of paper, given each sheet has four pages (2 per side)
- Folded View: How it will look as a finished pamphlet.
The terminal will return to usable once the preview window is closed.

For Example:

{EXAMPLE BEGIN}
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
Input file:        test.pdf
Total pages:       34
Final pages:       36
Blank pages:       2
Signature size:    16
Signatures:        3

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

============================================================

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

{EXAMPLE END}


# COMMENTS
This was a fun project. It took me a couple of days with the help of ChatGPT and Google Gemini. I decided to write this program because I just got into bookbinding. I started with a straight stitch project so I could have a book of Paganini 24 Caprices without having to buy it as a book. Because that first project was really fun, I decided that I wanted to bind my 109-page digital journal from last year, so I printed it out with the settings of two pages (of the document) per page (of the print) and double sided (flip on long end). You can imagine how that turned out. Thankfully, I immediately saw that the page order was completely messed up and determined the printing page order for a 12 page document, and, taking it to ChatGPT, I was introduced to the world of Imposition. Naturally, I thought that I could type in a page sequence into my chromebook's print preview and it would print in that order, and Naturally, I didn't want to write out the new order of a 109 page document. So, I thought to write a quick, simple script to do it for me. It was then that I thought to test whether the print preview takes sequences. It didn't. I was still in the mood to write a script, so I worked with AI (ChatGPT and Google Gemini) to write a script, trying to get as close as I could to what I envisioned. I'm pretty happy with how it turned out. I may end up expanding it to work for all imposition types for future bookbinding projects.
