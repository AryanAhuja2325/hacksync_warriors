const Campaign = require("../models/campaign.model");
const { bucket } = require("../config/firebase");
const fs = require("fs");
const axios = require("axios");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const pdfParse = require("pdf-parse");

// Initialize Gemini AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY);

/**
 * Use Gemini to analyze prompt/PDF and generate detailed strategy JSON
 * OPTIMIZED: Extracts PDF text, uses proper multimodal API, returns structured data
 */
async function analyzeWithGemini(promptText, fileBuffer = null) {
  try {
    const model = genAI.getGenerativeModel({ 
      model: "gemini-1.5-flash",
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048,
      }
    });

    let fullPromptText = promptText;
    let isPDF = false;

    // CRITICAL FIX: Extract actual text from PDF if provided
    if (fileBuffer) {
      try {
        console.log('📄 Extracting text from PDF...');
        const pdfData = await pdfParse(fileBuffer);
        const extractedText = pdfData.text.trim();
        
        if (extractedText && extractedText.length > 10) {
          fullPromptText = extractedText;
          isPDF = true;
          console.log(`✅ Extracted ${extractedText.length} characters from PDF`);
          console.log(`📝 First 200 chars: ${extractedText.substring(0, 200)}...`);
        } else {
          console.warn('⚠️ PDF text extraction returned empty or too short, using filename');
        }
      } catch (pdfError) {
        console.error('❌ PDF parsing failed:', pdfError.message);
        console.log('⚠️ Falling back to filename-based analysis');
      }
    }

    const systemPrompt = `You are an expert marketing strategist with deep knowledge of digital marketing, consumer behavior, and campaign planning.

Your task: Analyze the following ${isPDF ? 'PDF document content' : 'user input'} and extract a comprehensive marketing campaign strategy.

${isPDF ? '=== EXTRACTED PDF CONTENT ===' : '=== USER INPUT ==='}
${fullPromptText}
${isPDF ? '=== END PDF CONTENT ===' : '=== END INPUT ==='}

EXTRACT AND STRUCTURE:

1. **Product/Service**: Identify the exact product or service name
2. **Target Audience**: Define WHO would use/buy this (demographics, psychographics, behaviors)
3. **Campaign Goal**: What is the primary objective? (awareness, sales, engagement, launch, etc.)
4. **Brand Tone**: How should the brand communicate? (professional, playful, inspiring, luxurious, etc.)
5. **Platforms**: Which social/digital platforms make sense? (Instagram, TikTok, YouTube, LinkedIn, etc.)
6. **Visual Style**: Describe the creative direction (modern, minimalist, vibrant, earthy, etc.)
7. **Location**: Geographic target (country code like "US", "IN", "UK", or "GLOBAL")
8. **Competitors**: Who are the main competitors? (list 2-3 if identifiable)
9. **Key Features**: What are the product's main selling points? (list 3-5)
10. **Pain Points**: What customer problems does this solve? (list 2-4)
11. **Budget**: Estimated budget if mentioned (e.g., "$10k-50k", "Medium", or "Not specified")
12. **Timeline**: Campaign duration if mentioned (e.g., "3 months", "Q1 2026", or "Not specified")

IMPORTANT RULES:
- If information is explicitly stated, use it exactly
- If information is IMPLIED or can be INFERRED from context, make intelligent educated guesses
- Be SPECIFIC, not generic (e.g., "college students aged 18-24 interested in sustainability" not just "young people")
- For competitors, only include if you can reasonably identify them from context
- Return ONLY valid JSON, no markdown, no explanations, no extra text

RETURN THIS EXACT JSON STRUCTURE:
{
  "product": "string",
  "audience": "string",
  "goal": "string",
  "tone": "string",
  "platforms": ["string"],
  "stylistics": "string",
  "location": "string",
  "competitors": ["string"],
  "keyFeatures": ["string"],
  "painPoints": ["string"],
  "budget": "string",
  "timeline": "string"
}`;

    console.log('🤖 Sending to Gemini AI for analysis...');
    const startTime = Date.now();
    
    const result = await model.generateContent(systemPrompt);
    const response = await result.response;
    const text = response.text();
    
    const analysisTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`⚡ Gemini analysis completed in ${analysisTime}s`);
    
    // Extract JSON from response (handle markdown code blocks)
    let jsonText = text.trim();
    if (jsonText.includes('```json')) {
      jsonText = jsonText.split('```json')[1].split('```')[0].trim();
    } else if (jsonText.includes('```')) {
      jsonText = jsonText.split('```')[1].split('```')[0].trim();
    }
    
    // Find JSON object
    const jsonMatch = jsonText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("No JSON found in Gemini response");
    }
    
    const strategy = JSON.parse(jsonMatch[0]);
    console.log('✅ Successfully parsed strategy from Gemini');
    
    // Validate and normalize response
    return {
      product: strategy.product || "Unknown Product",
      audience: strategy.audience || "General audience",
      goal: strategy.goal || "increase brand awareness and engagement",
      tone: strategy.tone || "engaging and professional",
      platforms: Array.isArray(strategy.platforms) && strategy.platforms.length > 0 
        ? strategy.platforms 
        : ["Instagram", "YouTube", "TikTok"],
      stylistics: strategy.stylistics || "modern and creative",
      location: strategy.location || "GLOBAL",
      competitors: Array.isArray(strategy.competitors) ? strategy.competitors : [],
      keyFeatures: Array.isArray(strategy.keyFeatures) ? strategy.keyFeatures : [],
      painPoints: Array.isArray(strategy.painPoints) ? strategy.painPoints : [],
      budget: strategy.budget || "Not specified",
      timeline: strategy.timeline || "Not specified",
      _meta: {
        source: isPDF ? 'pdf' : 'text',
        extractedLength: fullPromptText.length,
        analysisTime: parseFloat(analysisTime)
      }
    };
    
  } catch (error) {
    console.error('❌ Gemini analysis failed:', error.message);
    console.log('🔄 Falling back to keyword-based parsing...');
    // Fallback to basic parsing if Gemini fails
    return parsePromptToStrategy(promptText);
  }
}

