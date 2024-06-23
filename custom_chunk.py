import fitz  # PyMuPDF library

def process_text_block(text):
    """
    Process a block of text to handle double spaces and remove extra spaces within words.
    
    Parameters:
    text (str): The text block to be processed.

    Returns:
    str: The processed text with cleaned spaces.
    """
    if "  " in text:  # Check if double spaces are present
        # Split by double spaces
        words = text.split("  ")
        
        # Remove any spacing within each word
        cleaned_words = [''.join(word.split()) for word in words]
        
        # Join the words with single spaces
        return ' '.join(cleaned_words)
    else:
        return text

def process_page(page):
    """
    Process a page to extract and clean text blocks.
    
    Parameters:
    page: The page object from PyMuPDF.

    Returns:
    str: The processed text for the page.
    """
    # Get text blocks from the page
    text_blocks = page.get_text("blocks")
    processed_blocks = []
    
    for text_block in text_blocks:
        # Get the 4th index (5th element) of the text block
        raw_text = text_block[4]
        # Process the raw text block
        processed_text = process_text_block(raw_text)
        if processed_text:  # Only add non-empty strings
            processed_blocks.append(processed_text)
    
    # Join all processed blocks into a single string
    return ' '.join(processed_blocks).strip()

def custom_text_splitter(pages, chunk_size=2048, overlap=128):
    """
    Split text into chunks with a specified size and overlap.
    
    Parameters:
    pages (list of tuples): List of tuples containing page numbers and their text content.
    chunk_size (int): The maximum size of each chunk.
    overlap (int): The number of characters to overlap between chunks.

    Returns:
    list of tuples: List of tuples containing chunks and their associated page numbers.
    """
    chunks = []
    current_chunk = ""
    current_pages = []

    for page_num, page_content in pages:
        words = page_content.split()
        for word in words:
            # Check if adding the next word exceeds the chunk size
            if len(current_chunk) + len(word) + 1 > chunk_size:
                # Append the current chunk to the list
                chunks.append((current_chunk.strip(), current_pages))
                
                # Prepare the overlap for the next chunk
                overlap_words = current_chunk.split()[-overlap:]
                overlap_text = " ".join(overlap_words)
                
                # Start the new chunk with the overlap
                current_chunk = overlap_text + " " + word
                current_pages = [current_pages[-1]]  # Keep the last page number
            else:
                current_chunk += word + " "
            
            if page_num not in current_pages:
                current_pages.append(page_num)

    # Add the last chunk if there's any remaining text
    if current_chunk:
        chunks.append((current_chunk.strip(), current_pages))

    return chunks

def process_document(pdf_path, chunk_size=2048, overlap_size=128):
    """
    Process a document to extract text and split it into chunks.
    
    Parameters:
    pdf_path (str): The path to the PDF file.
    chunk_size (int): The maximum size of each chunk.
    overlap_size (int): The number of characters to overlap between chunks.

    Returns:
    list of tuples: List of tuples containing chunks and their associated page numbers.
    """
    # Open the PDF document
    doc = fitz.open(pdf_path)
    processed_pages = []
    for page in doc:
        # Process each page and append the results
        page_content = process_page(page)
        processed_pages.append((page.number + 1, page_content))

    # Split the processed text into chunks
    return custom_text_splitter(processed_pages, chunk_size, overlap_size)
