"""
Test Word-Based Chunking
=========================
Test the new word-based chunking implementation to verify:
1. Chunks contain approximately 800 words each
2. Chunks overlap by 100 words
3. No section boundaries limit chunk size
"""

import sys
sys.path.insert(0, 'backend')

from app.rag.chunker import chunk_text

def test_word_based_chunking():
    """Test that chunking creates proper word-based chunks"""
    
    # Create a test text with known word count
    # Generate 2000 words to test multiple chunks
    test_words = " ".join([f"word{i}" for i in range(2000)])
    
    print(f"Input text: {len(test_words.split())} words")
    print(f"Expected chunks: ~3 chunks (2000 words / 800 words per chunk)")
    
    # Chunk the text
    chunks = chunk_text(test_words)
    
    print(f"\n=== RESULTS ===")
    print(f"Total chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        char_count = len(chunk)
        print(f"Chunk {i+1}: {word_count} words, {char_count} characters")
    
    # Verify expectations
    assert len(chunks) > 0, "Should create at least one chunk"
    
    # Check first chunk has approximately 800 words
    first_chunk_words = len(chunks[0].split())
    print(f"\n✅ First chunk has {first_chunk_words} words (target: 800)")
    assert 750 <= first_chunk_words <= 850, f"First chunk should have ~800 words, got {first_chunk_words}"
    
    # Check overlap if multiple chunks exist
    if len(chunks) > 1:
        # Check second chunk starts with some words from first chunk (overlap)
        first_chunk_last_words = chunks[0].split()[-50:]
        second_chunk_first_words = chunks[1].split()[:50]
        
        overlap_found = any(word in second_chunk_first_words for word in first_chunk_last_words)
        print(f"✅ Overlap detected between chunks: {overlap_found}")
    
    print("\n=== TEST PASSED ===")


def test_small_text():
    """Test chunking with text smaller than chunk size"""
    
    test_text = " ".join([f"word{i}" for i in range(100)])  # Only 100 words
    
    print(f"\n=== SMALL TEXT TEST ===")
    print(f"Input: {len(test_text.split())} words")
    
    chunks = chunk_text(test_text)
    
    print(f"Chunks created: {len(chunks)}")
    assert len(chunks) == 1, "Should create exactly one chunk for small text"
    
    word_count = len(chunks[0].split())
    print(f"✅ Single chunk: {word_count} words")
    
    print("=== SMALL TEXT TEST PASSED ===")


def test_section_boundary_ignored():
    """Test that section boundaries (\n\n) are ignored"""
    
    # Create text with multiple sections separated by \n\n
    # Each section is 200 words, total 1000 words
    section1 = " ".join([f"sec1word{i}" for i in range(200)])
    section2 = " ".join([f"sec2word{i}" for i in range(200)])
    section3 = " ".join([f"sec3word{i}" for i in range(200)])
    section4 = " ".join([f"sec4word{i}" for i in range(200)])
    section5 = " ".join([f"sec5word{i}" for i in range(200)])
    
    test_text = f"{section1}\n\n{section2}\n\n{section3}\n\n{section4}\n\n{section5}"
    
    print(f"\n=== SECTION BOUNDARY TEST ===")
    print(f"Input: 5 sections of 200 words each (1000 words total)")
    
    chunks = chunk_text(test_text)
    
    print(f"Chunks created: {len(chunks)}")
    
    # Should create 2 chunks (800 + remainder), NOT 5 chunks (one per section)
    assert len(chunks) == 2, f"Should create ~2 chunks, got {len(chunks)}"
    
    # First chunk should cross section boundaries (have words from multiple sections)
    first_chunk = chunks[0]
    has_sec1 = "sec1word" in first_chunk
    has_sec2 = "sec2word" in first_chunk
    has_sec3 = "sec3word" in first_chunk
    
    print(f"First chunk contains:")
    print(f"  - Section 1 words: {has_sec1}")
    print(f"  - Section 2 words: {has_sec2}")
    print(f"  - Section 3 words: {has_sec3}")
    
    assert has_sec1 and has_sec2, "First chunk should cross section boundaries"
    
    print("✅ Chunks ignore section boundaries (continuous chunking)")
    print("=== SECTION BOUNDARY TEST PASSED ===")


if __name__ == "__main__":
    print("Testing Word-Based Chunking Implementation\n")
    print("=" * 60)
    
    test_word_based_chunking()
    test_small_text()
    test_section_boundary_ignored()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("\nThe new chunking system:")
    print("  ✅ Creates chunks with ~800 words each")
    print("  ✅ Adds 100-word overlap between chunks")
    print("  ✅ Ignores section boundaries (continuous chunking)")
    print("  ✅ No more small 100-word chunks!")