/**
 * Fallback: Parse prompt text into strategy JSON (basic keyword detection)
 */
function parsePromptToStrategy(promptText) {
  const promptLower = promptText.toLowerCase();
  
  // Extract product name (assume first part before any descriptive text)
  const productMatch = promptText.match(/^([^-–—]+)/);
  const product = productMatch ? productMatch[1].trim() : promptText.slice(0, 50);
  
  // Detect audience keywords
  let audience = "target audience";
  if (promptLower.includes('student') || promptLower.includes('college')) {
    audience = "college students and young adults";
  } else if (promptLower.includes('professional') || promptLower.includes('business')) {
    audience = "working professionals";
  } else if (promptLower.includes('parent') || promptLower.includes('family')) {
    audience = "parents and families";
  } else if (promptLower.includes('fitness') || promptLower.includes('gym') || promptLower.includes('athlete')) {
    audience = "fitness enthusiasts and athletes";
  }
  
  // Detect tone from keywords
  let tone = "engaging and professional";
  if (promptLower.includes('fun') || promptLower.includes('playful')) {
    tone = "fun, energetic, and playful";
  } else if (promptLower.includes('luxury') || promptLower.includes('premium')) {
    tone = "sophisticated, elegant, and aspirational";
  } else if (promptLower.includes('eco') || promptLower.includes('sustainable') || promptLower.includes('green')) {
    tone = "inspiring, educational, and eco-conscious";
  } else if (promptLower.includes('tech') || promptLower.includes('innovation')) {
    tone = "innovative, forward-thinking, and tech-savvy";
  }
  
  // Detect goal
  let goal = "increase brand awareness and drive sales";
  if (promptLower.includes('awareness')) {
    goal = "build brand awareness and visibility";
  } else if (promptLower.includes('sales') || promptLower.includes('revenue')) {
    goal = "drive online sales and conversions";
  } else if (promptLower.includes('engagement')) {
    goal = "increase social media engagement";
  } else if (promptLower.includes('launch')) {
    goal = "successful product launch and market entry";
  }

  return {
    product: product,
    audience: audience,
    goal: goal,
    tone: tone,
    platforms: ["Instagram", "YouTube", "TikTok"],
    stylistics: (promptLower.includes('eco') || promptLower.includes('sustainable')) 
      ? "eco-friendly and natural" 
      : "modern and creative",
    location: "IN",
    competitors: [],
    keyFeatures: [],
    painPoints: [],
    budget: "Not specified",
    timeline: "Not specified"
  };
}

