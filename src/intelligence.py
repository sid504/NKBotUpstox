import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from textblob import TextBlob
import datetime

logger = logging.getLogger("Intelligence")

class IntelligenceModule:
    def __init__(self):
        self.news_sources = [
            "https://www.moneycontrol.com/news/business/markets/",
            "https://economictimes.indiatimes.com/markets/stocks/news",
        ]
        self.sentiment_cache = {}

    async def fetch_url(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def analyze_sentiment(self, text):
        """
        Analyze sentiment using TextBlob + Financial Keyword Dictionary.
        """
        if not text:
            return 0.0
            
        text_lower = text.lower()
        score = 0.0
        
        # 1. Financial Keyword Dictionary (The "Edge")
        # Standard NLP often fails on jargon like "Guidance cut" or "Beat estimates"
        keywords = {
            # Positive
            "surge": 0.5, "jump": 0.5, "high": 0.3, "gain": 0.4, "bull": 0.5,
            "buy": 0.4, "outperform": 0.6, "beat": 0.6, "profit": 0.4,
            "upgrade": 0.7, "acquisition": 0.4, "growth": 0.3, "record": 0.5,
            # Negative
            "slump": -0.5, "drop": -0.4, "fall": -0.4, "loss": -0.5, "bear": -0.5,
            "sell": -0.4, "underperform": -0.6, "miss": -0.6, "debt": -0.3,
            "downgrade": -0.7, "lawsuit": -0.8, "investigation": -0.8, "crash": -0.9
        }
        
        # Keyword matching
        for word, val in keywords.items():
            if word in text_lower:
                score += val
        
        # 2. Base NLP (TextBlob) as baseline
        blob_score = TextBlob(text).sentiment.polarity
        
        # Weighted Average: Keywords matter more (70%) than generic NLP (30%)
        final_score = (score * 0.7) + (blob_score * 0.3)
        
        # Clamp between -1 and 1
        return max(-1.0, min(1.0, final_score))

    async def scrape_news(self):
        """
        Scrape news from defined sources and calculate aggregate sentiment.
        """
        logger.info("Scraping news for market sentiment...")
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, url) for url in self.news_sources]
            responses = await asyncio.gather(*tasks)

        headlines = []
        for html in responses:
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # MoneyControl specific parsing (example)
                for item in soup.find_all('h2'):
                    headlines.append(item.get_text().strip())
                # Economic Times specific parsing (example)
                for item in soup.find_all('div', class_='eachStory'):
                     h3 = item.find('h3')
                     if h3:
                         headlines.append(h3.get_text().strip())

        # Filter empty
        headlines = [h for h in headlines if len(h) > 10]
        
        total_sentiment = 0.0
        count = 0
        
        logger.info(f"Found {len(headlines)} headlines.")
        
        for headline in headlines:
            score = self.analyze_sentiment(headline)
            if score != 0:
                total_sentiment += score
                count += 1
                # logger.debug(f"Headline: {headline[:50]}... | Score: {score}")

        market_sentiment = total_sentiment / count if count > 0 else 0.0
        logger.info(f"Market Sentiment Score: {market_sentiment:.4f} (based on {count} headlines)")
        
        return market_sentiment

# Test run
if __name__ == "__main__":
    async def test():
        brain = IntelligenceModule()
        score = await brain.scrape_news()
        print(f"Final Sentiment: {score}")
    
    asyncio.run(test())
