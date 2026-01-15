const axios = require('axios');
const cheerio = require('cheerio');

// ScrapingBee API Configuration
const SCRAPINGBEE_API_KEY = process.env.SCRAPINGBEE_API_KEY || 'CKZJJZGD8EAWSAZCLBC6W0ERTBF1V3EDB1R9GX0B7NQS4PC5DZDH4R56USTQ4Y46PM3XKUC8BPNTAP19';

/**
 * Scrape competitor website and extract insights
 */
const analyzeCompetitor = async (req, res) => {
  try {
    const { brandContext, competitorUrls } = req.body;

    if (!brandContext || !competitorUrls || competitorUrls.length === 0) {
      return res.status(400).json({ 
        msg: 'Brand context and at least one competitor URL required' 
      });
    }

    if (!SCRAPINGBEE_API_KEY) {
      return res.status(500).json({ 
        msg: 'ScrapingBee API key not configured' 
      });
    }

    const insights = [];

    // Scrape each competitor
    for (const url of competitorUrls.slice(0, 3)) { // Limit to 3 competitors
      try {
        // Use ScrapingBee to scrape the website
        const response = await axios.get('https://app.scrapingbee.com/api/v1/', {
          params: {
            api_key: SCRAPINGBEE_API_KEY,
            url: url,
            render_js: 'false',
            premium_proxy: 'false'
          },
          timeout: 30000
        });

        const html = response.data;
        const $ = cheerio.load(html);

        // Extract insights
        const insight = {
          url,
          domain: new URL(url).hostname,
          analysis: extractInsights($, brandContext),
          scrapedAt: new Date()
        };

        insights.push(insight);
      } catch (error) {
        console.error(`Error scraping ${url}:`, error.message);
        insights.push({
          url,
          domain: new URL(url).hostname,
          error: 'Failed to scrape this competitor',
          analysis: null
        });
      }
    }

    // Generate recommendations based on insights
    const recommendations = generateRecommendations(insights, brandContext);

    res.json({
      brandContext,
      insights,
      recommendations,
      analyzedAt: new Date()
    });

  } catch (error) {
    console.error('Competitor analysis error:', error);
    res.status(500).json({ 
      msg: 'Failed to analyze competitors', 
      error: error.message 
    });
  }
};

/**
 * Extract meaningful insights from scraped HTML
 */
function extractInsights($, brandContext) {
  // Extract page title and meta description
  const title = $('title').text().trim();
  const metaDescription = $('meta[name="description"]').attr('content') || '';
  
  // Extract all headings (h1, h2, h3)
  const headings = [];
  $('h1, h2, h3').each((i, el) => {
    const text = $(el).text().trim();
    if (text && text.length > 3 && text.length < 200) {
      headings.push(text);
    }
  });

  // Extract main content text (first 2000 chars)
  let mainText = '';
  $('p, article, main').each((i, el) => {
    const text = $(el).text().trim();
    if (text) mainText += text + ' ';
  });
  mainText = mainText.slice(0, 2000).trim();

  // Extract keywords from content
  const keywords = extractKeywords(mainText + ' ' + headings.join(' '));

  // Extract pricing indicators
  const pricingIndicators = [];
  $('body').find('*').each((i, el) => {
    const text = $(el).text();
    if (text.match(/\$\d+|\d+\s*(dollars|USD|EUR|price|cost)/i)) {
      const priceText = text.trim().slice(0, 100);
      if (priceText && !pricingIndicators.includes(priceText)) {
        pricingIndicators.push(priceText);
      }
    }
  });

  // Extract value propositions (text near buttons/CTAs)
  const valueProps = [];
  $('button, .cta, .hero, .value-prop, [class*="benefit"]').each((i, el) => {
    const text = $(el).text().trim();
    if (text && text.length > 10 && text.length < 150) {
      valueProps.push(text);
    }
  });

  // Extract testimonials/social proof
  const testimonials = [];
  $('[class*="testimonial"], [class*="review"], [class*="feedback"]').each((i, el) => {
    const text = $(el).text().trim();
    if (text && text.length > 20 && text.length < 300) {
      testimonials.push(text);
    }
  });

  // Analyze design elements
  const designElements = {
    hasVideo: $('video, iframe[src*="youtube"], iframe[src*="vimeo"]').length > 0,
    hasImages: $('img').length,
    hasCTA: $('button, [class*="cta"]').length,
    colorScheme: extractColors($),
    layout: analyzeLayout($)
  };

  return {
    title,
    metaDescription,
    headings: headings.slice(0, 10),
    keywords: keywords.slice(0, 20),
    valuePropositions: valueProps.slice(0, 5),
    pricingInfo: pricingIndicators.slice(0, 5),
    testimonials: testimonials.slice(0, 3),
    designElements,
    contentLength: mainText.length,
    wordCount: mainText.split(/\s+/).length
  };
}

/**
 * Extract top keywords from text
 */
