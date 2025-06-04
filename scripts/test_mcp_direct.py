#!/usr/bin/env python3
"""
Simple direct test for MCP adapter functionality
"""
import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_adapter import (
    generate_context_id, 
    execute_text_summarizer,
    execute_sentiment_analyzer,
    execute_extraction
)

async def test_context_id_generation():
    """Test context ID generation"""
    print("Testing context ID generation...")
    context_id = generate_context_id("test")
    print(f"Generated ID: {context_id}")
    
    # Verify format: prefix-timestamp-uuid
    parts = context_id.split("-")
    assert parts[0] == "test"
    assert len(parts) >= 3
    
    # Verify timestamp part
    current_date = datetime.now().strftime("%Y%m%d")
    assert current_date in parts[1]
    
    print("✅ Context ID generation test passed")

async def test_text_summarizer():
    """Test text summarizer tool"""
    print("\nTesting text summarizer...")
    
    # Test with short text (should return as-is)
    short_text = "This is a short text."
    short_result = await execute_text_summarizer({"text": short_text})
    print(f"Short text summary: {short_result['summary']}")
    assert short_result["summary"] == short_text
    
    # Test with longer text (should be summarized)
    long_text = "This is a much longer text that contains multiple sentences. " \
                "It has information spread across these sentences. " \
                "The summarizer should extract the most important parts."
    long_result = await execute_text_summarizer({"text": long_text, "max_length": 30})
    print(f"Long text summary: {long_result['summary']}")
    assert len(long_result["summary"]) <= 33  # 30 + "..."
    
    print("✅ Text summarizer test passed")

async def test_sentiment_analyzer():
    """Test sentiment analyzer tool"""
    print("\nTesting sentiment analyzer...")
    
    # Test positive sentiment
    positive_text = "I love this product! It's amazing and wonderful."
    positive_result = await execute_sentiment_analyzer({"text": positive_text})
    print(f"Positive text sentiment: {positive_result['sentiment']} (score: {positive_result['score']})")
    assert positive_result["sentiment"] == "positive"
    assert positive_result["score"] > 0
    
    # Test negative sentiment
    negative_text = "This is terrible. I hate it and it's the worst."
    negative_result = await execute_sentiment_analyzer({"text": negative_text})
    print(f"Negative text sentiment: {negative_result['sentiment']} (score: {negative_result['score']})")
    assert negative_result["sentiment"] == "negative"
    assert negative_result["score"] < 0
    
    # Test neutral sentiment
    neutral_text = "This is a regular text with no strong emotions."
    neutral_result = await execute_sentiment_analyzer({"text": neutral_text})
    print(f"Neutral text sentiment: {neutral_result['sentiment']} (score: {neutral_result['score']})")
    
    print("✅ Sentiment analyzer test passed")

async def test_extraction():
    """Test extraction tool"""
    print("\nTesting extraction tool...")
    
    # Test entity extraction
    entity_text = "John Smith visited New York with Mary Johnson."
    entity_result = await execute_extraction({"text": entity_text, "type": "entities"})
    print(f"Extracted entities: {entity_result['entities']}")
    assert "John" in entity_result["entities"]
    assert "Smith" in entity_result["entities"]
    assert "New" in entity_result["entities"]
    assert "York" in entity_result["entities"]
    assert "Mary" in entity_result["entities"]
    # Check if Johnson (with or without period) is in entities
    johnson_found = False
    for entity in entity_result["entities"]:
        if entity.startswith("Johnson"):
            johnson_found = True
            break
    assert johnson_found, "Johnson not found in entities"
    
    # Test keyword extraction
    keyword_text = "Artificial intelligence and machine learning are transforming technology."
    keyword_result = await execute_extraction({"text": keyword_text, "type": "keywords"})
    print(f"Extracted keywords: {keyword_result['keywords']}")
    assert "artificial" in keyword_result["keywords"]
    assert "intelligence" in keyword_result["keywords"]
    assert "machine" in keyword_result["keywords"]
    assert "learning" in keyword_result["keywords"]
    assert "transforming" in keyword_result["keywords"]
    
    # Check for technology with or without period
    technology_found = False
    for keyword in keyword_result["keywords"]:
        if keyword.startswith("technology"):
            technology_found = True
            break
    assert technology_found, "Technology not found in keywords"
    
    print("✅ Extraction test passed")

async def main():
    """Run all tests"""
    print("===== MCP Adapter Direct Tests =====")
    
    await test_context_id_generation()
    await test_text_summarizer()
    await test_sentiment_analyzer()
    await test_extraction()
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