exports.createCampaign = async (req, res) => {
  try {
    let promptText = "";
    let inputType = "text";
    let fileBuffer = null;

    /**
     * TEXT INPUT
     */
    if (req.body.text) {
      promptText = req.body.text;
      inputType = "text";
    }

    /**
     * PDF INPUT
     */
    if (req.file) {
      const localPath = req.file.path;
      
      console.log(`📂 Processing uploaded PDF: ${req.file.originalname}`);
      
      // Read file buffer for Gemini analysis (CRITICAL for text extraction)
      fileBuffer = fs.readFileSync(localPath);
      console.log(`📦 File buffer size: ${fileBuffer.length} bytes`);
      
      const fileName = `campaign_pdfs/${Date.now()}_${req.file.originalname}`;

      // Upload to Firebase Storage
      await bucket.upload(localPath, {
        destination: fileName,
        metadata: { contentType: req.file.mimetype }
      });

      const pdfUrl = `https://storage.googleapis.com/${bucket.name}/${fileName}`;
      console.log(`☁️ Uploaded to Firebase: ${fileName}`);
      
      // Clean up local file
      fs.unlinkSync(localPath);

      // Use filename as fallback (will be replaced by extracted text)
      promptText = req.file.originalname.replace('.pdf', '').replace(/_/g, ' ');
      inputType = "pdf";
    }

    if (!promptText && !fileBuffer) {
      return res.status(400).json({
        success: false,
        message: "Either text or PDF is required"
      });
    }

    console.log('\n🚀 ===== CAMPAIGN ANALYSIS STARTED =====');
    console.log(`📝 Input Type: ${inputType}`);
    console.log(`📄 Initial Prompt: ${promptText.substring(0, 100)}${promptText.length > 100 ? '...' : ''}`);
    
    const totalStartTime = Date.now();
    
    // Use Gemini to analyze and generate detailed strategy
    const strategy = await analyzeWithGemini(promptText, fileBuffer);
    
    const totalTime = ((Date.now() - totalStartTime) / 1000).toFixed(2);
    console.log(`✅ ===== ANALYSIS COMPLETE in ${totalTime}s =====\n`);

    // Return detailed strategy JSON with performance metrics
    res.status(200).json({
      success: true,
      input: {
        type: inputType,
        originalPrompt: promptText,
        extractedLength: strategy._meta?.extractedLength
      },
      strategy: {
        product: strategy.product,
        audience: strategy.audience,
        goal: strategy.goal,
        tone: strategy.tone,
        platforms: strategy.platforms,
        stylistics: strategy.stylistics,
        location: strategy.location,
        competitors: strategy.competitors,
        keyFeatures: strategy.keyFeatures,
        painPoints: strategy.painPoints,
        budget: strategy.budget,
        timeline: strategy.timeline
      },
      analyzed_by: "gemini-2.5-flash",
      performance: {
        total_time_seconds: parseFloat(totalTime),
        ai_analysis_time: strategy._meta?.analysisTime,
        source: strategy._meta?.source
      }
    });

  } catch (err) {
    console.error('Campaign creation error:', err);
    res.status(500).json({
      success: false,
      message: "Failed to parse prompt",
      error: err.message
    });
  }
};

/**
 * Add / Update agent output
 */
exports.addAgentResult = async (req, res) => {
  try {
    const { campaignId } = req.params;
    const { agentName, result } = req.body;

    if (!agentName || !result) {
      return res.status(400).json({ message: "Agent name and result required" });
    }

    const campaign = await Campaign.findById(campaignId);
    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }
    campaign.agents.push({ agentName, result });
    await campaign.save();

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to add agent result" });
  }
};

/**
 * Mark campaign status
 */
exports.updateCampaignStatus = async (req, res) => {
  try {
    const { campaignId } = req.params;
    const { status } = req.body;

    const campaign = await Campaign.findByIdAndUpdate(
      campaignId,
      { status },
      { new: true }
    );

    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to update status" });
  }
};

/**
 * Get all campaigns of logged-in user
 */
exports.getMyCampaigns = async (req, res) => {
  try {
    const campaigns = await Campaign.find({ email: req.user._id })
      .sort({ createdAt: -1 });

    res.json({ success: true, campaigns });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to fetch campaigns" });
  }
};

/**
 * Get single campaign
 */
exports.getCampaignById = async (req, res) => {
  try {
    const campaign = await Campaign.findOne({
      _id: req.params.id,
      email: req.user._id
    });

    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to fetch campaign" });
  }
};