function extractKeywords(text) {
  // Common stop words to filter out
  const stopWords = new Set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
  ]);

  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3 && !stopWords.has(word));

  // Count word frequency
  const wordCount = {};
  words.forEach(word => {
    wordCount[word] = (wordCount[word] || 0) + 1;
  });

  // Sort by frequency
  return Object.entries(wordCount)
    .sort((a, b) => b[1] - a[1])
    .map(([word]) => word);
}

/**
 * Extract color scheme from inline styles
 */
function extractColors($) {
  const colors = new Set();
  
  $('[style*="color"], [style*="background"]').each((i, el) => {
    const style = $(el).attr('style') || '';
    const colorMatches = style.match(/#[0-9a-f]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)/gi);
    if (colorMatches) {
      colorMatches.forEach(color => colors.add(color));
    }
  });

  return Array.from(colors).slice(0, 10);
}

/**
 * Analyze page layout structure
 */
function analyzeLayout($) {
  return {
    hasHeader: $('header, [role="banner"]').length > 0,
    hasNav: $('nav, [role="navigation"]').length > 0,
    hasFooter: $('footer, [role="contentinfo"]').length > 0,
    hasSidebar: $('aside, .sidebar').length > 0,
    sections: $('section, [role="region"]').length
  };
}

/**
 * Generate actionable recommendations
 */
function generateRecommendations(insights, brandContext) {
  const recommendations = [];
  
  const validInsights = insights.filter(i => i.analysis && !i.error);
  
  if (validInsights.length === 0) {
    return ['Unable to generate recommendations due to scraping errors'];
  }

  // Aggregate data
  const allKeywords = [];
  const allValueProps = [];
  let totalHasVideo = 0;
  let totalCTAs = 0;

  validInsights.forEach(insight => {
    if (insight.analysis) {
      allKeywords.push(...(insight.analysis.keywords || []));
      allValueProps.push(...(insight.analysis.valuePropositions || []));
      if (insight.analysis.designElements?.hasVideo) totalHasVideo++;
      totalCTAs += insight.analysis.designElements?.hasCTA || 0;
    }
  });

  // Keyword recommendations
  const topKeywords = [...new Set(allKeywords)].slice(0, 10);
  if (topKeywords.length > 0) {
    recommendations.push({
      category: 'Content Strategy',
      title: 'Leverage Competitor Keywords',
      insight: `Your competitors are focusing on: ${topKeywords.slice(0, 5).join(', ')}`,
      action: `Consider incorporating these keywords into your content strategy to improve SEO and resonate with your target audience.`,
      priority: 'high'
    });
  }

  // Video usage recommendation
  if (totalHasVideo > validInsights.length / 2) {
    recommendations.push({
      category: 'Media Strategy',
      title: 'Video Content Opportunity',
      insight: `${Math.round((totalHasVideo / validInsights.length) * 100)}% of analyzed competitors use video content`,
      action: 'Consider adding product demos, explainer videos, or customer testimonials to increase engagement.',
      priority: 'medium'
    });
  }

  // Value proposition recommendations
  if (allValueProps.length > 0) {
    recommendations.push({
      category: 'Messaging',
      title: 'Strengthen Your Value Proposition',
      insight: 'Competitors are emphasizing clear benefits and outcomes',
      action: `Ensure your messaging clearly communicates unique value. Consider A/B testing different value propositions.`,
      priority: 'high'
    });
  }

  // Design recommendations
  const avgCTAs = totalCTAs / validInsights.length;
  if (avgCTAs > 5) {
    recommendations.push({
      category: 'Conversion Optimization',
      title: 'Multiple Call-to-Actions',
      insight: `Competitors average ${Math.round(avgCTAs)} CTAs per page`,
      action: 'Strategically place CTAs throughout your page to guide users toward conversion.',
      priority: 'medium'
    });
  }

  // Social proof recommendation
  const withTestimonials = validInsights.filter(
    i => i.analysis?.testimonials?.length > 0
  ).length;
  
  if (withTestimonials > 0) {
    recommendations.push({
      category: 'Trust Building',
      title: 'Add Social Proof',
      insight: `${Math.round((withTestimonials / validInsights.length) * 100)}% of competitors display customer testimonials`,
      action: 'Showcase customer reviews, case studies, or trust badges to build credibility.',
      priority: 'high'
    });
  }

  // Content depth recommendation
  const avgWordCount = validInsights.reduce((sum, i) => 
    sum + (i.analysis?.wordCount || 0), 0) / validInsights.length;
  
  if (avgWordCount > 500) {
    recommendations.push({
      category: 'Content Quality',
      title: 'Comprehensive Content',
      insight: `Competitors provide detailed content (avg ${Math.round(avgWordCount)} words)`,
      action: 'Create in-depth, valuable content that addresses user pain points and questions.',
      priority: 'medium'
    });
  }

  return recommendations;
}

module.exports = { analyzeCompetitor };
